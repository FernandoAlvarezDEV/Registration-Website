// ── Leer datos del registro desde sessionStorage ──
const rawData = sessionStorage.getItem("eno_registration");
const registrationData = rawData ? JSON.parse(rawData) : null;

if (registrationData) {
    // Código de registro oficial (ENO-A001 a ENO-Z100)
    const codeVal = registrationData.codigoRegistro || registrationData.id || "ENO-A001";
    const codeValEl = document.getElementById("code-value");
    if (codeValEl) {
        codeValEl.textContent = codeVal;
    }

    // Concepto de transferencia: [CÓDIGO] - [Nombre] - [Distrito/Municipio]
    const memoEl = document.getElementById("transfer-memo");
    if (memoEl) {
        const nombre = (registrationData.nombreCompleto || "").trim();
        const distrito = (registrationData.municipio || "").trim();
        memoEl.textContent = `${codeVal} - ${nombre || "Tu Nombre"} - ${distrito || "Tu Distrito"}`;
    }

    // Resumen de datos registrados
    const summaryEl = document.getElementById("summary-details");
    if (summaryEl) {
        const fields = [
            { label: "Número de Registro", value: codeVal, icon: "confirmation_number" },
            { label: "Nombre Completo", value: registrationData.nombreCompleto, icon: "person" },
            { label: "Teléfono", value: registrationData.telefono, icon: "phone" },
            { label: "Correo Electrónico", value: registrationData.email, icon: "alternate_email" },
            { label: "Municipio / Distrito", value: registrationData.municipio, icon: "location_on" },
            { label: "Talla de Camiseta", value: (registrationData.tallaCamiseta || "—").toUpperCase(), icon: "checkroom" },
            { label: "Estado del Registro", value: "Registrado - Pago Pendiente", icon: "schedule" },
        ];

        summaryEl.innerHTML = fields.map(f => `
            <div class="summary-item">
                <div class="summary-icon">
                    <span class="material-symbols-outlined" style="font-size:22px;">${f.icon}</span>
                </div>
                <div style="min-width:0; overflow:hidden;">
                    <div class="summary-label">${f.label}</div>
                    <div class="summary-val">${f.value || "—"}</div>
                </div>
            </div>
        `).join("");
    }
} else {
    // Si no hay datos en sessionStorage, mostrar aviso amigable
    const summaryCard = document.getElementById("summary-card");
    if (summaryCard) {
        summaryCard.innerHTML = `
            <div class="card-header">
                <span class="material-symbols-outlined" style="color:var(--fucsia);">info</span>
                <h3>Información de Inscripción</h3>
            </div>
            <div class="card-body" style="text-align:center; padding:32px 20px;">
                <span class="material-symbols-outlined" style="font-size:48px; color:var(--naranja); margin-bottom:12px; display:inline-block;">how_to_reg</span>
                <p style="font-size:1.05rem; font-weight:700; color:var(--oscuro); margin-bottom:8px;">No se encontraron datos en esta sesión local</p>
                <p style="font-size:0.9rem; color:#666; max-width:440px; margin:0 auto 20px;">
                    Si ya te registraste, puedes revisar tu estado con tu número de teléfono y nombre en el portal.
                </p>
                <a href="dashboard.html" class="btn-register-nav" style="display:inline-block;">Ir a Revisar Mi Inscripción →</a>
            </div>
        `;
    }
}

// ── Confetti animado con paleta oficial Onda Fest ──
function launchFestivalConfetti() {
    const container = document.getElementById("confetti-container");
    if (!container) return;

    const colors = ["#ED008C", "#FEB004", "#FF7D04", "#3CE705", "#FF0000", "#1A1A1A", "#FFFFFF"];
    const totalPieces = 50;

    for (let i = 0; i < totalPieces; i++) {
        const piece = document.createElement("div");
        piece.className = "confetti-piece";

        const startX = Math.random() * 100;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const delay = Math.random() * 1.2;
        const duration = 2.4 + Math.random() * 2;
        const sizeW = 6 + Math.random() * 8;
        const sizeH = 8 + Math.random() * 12;

        piece.style.left = `${startX}vw`;
        piece.style.top = `-20px`;
        piece.style.backgroundColor = color;
        piece.style.width = `${sizeW}px`;
        piece.style.height = `${sizeH}px`;
        piece.style.animationDelay = `${delay}s`;
        piece.style.animationDuration = `${duration}s`;
        piece.style.transform = `rotate(${Math.random() * 360}deg)`;

        container.appendChild(piece);

        setTimeout(() => {
            piece.remove();
        }, (delay + duration) * 1000 + 100);
    }
}

// Disparar confeti al cargar
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", launchFestivalConfetti);
} else {
    launchFestivalConfetti();
}