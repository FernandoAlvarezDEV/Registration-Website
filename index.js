// ============================================================
// ENO Portal - Registration Form JavaScript
// ============================================================

// ─────────────────────────────────────────────────────────────
// 🔧 CONFIGURACIÓN DEL BACKEND (Edita esta sección para conectar)
// ─────────────────────────────────────────────────────────────
const API_CONFIG = {
    // URL del backend FastAPI
    BASE_URL: "http://localhost:8000",

    // Endpoints
    ENDPOINTS: {
        REGISTER: "/api/registros",            // POST - Registrar participante
        CHECK_STATUS: "/api/registros/buscar",  // GET  - Verificar si ya está registrado
        STATS: "/api/registros/stats",          // GET  - Estadísticas de registros
    },

    // Headers por defecto para las peticiones
    HEADERS: {
        "Content-Type": "application/json",
        // "Authorization": "Bearer TU_TOKEN_AQUI",  // Descomenta si necesitas auth
    },

    // Cuando tu backend FastAPI esté corriendo, pon esto en true.
    USE_REAL_BACKEND: true,
};


// ─────────────────────────────────────────────────────────────
// 📋 REFERENCIAS A ELEMENTOS DEL DOM
// ─────────────────────────────────────────────────────────────
const form = document.getElementById("registration-form");
const btnSubmit = document.getElementById("btn-submit");

const fields = {
    nombre: { input: document.getElementById("input-nombre"), error: document.getElementById("error-nombre") },
    edad: { input: document.getElementById("input-edad"), error: document.getElementById("error-edad") },
    telefono: { input: document.getElementById("input-telefono"), error: document.getElementById("error-telefono") },
    email: { input: document.getElementById("input-email"), error: document.getElementById("error-email") },
    municipio: { input: document.getElementById("input-municipio"), error: document.getElementById("error-municipio") },
    talla: { input: document.getElementById("input-talla"), error: document.getElementById("error-talla") },
};

const toastContainer = document.getElementById("toast-container");


// ─────────────────────────────────────────────────────────────
// ✅ VALIDACIONES
// ─────────────────────────────────────────────────────────────
const validators = {
    nombre(value) {
        if (!value.trim()) return "El nombre completo es obligatorio.";
        if (value.trim().length < 3) return "El nombre debe tener al menos 3 caracteres.";
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$/.test(value.trim())) return "El nombre solo puede contener letras.";
        return null;
    },

    edad(value) {
        if (!value) return "La edad es obligatoria.";
        const num = parseInt(value, 10);
        if (isNaN(num) || num < 1) return "Ingresa una edad válida.";
        if (num < 5) return "Debes tener al menos 5 años para registrarte.";
        if (num > 120) return "Ingresa una edad válida.";
        return null;
    },

    telefono(value) {
        if (!value.trim()) return "El número de teléfono es obligatorio.";
        // Acepta formatos como: +1 234 567 890, (809)555-1234, 8095551234
        const cleaned = value.replace(/[\s\-().+]/g, "");
        if (!/^\d{7,15}$/.test(cleaned)) return "Ingresa un número de teléfono válido (7 a 15 dígitos).";
        return null;
    },

    municipio(value) {
        if (!value) return "Debes seleccionar un municipio.";
        return null;
    },

    email(value) {
        if (!value.trim()) return "El correo electrónico es obligatorio.";
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value.trim())) return "Ingresa un correo electrónico válido.";
        return null;
    },

    talla(value) {
        if (!value) return "Debes seleccionar una talla de camiseta.";
        return null;
    },
};


// ─────────────────────────────────────────────────────────────
// 🎨 FUNCIONES DE UI
// ─────────────────────────────────────────────────────────────

/**
 * Muestra un error inline debajo de un campo.
 */
function showFieldError(fieldKey, message) {
    const { input, error } = fields[fieldKey];
    if (error) {
        error.textContent = message;
        error.classList.remove("hidden");
    }
    if (input) {
        input.classList.add("border-red-500", "ring-red-500");
        input.classList.remove("border-slate-300", "dark:border-slate-700");
    }
}

/**
 * Limpia el error inline de un campo.
 */
function clearFieldError(fieldKey) {
    const { input, error } = fields[fieldKey];
    if (error) {
        error.textContent = "";
        error.classList.add("hidden");
    }
    if (input) {
        input.classList.remove("border-red-500", "ring-red-500");
        input.classList.add("border-slate-300", "dark:border-slate-700");
    }
}

