const API_BASE = "http://localhost:8000";
        const form = document.getElementById("login-form");
        const btnLogin = document.getElementById("btn-login");
        const btnText = document.getElementById("btn-login-text");

        // Toast
        function showToast(type, message) {
            const toast = document.getElementById("toast");
            toast.className = `toast toast-${type} show`;
            toast.textContent = message;
            setTimeout(() => toast.classList.remove("show"), 4000);
        }

        // Clean phone
        function cleanPhone(phone) {
            let c = phone.replace(/[\s\-().]/g, "");
            if (c.startsWith("+1")) c = c.substring(2);
            return c;
        }

        // Handle login
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nombre = document.getElementById("login-nombre").value.trim();
            const telefono = document.getElementById("login-telefono").value.trim();

            // Validation
            if (!nombre) { showToast("error", "Ingresa tu nombre completo."); return; }
            if (!telefono) { showToast("error", "Ingresa tu número de teléfono."); return; }

            // Loading state
            btnLogin.disabled = true;
            btnText.textContent = "Verificando...";

            try {
                const response = await fetch(`${API_BASE}/api/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        nombreCompleto: nombre,
                        telefono: cleanPhone(telefono),
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Error al iniciar sesión.");
                }

                // Save session
                sessionStorage.setItem("eno_session", JSON.stringify(data));

                // Redirect based on role
                if (data.role === "admin") {
                    window.location.href = "admin.html";
                } else {
                    window.location.href = "dashboard.html";
                }

            } catch (error) {
                showToast("error", error.message);
            } finally {
                btnLogin.disabled = false;
                btnText.textContent = "Iniciar Sesión";
            }
        });