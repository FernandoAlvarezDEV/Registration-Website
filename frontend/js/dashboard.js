const API_BASE = "http://localhost:8000";

        // Toast
        function showToast(type, msg) {
            const t = document.getElementById("toast");
            t.className = `toast toast-${type} show`;
            t.textContent = msg;
            setTimeout(() => t.classList.remove("show"), 4000);
        }

        // Check session
        const session = JSON.parse(sessionStorage.getItem("eno_session") || "null");
        let registroId = null;

        if (!session || !session.data || session.role === "admin") {
            window.location.href = "login.html";
        } else {
            const d = session.data;
            registroId = d.id ? parseInt(d.id.replace("ENO-", "")) : null;
            document.getElementById("header-name").textContent = d.nombreCompleto;
            document.getElementById("user-name").textContent = d.nombreCompleto;
            document.getElementById("reg-code").textContent = d.id || "—";
            document.getElementById("detail-nombre").textContent = d.nombreCompleto;
            document.getElementById("detail-edad").textContent = d.edad ? `${d.edad} años` : "—";
            document.getElementById("detail-telefono").textContent = d.telefono || "—";
            document.getElementById("detail-email").textContent = d.email || "—";
            document.getElementById("detail-municipio").textContent = d.municipio || "—";
            document.getElementById("detail-talla").textContent = (d.tallaCamiseta || "—").toUpperCase();
            document.getElementById("detail-fecha").textContent = d.fechaRegistro
                ? new Date(d.fechaRegistro).toLocaleDateString("es-DO", { year: "numeric", month: "long", day: "numeric" })
                : "—";

            // Payment status badge
            const estadoPago = d.estadoPago || "pendiente";
            const badge = document.getElementById("pago-badge");
            const statusMap = {
                "pendiente": { bg: "bg-amber-500/90", icon: "schedule", text: "Pago Pendiente" },
                "en revisión": { bg: "bg-blue-500/90", icon: "hourglass_top", text: "En Revisión" },
                "verificado": { bg: "bg-emerald-500/90", icon: "verified", text: "Pago Verificado" },
                "rechazado": { bg: "bg-red-500/90", icon: "cancel", text: "Pago Rechazado" },
            };
            const status = statusMap[estadoPago] || statusMap["pendiente"];
            badge.className = `inline-flex items-center gap-1 ${status.bg} text-white text-sm font-bold px-4 py-2 rounded-full`;
            badge.innerHTML = `<span class="material-symbols-outlined text-sm">${status.icon}</span> ${status.text}`;

            // Comprobante already uploaded
            if (d.comprobantePago) {
                document.getElementById("comprobante-uploaded").classList.remove("hidden");
                document.getElementById("upload-zone-container").classList.add("hidden");
                document.getElementById("comprobante-preview-existing").src = `${API_BASE}${d.comprobantePago}`;
            }
        }

        // File upload logic
        let selectedFile = null;
        const fileInput = document.getElementById("file-input");
        const uploadZone = document.getElementById("upload-zone");

        // Drag & Drop
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
            document.getElementById("file-preview").classList.remove("hidden");
            document.getElementById("file-name").textContent = file.name;
            document.getElementById("file-size").textContent = (file.size / 1024).toFixed(1) + " KB";
            const reader = new FileReader();
            reader.onload = (e) => document.getElementById("preview-img").src = e.target.result;
            reader.readAsDataURL(file);
        }

        function clearFile() {
            selectedFile = null;
            fileInput.value = "";
            document.getElementById("file-preview").classList.add("hidden");
        }

        async function uploadComprobante() {
            if (!selectedFile || !registroId) return;

            const btn = document.getElementById("btn-upload");
            const btnText = document.getElementById("btn-upload-text");
            btn.disabled = true;
            btnText.textContent = "Subiendo...";

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

                // Update session
                const s = JSON.parse(sessionStorage.getItem("eno_session"));
                s.data.comprobantePago = data.data.comprobantePago;
                s.data.estadoPago = data.data.estadoPago;
                sessionStorage.setItem("eno_session", JSON.stringify(s));

                // Update UI
                setTimeout(() => location.reload(), 1500);

            } catch (err) {
                showToast("error", err.message);
                btn.disabled = false;
                btnText.textContent = "Subir Comprobante";
            }
        }

        function logout() {
            sessionStorage.removeItem("eno_session");
            window.location.href = "login.html";
        }