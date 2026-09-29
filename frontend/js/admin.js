const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname.startsWith("192.168") || window.location.protocol === "file:";
const API_BASE = isLocal
    ? "http://localhost:8000"
    : "https://eno-portal-backend-production.up.railway.app";
let allRegistros = [];
let currentModalId = null;

// ── Formateador oficial de Código de Registro (ENO-A001 a ENO-Z100) ──
function formatRegistroCode(id) {
    if (!id) return "ENO-A001";
    if (typeof id === "string" && id.startsWith("ENO-")) return id;
    const numId = parseInt(id.toString().replace(/\D/g, ""), 10);
    if (isNaN(numId) || numId <= 0) return "ENO-A001";
    const letterIndex = Math.min(Math.floor((numId - 1) / 100), 25);
    const letter = String.fromCharCode(65 + letterIndex);
    const num = ((numId - 1) % 100) + 1;
    return `ENO-${letter}${String(num).padStart(3, "0")}`;
}

// 🔒 Helper: obtener headers con autenticación admin
function getAdminHeaders(extra = {}) {
    const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");
    const token = session?.token || "";
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        ...extra,
    };
}

// Check admin session — si no hay sesión admin, mostrar formulario de login
const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");
const adminBadge = document.getElementById("admin-header-badge");
const adminLogout = document.getElementById("admin-header-logout");

if (!session || session.role !== "admin") {
    // Mostrar login form, ocultar dashboard
    document.getElementById("admin-login-screen").classList.remove("hidden");
    document.getElementById("admin-dashboard-content").classList.add("hidden");
    if (adminBadge) adminBadge.style.display = "none";
    if (adminLogout) adminLogout.style.display = "none";
} else {
    document.getElementById("admin-login-screen").classList.add("hidden");
    document.getElementById("admin-dashboard-content").classList.remove("hidden");
    if (adminBadge) adminBadge.style.display = "inline-flex";
    if (adminLogout) adminLogout.style.display = "inline-flex";
    loadData();
}

// Toast
function showToast(type, msg) {
    const t = document.getElementById("toast");
    t.className = `toast toast-${type} show`;
    t.textContent = msg;
    setTimeout(() => t.classList.remove("show"), 3000);
}

// Estado badge helper
function estadoBadge(estado) {
    const map = {
        "pendiente": { bg: "bg-amber-100 text-amber-800", icon: "schedule", label: "Pendiente" },
        "en revisión": { bg: "bg-blue-100 text-blue-800", icon: "hourglass_top", label: "En Revisión" },
        "verificado": { bg: "bg-emerald-100 text-emerald-800", icon: "verified", label: "Verificado" },
        "rechazado": { bg: "bg-red-100 text-red-800", icon: "cancel", label: "Rechazado" },
    };
    const s = map[estado] || map["pendiente"];
    return `<span class="inline-flex items-center gap-1 ${s.bg} text-xs font-bold px-2 py-1 rounded-full">
                <span class="material-symbols-outlined text-xs">${s.icon}</span>${s.label}
            </span>`;
}

// Load registrations
async function loadRegistrations() {
    try {
        const res = await fetch(`${API_BASE}/api/registros?limit=200`, {
            headers: getAdminHeaders(),
        });
        if (res.status === 401) {
            showToast("error", "Sesión expirada. Inicia sesión de nuevo.");
            logout();
            return;
        }
        allRegistros = await res.json();
        populateMunicipioFilter();
        renderComprobantes();
        applyFilters();
        updateStats();
    } catch (e) {
        console.error("Error loading registrations:", e);
        document.getElementById("table-body").innerHTML = `
                    <tr><td colspan="11" class="px-6 py-12 text-center text-red-400">
                        <span class="material-symbols-outlined mb-2" style="font-size: 40px;">error</span>
                        <p>Error al cargar los registros.</p>
                    </td></tr>`;
    }
}

