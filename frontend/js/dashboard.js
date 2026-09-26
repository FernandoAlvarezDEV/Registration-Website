const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname.startsWith("192.168") || window.location.protocol === "file:";
const API_BASE = isLocal
    ? "http://localhost:8000"
    : "https://eno-portal-backend-production.up.railway.app";

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

// ── Toast ──────────────────────────────────────────────────────────
function showToast(type, msg) {
    const t = document.getElementById("toast");
    if (!t) return;
    t.className = `toast toast-${type} show`;
    t.textContent = msg;
    setTimeout(() => t.classList.remove("show"), 4000);
}

// ── Mostrar estado de pago en UI ───────────────────────────────────
function renderPaymentStatus(estadoPago) {
    const badge = document.getElementById("pago-badge");
    if (!badge) return;
    const statusMap = {
        "pendiente":   { bg: "background-color: rgba(245, 158, 11, 0.9); color: white;",  icon: "schedule",      text: "Pago Pendiente" },
        "en revisión": { bg: "background-color: rgba(59, 130, 246, 0.9); color: white;",   icon: "hourglass_top", text: "En Revisión" },
        "verificado":  { bg: "background-color: rgba(16, 185, 129, 0.9); color: white;",  icon: "verified",      text: "Pago Verificado" },
        "rechazado":   { bg: "background-color: rgba(239, 68, 68, 0.9); color: white;",    icon: "cancel",        text: "Pago Rechazado" },
    };
    const status = statusMap[estadoPago] || statusMap["pendiente"];
    badge.style.cssText = status.bg;
    badge.innerHTML = `<span class="material-symbols-outlined" style="font-size:1.1rem;">${status.icon}</span> ${status.text}`;
}

// ── Rellenar UI con los datos del usuario ──────────────────────────
function populateUI(d) {
    const registroId = d.id ? parseInt(d.id.toString().replace(/\D/g, ""), 10) : d.id;
    const codigoOficial = d.codigoRegistro || d.idLabel || formatRegistroCode(registroId);

    // Guardar en sessionStorage para uso posterior (subir comprobante, etc.)
    sessionStorage.setItem("eno_session", JSON.stringify({
        role: "user",
        data: { ...d, idLabel: codigoOficial, codigoRegistro: codigoOficial }
    }));
    sessionStorage.setItem("eno_registro_id", registroId);

    // Rellenar campos HTML
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("header-name", d.nombreCompleto);
    set("user-name", d.nombreCompleto);
    set("reg-code", codigoOficial);
    set("detail-nombre", d.nombreCompleto);
    set("detail-edad", d.edad ? `${d.edad} años` : "—");
    set("detail-telefono", d.telefono || "—");
    set("detail-email", d.email || "—");
    set("detail-municipio", d.municipio || "—");
    set("detail-talla", (d.tallaCamiseta || "—").toUpperCase());
    set("detail-comida", d.opcion_comida || d.opcionComida || "—");
    set("detail-fecha", d.fechaRegistro
        ? new Date(d.fechaRegistro).toLocaleDateString("es-DO", { year: "numeric", month: "long", day: "numeric" })
        : "—");

    // Concepto de transferencia oficial en panel
    const transferMemoEl = document.getElementById("dashboard-transfer-memo");
    if (transferMemoEl) {
        transferMemoEl.textContent = `${codigoOficial} - ${d.nombreCompleto || "Tu Nombre"} - ${d.municipio || "Tu Distrito"}`;
    }

    renderPaymentStatus(d.estadoPago || "pendiente");

    // Comprobante ya subido
    if (d.comprobantePago) {
        const uploaded = document.getElementById("comprobante-uploaded");
        const uploadZone = document.getElementById("upload-zone-container");
        const preview = document.getElementById("comprobante-preview-existing");
        if (uploaded) uploaded.style.display = "block";
        if (uploadZone) uploadZone.style.display = "none";
        if (preview) preview.src = d.comprobantePago.startsWith("http")
            ? d.comprobantePago
            : `${API_BASE}${d.comprobantePago}`;
    } else {
        const uploaded = document.getElementById("comprobante-uploaded");
        const uploadZone = document.getElementById("upload-zone-container");
        if (uploaded) uploaded.style.display = "none";
        if (uploadZone) uploadZone.style.display = "block";
    }

    // Mostrar panel, ocultar login y loader
    const loader = document.getElementById("loading-screen");
    const loginScreen = document.getElementById("user-login-screen");
    const main = document.getElementById("dashboard-main");
    if (loader) loader.style.display = "none";
    if (loginScreen) loginScreen.style.display = "none";
    if (main) main.style.display = "block";
}

