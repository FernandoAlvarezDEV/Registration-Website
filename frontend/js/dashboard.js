const API_BASE = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://localhost:8000"
    : "https://eno-portal-backend-production.up.railway.app";

// ── Toast ──────────────────────────────────────────────────────────
function showToast(type, msg) {
    const t = document.getElementById("toast");
    t.className = `toast toast-${type} show`;
    t.textContent = msg;
    setTimeout(() => t.classList.remove("show"), 4000);
}

// ── Mostrar estado de pago en UI ───────────────────────────────────
function renderPaymentStatus(estadoPago) {
    const badge = document.getElementById("pago-badge");
    if (!badge) return;
    const statusMap = {
        "pendiente":    { bg: "bg-amber-500/90",   icon: "schedule",     text: "Pago Pendiente" },
        "en revisión":  { bg: "bg-blue-500/90",    icon: "hourglass_top",text: "En Revisión" },
        "verificado":   { bg: "bg-emerald-500/90", icon: "verified",     text: "Pago Verificado" },
        "rechazado":    { bg: "bg-red-500/90",      icon: "cancel",       text: "Pago Rechazado" },
    };
    const status = statusMap[estadoPago] || statusMap["pendiente"];
    badge.className = `inline-flex items-center gap-1 ${status.bg} text-white text-sm font-bold px-4 py-2 rounded-full`;
    badge.innerHTML = `<span class="material-symbols-outlined text-sm">${status.icon}</span> ${status.text}`;
}

// ── Rellenar UI con los datos del usuario ──────────────────────────
function populateUI(d) {
    const registroId = d.id ? parseInt(d.id.toString().replace("ENO-", "")) : d.id;

    // Guardar en sessionStorage para uso posterior (subir comprobante, etc.)
    sessionStorage.setItem("eno_session", JSON.stringify({
        role: "user",
        data: { ...d, idLabel: `ENO-${registroId}` }
    }));
    sessionStorage.setItem("eno_registro_id", registroId);

    // Rellenar campos HTML
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("header-name", d.nombreCompleto);
    set("user-name", d.nombreCompleto);
    set("reg-code", d.idLabel || `ENO-${registroId}`);
    set("detail-nombre", d.nombreCompleto);
    set("detail-edad", d.edad ? `${d.edad} años` : "—");
    set("detail-telefono", d.telefono || "—");
    set("detail-email", d.email || "—");
    set("detail-municipio", d.municipio || "—");
    set("detail-talla", (d.tallaCamiseta || "—").toUpperCase());
    set("detail-fecha", d.fechaRegistro
        ? new Date(d.fechaRegistro).toLocaleDateString("es-DO", { year: "numeric", month: "long", day: "numeric" })
        : "—");

    renderPaymentStatus(d.estadoPago || "pendiente");

    // Comprobante ya subido
    if (d.comprobantePago) {
        const uploaded = document.getElementById("comprobante-uploaded");
        const uploadZone = document.getElementById("upload-zone-container");
        const preview = document.getElementById("comprobante-preview-existing");
        if (uploaded) uploaded.classList.remove("hidden");
        if (uploadZone) uploadZone.classList.add("hidden");
        if (preview) preview.src = d.comprobantePago.startsWith("http")
            ? d.comprobantePago
            : `${API_BASE}${d.comprobantePago}`;
    }

    // Mostrar dashboard, ocultar loader
    const loader = document.getElementById("loading-screen");
    const main = document.getElementById("dashboard-main");
    if (loader) loader.classList.add("hidden");
    if (main) main.classList.remove("hidden");
}

// ── Mostrar pantalla de error ──────────────────────────────────────
function showError(msg) {
    const loader = document.getElementById("loading-screen");
    const errorScreen = document.getElementById("error-screen");
    const errorMsg = document.getElementById("error-message");
    if (loader) loader.classList.add("hidden");
    if (errorScreen) errorScreen.classList.remove("hidden");
    if (errorMsg) errorMsg.textContent = msg;
}

// ── Lógica principal de autenticación ─────────────────────────────
async function initDashboard() {
    // 1. Intentar leer token de la URL (?token=xyz)
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");

    if (urlToken) {
        // Verificar token con el backend
        try {
            const res = await fetch(`${API_BASE}/api/auth/verify?token=${encodeURIComponent(urlToken)}`);
            const data = await res.json();

            if (!res.ok) {
                showError(data.detail || "Este enlace es inválido o ha expirado.");
                return;
            }

            // Limpiar el token de la URL para no exponerlo en historial
            window.history.replaceState({}, document.title, window.location.pathname);

            populateUI(data.data);
        } catch (err) {
            showError("No se pudo conectar con el servidor. Intenta de nuevo.");
        }
        return;
    }

    // 2. Si no hay token en URL, revisar sessionStorage (sesión activa)
    const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");

    if (session && session.data && session.role === "user") {
        populateUI(session.data);
        return;
    }

    // 3. Sin token y sin sesión: mostrar error
    showError("No se encontró un enlace de acceso válido. Revisa tu correo electrónico para obtener tu enlace de acceso.");
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
        showToast("error", "Solo se aceptan imágenes.");
        return;
    }
    selectedFile = file;
    const preview = document.getElementById("file-preview");
    const name = document.getElementById("file-name");
    const size = document.getElementById("file-size");
    const img = document.getElementById("preview-img");
    if (preview) preview.classList.remove("hidden");
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
    if (preview) preview.classList.add("hidden");
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

        showToast("success", data.message);

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
    window.location.href = "index.html";
}

// ── Iniciar ────────────────────────────────────────────────────────
initDashboard();