// Update stats
function updateStats() {
    const total = allRegistros.length;
    const verificados = allRegistros.filter(r => r.estado_pago === "verificado").length;
    const enRevision = allRegistros.filter(r => r.estado_pago === "en revisión").length;
    const pendientes = allRegistros.filter(r => r.estado_pago === "pendiente").length;

    document.getElementById("stat-total").textContent = total;
    document.getElementById("stat-verificados").textContent = verificados;
    document.getElementById("stat-revision").textContent = enRevision;
    document.getElementById("stat-pendientes").textContent = pendientes;
    document.getElementById("stat-ingresos").textContent = `RD$${(verificados * 600).toLocaleString()}`;
}

// Populate municipio filter
function populateMunicipioFilter() {
    const session = JSON.parse(sessionStorage.getItem("eno_session") || "{}");
    const container = document.getElementById("dropdown-municipios-container");
    if (!container) return;

    if (session.municipio && session.municipio !== "ALL") {
        container.style.display = "none";
        return;
    }

    const defaultMunicipios = [
        "Las Guáranas", "San Francisco", "Cotuí", "Nagua", "La Vega", 
        "Bonao", "Maimón", "Fantino", "Villa Tapia", "Salcedo", 
        "Santo Domingo Este", "Distrito Nacional"
    ];
    
    // Incluir también cualquier municipio extra que esté en la DB pero no en la lista
    const extraMunicipios = [...new Set(allRegistros.map(r => r.municipio))]
        .filter(m => m && !defaultMunicipios.includes(m))
        .sort();

    const allMunicipios = [...defaultMunicipios, ...extraMunicipios];
    
    let html = '<div class="odoo-dropdown-header">Por Municipio</div>';
    allMunicipios.forEach(m => {
        html += `<div class="odoo-dropdown-item" onclick="syncOdooFilter('municipio', '${m.replace(/'/g, "\\'")}')">${m}</div>`;
    });
    container.innerHTML = html;
}

// Render comprobantes pending review
function renderComprobantes() {
    const pendientes = allRegistros.filter(r => r.comprobante_pago && r.estado_pago === "en revisión");
    const section = document.getElementById("comprobantes-section");
    const list = document.getElementById("comprobantes-list");
    const count = document.getElementById("comprobantes-count");

    if (pendientes.length === 0) {
        section.classList.add("hidden");
        return;
    }

    section.classList.remove("hidden");
    count.textContent = pendientes.length;

    list.innerHTML = pendientes.map(r => `
                <div class="flex items-center justify-between p-5 hover:bg-slate-50 transition-colors">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                            <span class="material-symbols-outlined text-blue-600">receipt_long</span>
                        </div>
                        <div>
                            <p class="font-bold text-slate-800 max-w-[150px] truncate" title="${r.nombre_completo}">${r.nombre_completo}</p>
                            <p class="text-slate-400 text-xs font-mono">${r.telefono} · ${formatRegistroCode(r.id)}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        ${estadoBadge(r.estado_pago)}
                        <button onclick="openModal(${r.id}, '${r.nombre_completo.replace(/'/g, "\\'")}', '${r.telefono}', '${r.comprobante_pago}')"
                            class="flex items-center gap-1 bg-primary text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-primary/90 transition-all">
                            <span class="material-symbols-outlined text-sm">visibility</span>
                            Revisar
                        </button>
                    </div>
                </div>
            `).join("");
}

// Apply filters to table
// Toggle Odoo style dropdown
function toggleOdooDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById("odoo-filter-dropdown");
    dropdown.classList.toggle("show");
}

// Close Odoo style dropdown when clicking outside
document.addEventListener("click", function(event) {
    const dropdown = document.getElementById("odoo-filter-dropdown");
    if (dropdown && dropdown.classList.contains("show")) {
        dropdown.classList.remove("show");
    }
});

