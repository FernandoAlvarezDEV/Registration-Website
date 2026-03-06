// ── Leer datos del registro desde sessionStorage ──
        const registrationData = JSON.parse(sessionStorage.getItem("eno_registration") || "null");

        if (registrationData) {
            // Código de registro
            const codeEl = document.getElementById("registration-code");
            if (registrationData.id) {
                codeEl.textContent = `Código de registro: ${registrationData.id}`;
            }

            // Resumen de datos
            const summaryEl = document.getElementById("summary-details");
            const fields = [
                { label: "Nombre Completo", value: registrationData.nombreCompleto, icon: "person" },
                { label: "Edad", value: `${registrationData.edad} años`, icon: "cake" },
                { label: "Teléfono", value: registrationData.telefono, icon: "phone" },
                { label: "Correo Electrónico", value: registrationData.email, icon: "email" },
                { label: "Municipio", value: registrationData.municipio, icon: "location_city" },
                { label: "Talla de Camiseta", value: (registrationData.tallaCamiseta || "").toUpperCase(), icon: "checkroom" },
            ];

            summaryEl.innerHTML = fields.map(f => `
                <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                    <span class="material-symbols-outlined text-primary text-lg">${f.icon}</span>
                    <div>
                        <p class="text-slate-400 text-xs font-medium">${f.label}</p>
                        <p class="text-slate-800 font-semibold">${f.value || "—"}</p>
                    </div>
                </div>
            `).join("");

            // Limpiar sessionStorage después de mostrar
            sessionStorage.removeItem("eno_registration");
        } else {
            // Si no hay datos, mostrar mensaje genérico
            document.getElementById("summary-card").innerHTML = `
                <div class="text-center py-4">
                    <span class="material-symbols-outlined text-slate-300 mb-2" style="font-size: 48px;">info</span>
                    <p class="text-slate-400">No se encontraron datos de registro recientes.</p>
                    <a href="Index.html" class="text-primary font-semibold text-sm hover:underline mt-2 inline-block">Ir al formulario de registro →</a>
                </div>
            `;
        }

        // ── Confetti animation ──
        function createConfetti() {
            const container = document.getElementById("confetti-container");
            const colors = ["#2547f4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];
            for (let i = 0; i < 40; i++) {
                const piece = document.createElement("div");
                piece.className = "confetti-piece";
                piece.style.left = Math.random() * 100 + "vw";
                piece.style.top = Math.random() * 60 + 40 + "vh";
                piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                piece.style.animationDelay = Math.random() * 0.8 + "s";
                piece.style.animationDuration = (Math.random() * 1 + 1) + "s";
                piece.style.width = (Math.random() * 8 + 5) + "px";
                piece.style.height = (Math.random() * 8 + 5) + "px";
                container.appendChild(piece);
                setTimeout(() => piece.remove(), 2500);
            }
        }
        createConfetti();