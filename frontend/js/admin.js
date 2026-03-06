const API_BASE = "http://localhost:8000";
        let allRegistros = [];
        let currentModalId = null;

        // Check admin session
        const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");
        if (!session || session.role !== "admin") {
            window.location.href = "login.html";
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
                const res = await fetch(`${API_BASE}/api/registros?limit=200`);
                allRegistros = await res.json();
                populateMunicipioFilter();
                renderComprobantes();
                applyFilters();
                updateStats();
            } catch (e) {
                console.error("Error loading registrations:", e);
                document.getElementById("table-body").innerHTML = `
                    <tr><td colspan="9" class="px-6 py-12 text-center text-red-400">
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
            document.getElementById("stat-ingresos").textContent = `RD$${(verificados * 700).toLocaleString()}`;
        }

        // Populate municipio filter
        function populateMunicipioFilter() {
            const municipios = [...new Set(allRegistros.map(r => r.municipio))].sort();
            const select = document.getElementById("filter-municipio");
            select.innerHTML = '<option value="">Todos los municipios</option>' +
                municipios.map(m => `<option value="${m}">${m}</option>`).join("");
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
                            <p class="font-bold text-slate-800">${r.nombre_completo}</p>
                            <p class="text-slate-400 text-xs font-mono">${r.telefono} · ENO-${r.id}</p>
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
        function applyFilters() {
            const search = document.getElementById("filter-search").value.toLowerCase();
            const pagoFilter = document.getElementById("filter-pago").value;
            const tallaFilter = document.getElementById("filter-talla").value;
            const municipioFilter = document.getElementById("filter-municipio").value;

            const filtered = allRegistros.filter(r => {
                const matchSearch = !search ||
                    r.nombre_completo.toLowerCase().includes(search) ||
                    r.telefono.includes(search) ||
                    r.email.toLowerCase().includes(search);
                const matchPago = !pagoFilter || r.estado_pago === pagoFilter;
                const matchTalla = !tallaFilter || r.talla_camiseta === tallaFilter;
                const matchMunicipio = !municipioFilter || r.municipio === municipioFilter;
                return matchSearch && matchPago && matchTalla && matchMunicipio;
            });

            document.getElementById("filter-count").textContent =
                `Mostrando ${filtered.length} de ${allRegistros.length} registros`;

            const tbody = document.getElementById("table-body");

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" class="px-6 py-12 text-center text-slate-400">
                    <span class="material-symbols-outlined mb-2" style="font-size: 40px;">search_off</span>
                    <p>No se encontraron registros con estos filtros.</p>
                </td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-5 py-3.5 font-bold text-primary text-xs">ENO-${r.id}</td>
                    <td class="px-5 py-3.5 font-semibold text-slate-800">${r.nombre_completo}</td>
                    <td class="px-5 py-3.5 text-slate-600 font-mono text-xs">${r.telefono}</td>
                    <td class="px-5 py-3.5 text-slate-600 text-xs">${r.email}</td>
                    <td class="px-5 py-3.5 text-slate-600 text-xs">${r.municipio}</td>
                    <td class="px-5 py-3.5">
                        <span class="bg-primary/10 text-primary text-xs font-bold px-2 py-1 rounded">${r.talla_camiseta.toUpperCase()}</span>
                    </td>
                    <td class="px-5 py-3.5">${estadoBadge(r.estado_pago)}</td>
                    <td class="px-5 py-3.5">
                        ${r.comprobante_pago
                    ? `<button onclick="openModal(${r.id}, '${r.nombre_completo.replace(/'/g, "\\'")}', '${r.telefono}', '${r.comprobante_pago}')"
                                class="text-primary hover:bg-primary/5 p-1.5 rounded-lg transition-colors flex items-center gap-1 text-xs font-bold">
                                <span class="material-symbols-outlined text-sm">image</span>Ver
                            </button>`
                    : `<span class="text-slate-300 text-xs">Sin enviar</span>`
                }
                    </td>
                    <td class="px-5 py-3.5 text-center">
                        <div class="flex items-center justify-center gap-1">
                            ${r.comprobante_pago ? `
                                <button onclick="quickSetEstado(${r.id}, 'verificado')" title="Aprobar pago"
                                    class="text-emerald-500 hover:bg-emerald-50 p-1.5 rounded-lg transition-colors">
                                    <span class="material-symbols-outlined text-sm">check_circle</span>
                                </button>
                                <button onclick="quickSetEstado(${r.id}, 'rechazado')" title="Rechazar pago"
                                    class="text-red-500 hover:bg-red-50 p-1.5 rounded-lg transition-colors">
                                    <span class="material-symbols-outlined text-sm">cancel</span>
                                </button>
                            ` : ''}
                            <button onclick="deleteRegistro(${r.id})" title="Eliminar registro"
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
            document.getElementById("modal-user-phone").textContent = `${phone} · ENO-${id}`;
            document.getElementById("modal-img").src = `${API_BASE}${imgPath}`;
            document.getElementById("modal-comprobante").classList.add("active");
        }

        function closeModal() {
            document.getElementById("modal-comprobante").classList.remove("active");
            currentModalId = null;
        }

        // Set payment status
        async function setEstado(estado) {
            if (!currentModalId) return;
            await quickSetEstado(currentModalId, estado);
            closeModal();
        }

        async function quickSetEstado(id, estado) {
            try {
                const res = await fetch(`${API_BASE}/api/registros/${id}/estado-pago`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
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
            if (!confirm(`¿Estás seguro de eliminar el registro ENO-${id}?`)) return;
            try {
                const res = await fetch(`${API_BASE}/api/registros/${id}`, { method: "DELETE" });
                if (res.ok) {
                    showToast("success", `Registro ENO-${id} eliminado.`);
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
            window.location.href = "login.html";
        }

        // Init
        loadData();