// Sync Odoo style filter with the actual header select
function syncOdooFilter(type, value) {
    const selectEl = document.getElementById(`filter-${type}`);
    let finalValue = value;
    
    if (selectEl) {
        if (selectEl.value === value && value !== "") {
            finalValue = ""; // Toggle off
        }
        selectEl.value = finalValue;
        applyFilters();
    }
    
    // Update active visual state in dropdown
    const dropdown = document.getElementById("odoo-filter-dropdown");
    const items = dropdown.querySelectorAll(".odoo-dropdown-item");
    items.forEach(item => {
        const onClickAttr = item.getAttribute("onclick") || "";
        if (value === "") {
            if (onClickAttr.includes(`'${type}', ''`)) {
                item.classList.add("active");
            } else if (onClickAttr.includes(`'${type}'`)) {
                item.classList.remove("active");
            }
        } else {
            if (onClickAttr.includes(`'${type}',`)) {
                if (onClickAttr.includes(`'${type}', '${finalValue}'`) && finalValue !== "") {
                    item.classList.add("active");
                } else {
                    item.classList.remove("active");
                }
            }
        }
    });
}

function applyFilters() {
    const search = document.getElementById("filter-search").value.toLowerCase();
    const pagoFilter = document.getElementById("filter-pago").value;
    const tallaFilter = document.getElementById("filter-talla").value;
    const municipioFilter = document.getElementById("filter-municipio").value;
    const comidaFilter = document.getElementById("filter-comida").value;

    const filtered = allRegistros.filter(r => {
        const matchSearch = !search ||
            r.nombre_completo.toLowerCase().includes(search) ||
            r.telefono.includes(search) ||
            r.email.toLowerCase().includes(search);
    const matchPago = !pagoFilter || r.estado_pago === pagoFilter;
        const matchTalla = !tallaFilter || r.talla_camiseta === tallaFilter;
        const matchMunicipio = !municipioFilter || r.municipio === municipioFilter;
        const matchComida = !comidaFilter || r.opcion_comida === comidaFilter || r.opcionComida === comidaFilter;
        return matchSearch && matchPago && matchTalla && matchMunicipio && matchComida;
    });

    // Default to id ascending
    filtered.sort((a, b) => a.id - b.id);

    const tbody = document.getElementById("table-body");

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-slate-400">
                    <span class="material-symbols-outlined mb-2" style="font-size: 40px;">search_off</span>
                    <p>No se encontraron registros con estos filtros.</p>
                </td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(r => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td data-label="ID" class="px-5 py-3.5 font-bold text-primary text-xs">${formatRegistroCode(r.id)}</td>
                    <td data-label="Nombre" class="px-5 py-3.5 font-semibold text-slate-800 max-w-[150px] truncate" title="${r.nombre_completo}">${r.nombre_completo}</td>
                    <td data-label="Edad" class="px-5 py-3.5 text-slate-600 text-xs font-mono">${r.edad || "—"}</td>
                    <td data-label="Teléfono" class="px-5 py-3.5 text-slate-600 font-mono text-xs">${r.telefono}</td>
                    <td data-label="Email" class="px-5 py-3.5 text-slate-600 text-xs">${r.email}</td>
                    <td data-label="Municipio" class="px-5 py-3.5 text-slate-600 text-xs">${r.municipio}</td>
                    <td data-label="Talla" class="px-5 py-3.5">
                        <span class="bg-primary/10 text-primary text-xs font-bold px-2 py-1 rounded">${r.talla_camiseta.toUpperCase()}</span>
                    </td>
                    <td data-label="Comida" class="px-5 py-3.5 text-slate-600 text-xs">${r.opcion_comida || r.opcionComida || "—"}</td>
                    <td data-label="Estado Pago" class="px-5 py-3.5">${estadoBadge(r.estado_pago)}</td>
                    <td data-label="Comprobante" class="px-5 py-3.5">
                        ${r.comprobante_pago
            ? `<button onclick="openModal(${r.id}, '${r.nombre_completo.replace(/'/g, "\\'")}', '${r.telefono}', '${r.comprobante_pago}')"
                                class="text-primary hover:bg-primary/5 p-1.5 rounded-lg transition-colors flex items-center gap-1 text-xs font-bold">
                                <span class="material-symbols-outlined text-sm">image</span>Ver
                            </button>`
            : `<span class="text-slate-300 text-xs">Sin enviar</span>`
        }
                    </td>
                    <td data-label="Acciones" class="px-5 py-3.5 text-center">
                        <div class="flex items-center justify-center gap-1">
                            ${r.comprobante_pago ? `
                                <button onclick="promptQuickSetEstado(${r.id}, 'verificado', '${r.nombre_completo.replace(/'/g, "\\'")}')" title="Aprobar pago"
                                    class="text-emerald-500 hover:bg-emerald-50 p-1.5 rounded-lg transition-colors">
                                    <span class="material-symbols-outlined text-sm">check_circle</span>
                                </button>
                                <button onclick="promptQuickSetEstado(${r.id}, 'rechazado', '${r.nombre_completo.replace(/'/g, "\\'")}')" title="Rechazar pago"
                                    class="text-red-500 hover:bg-red-50 p-1.5 rounded-lg transition-colors">
                                    <span class="material-symbols-outlined text-sm">cancel</span>
                                </button>
                            ` : ''}
                            <button onclick="promptDeleteRegistro(${r.id}, '${r.nombre_completo.replace(/'/g, "\\'")}')" title="Eliminar registro"
                                class="text-slate-400 hover:bg-red-50 hover:text-red-500 p-1.5 rounded-lg transition-colors">
                                <span class="material-symbols-outlined text-sm">delete</span>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join("");
}