/**
 * Limpia todos los errores del formulario.
 */
function clearAllErrors() {
    Object.keys(fields).forEach(clearFieldError);
}

/**
 * Muestra una notificación toast.
 * @param {"success"|"error"|"info"} type 
 * @param {string} message 
 * @param {number} duration - Duración en ms (default 5000)
 */
function showToast(type, message, duration = 5000) {
    const colors = {
        success: "bg-emerald-600",
        error: "bg-red-600",
        info: "bg-blue-600",
    };
    const icons = {
        success: "check_circle",
        error: "error",
        info: "info",
    };

    const toast = document.createElement("div");
    toast.className = `flex items-center gap-3 ${colors[type]} text-white px-5 py-4 rounded-lg shadow-2xl text-sm font-medium transform translate-x-full opacity-0 transition-all duration-300 max-w-sm`;
    toast.innerHTML = `
    <span class="material-symbols-outlined text-lg">${icons[type]}</span>
    <span class="flex-1">${message}</span>
    <button class="ml-2 hover:opacity-70 transition-opacity" onclick="this.parentElement.remove()">
      <span class="material-symbols-outlined text-sm">close</span>
    </button>
  `;

    toastContainer.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove("translate-x-full", "opacity-0");
        toast.classList.add("translate-x-0", "opacity-100");
    });

    // Auto-remove
    setTimeout(() => {
        toast.classList.add("translate-x-full", "opacity-0");
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Muestra/esconde el estado de carga en el botón de submit.
 */
function setLoadingState(isLoading) {
    if (isLoading) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `
      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <span>Enviando...</span>
    `;
        btnSubmit.classList.add("opacity-70", "cursor-not-allowed");
    } else {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `
      <span class="material-symbols-outlined">send</span>
      Enviar Inscripción
    `;
        btnSubmit.classList.remove("opacity-70", "cursor-not-allowed");
    }
}


// ─────────────────────────────────────────────────────────────
// 🌐 FUNCIONES DE BACKEND / API
// ─────────────────────────────────────────────────────────────

/**
 * Envía los datos de registro al backend.
 * 
 * @param {Object} formData - Los datos del formulario
 * @returns {Promise<Object>} - La respuesta del servidor
 * 
 * 📌 INSTRUCCIONES PARA CONECTAR AL BACKEND:
 * 1. Cambia API_CONFIG.BASE_URL a la URL de tu API
 * 2. Cambia API_CONFIG.USE_REAL_BACKEND a true
 * 3. Ajusta los headers si necesitas autenticación
 * 4. Modifica el body del fetch si tu API espera un formato diferente
 */
async function submitRegistration(formData) {
    // ── Si USE_REAL_BACKEND es false, simula una respuesta ──
    if (!API_CONFIG.USE_REAL_BACKEND) {
        return simulateBackendResponse(formData);
    }

    // ── PETICIÓN REAL AL BACKEND ──
    const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REGISTER}`;

    const response = await fetch(url, {
        method: "POST",
        headers: API_CONFIG.HEADERS,
        body: JSON.stringify(formData),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Error del servidor (${response.status})`);
    }

    return response.json();
}

/**
 * Simula una respuesta de backend para desarrollo local.
 * Elimina esta función cuando conectes el backend real.
 */
async function simulateBackendResponse(formData) {
    // Simula un delay de red (800ms - 1500ms)
    const delay = Math.random() * 700 + 800;
    await new Promise((resolve) => setTimeout(resolve, delay));

    // Simula un 10% de probabilidad de error para testing
    if (Math.random() < 0.1) {
        throw new Error("Error simulado del servidor. Intenta de nuevo.");
    }

    // Respuesta exitosa simulada
    console.log("📨 Datos enviados (simulado):", formData);
    return {
        success: true,
        message: "Registro exitoso",
        data: {
            id: `ENO-${Date.now()}`,
            ...formData,
            registeredAt: new Date().toISOString(),
        },
    };
}

/**
 * 📌 FUNCIÓN PLACEHOLDER: Verificar si un usuario ya está registrado.
 * Implementa esta función según tu backend.
 */