// ── Iniciar sesión en el portal de participantes ───────────────────
async function loginUsuarioNormal() {
    const errorBox = document.getElementById("user-login-error");
    const btn = document.getElementById("btn-login-user");

    const nombre = (document.getElementById("login-nombre")?.value || "").trim();
    const telefono = (document.getElementById("login-telefono")?.value || "").trim();
    const distrito = (document.getElementById("login-distrito")?.value || "").trim();
    const email = (document.getElementById("login-email")?.value || "").trim();

    if (errorBox) {
        errorBox.textContent = "";
        errorBox.classList.add("hidden");
    }

    if (!nombre || !telefono || !distrito || !email) {
        if (errorBox) {
            errorBox.textContent = "Por favor completa todos los campos (Nombre, Teléfono, Distrito y Correo).";
            errorBox.classList.remove("hidden");
        }
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="material-symbols-outlined" style="animation: spin 0.8s linear infinite;">progress_activity</span> Buscando registro...`;
    }

    try {
        const res = await fetch(`${API_BASE}/api/registros/verificar`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, telefono, distrito, email }),
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "No encontramos un registro que coincida exactamente con estos datos.");
        }

        populateUI(data.data);
    } catch (err) {
        if (errorBox) {
            errorBox.textContent = err.message;
            errorBox.classList.remove("hidden");
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<span class="material-symbols-outlined">badge</span> Consultar Mi Inscripción`;
        }
    }
}

// ── Lógica principal de carga ─────────────────────────────────────
function initDashboard() {
    // 1. Revisar si ya hay una sesión activa de participante
    const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");
    if (session && session.data && session.role === "user") {
        populateUI(session.data);
        return;
    }

    // 2. Si no hay sesión activa, preparar pantalla de consulta
    const loginScreen = document.getElementById("user-login-screen");
    const main = document.getElementById("dashboard-main");
    const loader = document.getElementById("loading-screen");

    if (loader) loader.style.display = "none";
    if (main) main.style.display = "none";
    if (loginScreen) loginScreen.style.display = "flex";

    // 3. Pre-llenar campos si el usuario viene de registrarse en la misma pestaña
    const lastReg = JSON.parse(sessionStorage.getItem("eno_registration") || "null");
    if (lastReg) {
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el && val) el.value = val;
        };
        setVal("login-nombre", lastReg.nombreCompleto);
        setVal("login-telefono", lastReg.telefono);
        setVal("login-distrito", lastReg.municipio);
        setVal("login-email", lastReg.email);
    }
}

// ── Upload de comprobante ──────────────────────────────────────────
let selectedFile = null;
const fileInput = document.getElementById("file-input");
const uploadZone = document.getElementById("upload-zone");

if (uploadZone) {
    uploadZone.addEventListener("dragover", (e) => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
    uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
    uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("drag-over");
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
}

if (fileInput) {
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
}

function handleFile(file) {
    if (!file.type.startsWith("image/")) {
        showToast("error", "Solo se aceptan archivos de imagen (JPG, PNG, WebP).");
        return;
    }
    selectedFile = file;
    const preview = document.getElementById("file-preview");
    const name = document.getElementById("file-name");
    const size = document.getElementById("file-size");
    const img = document.getElementById("preview-img");
    if (preview) preview.style.display = "block";
    if (name) name.textContent = file.name;
    if (size) size.textContent = (file.size / 1024).toFixed(1) + " KB";
    if (img) {
        const reader = new FileReader();
        reader.onload = (e) => img.src = e.target.result;
        reader.readAsDataURL(file);
    }
}

function clearFile() {
    selectedFile = null;
    if (fileInput) fileInput.value = "";
    const preview = document.getElementById("file-preview");
    if (preview) preview.style.display = "none";
}

async function uploadComprobante() {
    if (!selectedFile) return;
    const registroId = sessionStorage.getItem("eno_registro_id");
    if (!registroId) { showToast("error", "No se pudo identificar tu registro."); return; }

    const btn = document.getElementById("btn-upload");
    const btnText = document.getElementById("btn-upload-text");
    if (btn) btn.disabled = true;
    if (btnText) btnText.textContent = "Subiendo...";

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        const res = await fetch(`${API_BASE}/api/registros/${registroId}/comprobante`, {
            method: "POST",
            body: formData,
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Error al subir comprobante.");

        showToast("success", data.message || "¡Comprobante subido con éxito!");

        // Actualizar sesión guardada
        const s = JSON.parse(sessionStorage.getItem("eno_session") || "{}");
        if (s.data) {
            s.data.comprobantePago = data.data.comprobantePago;
            s.data.estadoPago = data.data.estadoPago;
            sessionStorage.setItem("eno_session", JSON.stringify(s));
        }

        setTimeout(() => location.reload(), 1500);
    } catch (err) {
        showToast("error", err.message);
        if (btn) btn.disabled = false;
        if (btnText) btnText.textContent = "Subir Comprobante";
    }
}

function logout() {
    sessionStorage.removeItem("eno_session");
    sessionStorage.removeItem("eno_registro_id");
    window.location.reload();
}

// ── Iniciar ────────────────────────────────────────────────────────
initDashboard();