// Modal functions
function openModal(id, name, phone, imgPath) {
    currentModalId = id;
    document.getElementById("modal-user-name").textContent = name;
    document.getElementById("modal-user-phone").textContent = `${phone} · ${formatRegistroCode(id)}`;
    const fullImgUrl = `${API_BASE}${imgPath}`;
    document.getElementById("modal-img").src = fullImgUrl;
    const linkEl = document.getElementById("modal-img-link");
    if (linkEl) linkEl.href = fullImgUrl;
    document.getElementById("modal-comprobante").classList.add("active");
}

function closeModal() {
    document.getElementById("modal-comprobante").classList.remove("active");
    currentModalId = null;
}

// ── Modal de Confirmación para Acciones Rápidas ──
let confirmActionCallback = null;

function requestConfirmAction({ title, message, targetName, targetCode, warning, actionType, btnText, onConfirm }) {
    const modal = document.getElementById("modal-confirm");
    if (!modal) {
        if (confirm(`${title}\n${targetName} (${targetCode})\n¿Deseas continuar?`)) {
            onConfirm();
        }
        return;
    }

    const iconWrap = document.getElementById("confirm-icon-wrap");
    const icon = document.getElementById("confirm-icon");
    const titleEl = document.getElementById("confirm-title");
    const msgEl = document.getElementById("confirm-message");
    const targetNameEl = document.getElementById("confirm-target-name");
    const targetMetaEl = document.getElementById("confirm-target-meta");
    const warningEl = document.getElementById("confirm-warning");
    const btn = document.getElementById("confirm-action-btn");

    if (titleEl) titleEl.textContent = title;
    if (msgEl) msgEl.textContent = message || "Por favor confirma antes de continuar.";
    if (targetNameEl) targetNameEl.textContent = targetName;
    if (targetMetaEl) targetMetaEl.textContent = targetCode;

    if (warningEl) {
        if (warning) {
            warningEl.textContent = warning;
            warningEl.style.display = "block";
        } else {
            warningEl.style.display = "none";
        }
    }

    if (btn) btn.textContent = btnText || "Confirmar";

    if (iconWrap && icon && btn) {
        if (actionType === "approve") {
            iconWrap.style.background = "#ecfdf5";
            iconWrap.style.borderColor = "#a7f3d0";
            icon.style.color = "#059669";
            icon.textContent = "check_circle";
            btn.style.background = "#059669";
        } else if (actionType === "reject") {
            iconWrap.style.background = "#fef2f2";
            iconWrap.style.borderColor = "#fecaca";
            icon.style.color = "#dc2626";
            icon.textContent = "cancel";
            btn.style.background = "#dc2626";
        } else {
            iconWrap.style.background = "#fff1f2";
            iconWrap.style.borderColor = "#fecdd3";
            icon.style.color = "#e11d48";
            icon.textContent = "delete_forever";
            btn.style.background = "#b91c1c";
        }
    }

    confirmActionCallback = onConfirm;
    modal.classList.add("active");
}