async function checkExistingRegistration(telefono) {
    if (!API_CONFIG.USE_REAL_BACKEND) {
        // Simulación: siempre devuelve que no está registrado
        return { exists: false };
    }

    const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHECK_STATUS}?telefono=${encodeURIComponent(telefono)}`;
    const response = await fetch(url, {
        method: "GET",
        headers: API_CONFIG.HEADERS,
    });

    if (!response.ok) throw new Error("No se pudo verificar el registro.");
    return response.json();
}


// ─────────────────────────────────────────────────────────────
// 🚀 LÓGICA PRINCIPAL DEL FORMULARIO
// ─────────────────────────────────────────────────────────────

/**
 * Limpia el número de teléfono: elimina espacios, guiones, paréntesis, puntos y el prefijo +1.
 */
function cleanPhoneNumber(phone) {
    let cleaned = phone.replace(/[\s\-().]/g, "");
    // Eliminar prefijo +1 si existe
    if (cleaned.startsWith("+1")) {
        cleaned = cleaned.substring(2);
    }
    return cleaned;
}

/**
 * Recolecta los datos del formulario en un objeto limpio.
 */
function getFormData() {
    return {
        nombreCompleto: fields.nombre.input.value.trim(),
        edad: parseInt(fields.edad.input.value, 10),
        telefono: cleanPhoneNumber(fields.telefono.input.value.trim()),
        email: fields.email.input.value.trim(),
        municipio: fields.municipio.input.value,
        tallaCamiseta: fields.talla.input.value,
    };
}

/**
 * Valida todos los campos del formulario.
 * @returns {boolean} true si todo es válido
 */
function validateForm() {
    let isValid = true;
    clearAllErrors();

    Object.keys(fields).forEach((key) => {
        const value = fields[key].input.value;
        const error = validators[key](value);
        if (error) {
            showFieldError(key, error);
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Maneja el envío del formulario.
 */
async function handleSubmit(event) {
    event.preventDefault();

    // 1. Validar campos
    if (!validateForm()) {
        showToast("error", "Por favor corrige los errores en el formulario.");
        // Scroll al primer error visible
        const firstError = document.querySelector(".border-red-500");
        if (firstError) firstError.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
    }

    // 2. Recoger datos
    const formData = getFormData();

    // 3. Mostrar estado de carga
    setLoadingState(true);

    try {
        // 4. (Opcional) Verificar registro existente
        const existing = await checkExistingRegistration(formData.telefono);
        if (existing.exists) {
            showToast("info", "Ya estás registrado para este evento. Revisa tu correo de confirmación.");
            setLoadingState(false);
            return;
        }

        // 5. Enviar registro
        const result = await submitRegistration(formData);

        // 6. Éxito — Guardar datos y redirigir a página de confirmación
        console.log("✅ Registro exitoso:", result);

        // Guardar en sessionStorage para la página de éxito
        const registrationInfo = {
            ...formData,
            id: result.data?.id || `ENO-${Date.now()}`,
            fechaRegistro: result.data?.fechaRegistro || new Date().toISOString(),
        };
        sessionStorage.setItem("eno_registration", JSON.stringify(registrationInfo));

        // Redirigir a la página de confirmación
        window.location.href = "success.html";
    } catch (error) {
        // 7. Error
        console.error("❌ Error al registrar:", error);
        showToast("error", error.message || "Hubo un error al enviar tu registro. Intenta de nuevo.");
    } finally {
        setLoadingState(false);
    }
}


// ─────────────────────────────────────────────────────────────
// 🎧 EVENT LISTENERS
// ─────────────────────────────────────────────────────────────

// Submit del formulario
form.addEventListener("submit", handleSubmit);

// Validación en tiempo real (al salir de un campo)
Object.keys(fields).forEach((key) => {
    const input = fields[key].input;
    if (!input) return;

    // Validar al perder foco
    input.addEventListener("blur", () => {
        const error = validators[key](input.value);
        if (error) {
            showFieldError(key, error);
        } else {
            clearFieldError(key);
        }
    });

    // Limpiar error al empezar a escribir
    input.addEventListener("input", () => {
        clearFieldError(key);
    });
});

// Log de inicialización
console.log("🟢 ENO Portal - Formulario de registro inicializado.");
console.log(`🔧 Backend real: ${API_CONFIG.USE_REAL_BACKEND ? "ACTIVADO" : "DESACTIVADO (modo simulación)"}`);