function closeConfirmModal() {
    const modal = document.getElementById("modal-confirm");
    if (modal) modal.classList.remove("active");
    confirmActionCallback = null;
}

// Inicializar listener de confirmación
(function initConfirmModalListener() {
    const btn = document.getElementById("confirm-action-btn");
    if (btn) {
        btn.onclick = () => {
            if (typeof confirmActionCallback === "function") {
                const cb = confirmActionCallback;
                closeConfirmModal();
                cb();
            }
        };
    }
})();

// Cerrar modales con tecla Escape
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        const confirmModal = document.getElementById("modal-confirm");
        if (confirmModal && confirmModal.classList.contains("active")) {
            closeConfirmModal();
            return;
        }
        if (currentModalId) {
            closeModal();
        }
    }
});

// Prompts para acciones rápidas desde la tabla
function promptQuickSetEstado(id, estado, nombre) {
    const code = formatRegistroCode(id);
    const isApprove = estado === "verificado";
    requestConfirmAction({
        title: isApprove
            ? "¿Realmente quieres aprobar el pago?"
            : "¿Realmente quieres rechazar el pago?",
        message: isApprove
            ? `Vas a aprobar el pago de este asistente.`
            : `Vas a rechazar el comprobante de este asistente.`,
        targetName: nombre,
        targetCode: code,
        warning: isApprove
            ? "El asistente quedará registrado con estado verificado en el sistema."
            : "El asistente figurará con pago rechazado y deberá subir un nuevo comprobante.",
        actionType: isApprove ? "approve" : "reject",
        btnText: isApprove ? "Sí, aprobar pago" : "Sí, rechazar pago",
        onConfirm: () => quickSetEstado(id, estado)
    });
}

function promptDeleteRegistro(id, nombre) {
    const code = formatRegistroCode(id);
    requestConfirmAction({
        title: "¿Realmente quieres eliminar este registro?",
        message: "Esta acción borrará permanentemente los datos del asistente.",
        targetName: nombre,
        targetCode: code,
        warning: "⚠️ Esta acción es irreversible. Se eliminarán los datos personales y el comprobante asociado a este registro.",
        actionType: "delete",
        btnText: "Sí, eliminar registro",
        onConfirm: () => executeDeleteRegistro(id, code)
    });
}

// Set payment status (desde modal de imagen)
async function setEstado(estado) {
    if (!currentModalId) return;
    await quickSetEstado(currentModalId, estado);
    closeModal();
}

async function quickSetEstado(id, estado) {
    try {
        const res = await fetch(`${API_BASE}/api/registros/${id}/estado-pago`, {
            method: "PATCH",
            headers: getAdminHeaders(),
            body: JSON.stringify({ estado_pago: estado }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        showToast("success", data.message);
        loadData();
    } catch (e) {
        showToast("error", e.message);
    }
}

// Delete registration
async function deleteRegistro(id) {
    const reg = allRegistros.find(r => r.id === id);
    const name = reg ? reg.nombre_completo : "Asistente";
    promptDeleteRegistro(id, name);
}

async function executeDeleteRegistro(id, code) {
    try {
        const res = await fetch(`${API_BASE}/api/registros/${id}`, {
            method: "DELETE",
            headers: getAdminHeaders(),
        });
        if (res.ok) {
            showToast("success", `Registro ${code} eliminado.`);
            loadData();
        } else {
            showToast("error", "Error al eliminar el registro.");
        }
    } catch (e) {
        showToast("error", "Error de conexión.");
    }
}

// Load all data
function loadData() {
    loadRegistrations();
}

function logout() {
    sessionStorage.removeItem("eno_session");
    window.location.href = "index.html";
}

// Init — solo si hay sesión (si no, el login form ya se muestra arriba)
// loadData() se llama dentro del bloque session check

// ── Admin Login form ──────────────────────────────────────────
const API_BASE_ADMIN = isLocal
    ? "http://localhost:8000"
    : "https://eno-portal-backend-production.up.railway.app";

async function adminLogin() {
    const username = document.getElementById("admin-username").value.trim();
    const password = document.getElementById("admin-password").value.trim();
    const errorEl = document.getElementById("admin-login-error");
    const btn = document.getElementById("admin-login-btn");

    if (!username || !password) {
        errorEl.textContent = "Por favor completa todos los campos.";
        errorEl.classList.remove("hidden");
        return;
    }

    btn.disabled = true;
    btn.textContent = "Verificando...";
    errorEl.classList.add("hidden");

    try {
        const res = await fetch(`${API_BASE_ADMIN}/api/auth/admin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Credenciales incorrectas.");

        // 🔒 Guardar token admin en sesión para peticiones autenticadas
        sessionStorage.setItem("eno_session", JSON.stringify({
            role: "admin",
            token: data.token,
            data: data.data,
            municipio: data.data.municipio // Guarda el municipio del admin
        }));

        // Mostrar dashboard, ocultar login
        document.getElementById("admin-login-screen").classList.add("hidden");
        document.getElementById("admin-dashboard-content").classList.remove("hidden");
        if (adminBadge) adminBadge.style.display = "inline-flex";
        if (adminLogout) adminLogout.style.display = "inline-flex";
        loadData();
    } catch (err) {
        if (err.name === "TypeError" || (err.message && err.message.toLowerCase().includes("failed to fetch"))) {
            errorEl.textContent = "El servidor está despertando de inactividad o hay un problema de conexión. Por favor reintenta en unos segundos.";
        } else {
            errorEl.textContent = err.message;
        }
        errorEl.classList.remove("hidden");
        btn.disabled = false;
        btn.textContent = "Entrar";
    }
}

// ── Generic Table Sorter (Odoo Style) ──────────────────────────────────────────
document.addEventListener('click', function (e) {
    const th = e.target.closest('th');
    if (!th) return;
    
    const table = th.closest('.sortable-table');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody || tbody.rows.length <= 1) return; // Prevent sorting when loading or empty
    
    const thIndex = Array.from(th.parentNode.children).indexOf(th);
    
    // Ignore sort on "Acciones" column
    if (th.textContent.trim().toLowerCase() === 'acciones') return;

    // Get current sort direction
    const isAscending = th.classList.contains('sort-asc');
    
    // Reset all headers in this table
    table.querySelectorAll('th').forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
    });

    // Set new direction
    const direction = isAscending ? -1 : 1;
    th.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

    // Sort rows
    const rowsArray = Array.from(tbody.querySelectorAll('tr'));
    
    rowsArray.sort((rowA, rowB) => {
        const cellA = rowA.children[thIndex].textContent.trim();
        const cellB = rowB.children[thIndex].textContent.trim();
        
        const parseValue = (val) => {
            // Remove currency symbols, commas, spaces for numeric check
            const clean = val.replace(/[$,\s]/g, "");
            if (/^-?\d+(\.\d+)?$/.test(clean)) {
                return parseFloat(clean);
            }
            return val;
        };

        const valA = parseValue(cellA);
        const valB = parseValue(cellB);
        
        if (typeof valA === 'number' && typeof valB === 'number') {
            return (valA - valB) * direction;
        }
        
        // Fallback to text compare
        return cellA.localeCompare(cellB, 'es', { numeric: true, sensitivity: 'base' }) * direction;
    });

    // Re-append sorted rows
    rowsArray.forEach(row => tbody.appendChild(row));
});