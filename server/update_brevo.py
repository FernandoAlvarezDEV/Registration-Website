import re

with open("c:\\Users\\ferjo\\Desktop\\Proyectos Personales\\Registration-Website\\server\\email_service.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace imports
content = content.replace("import resend", "import requests")
content = content.replace("Envía correos usando la API HTTP de Resend (funciona en Render, Vercel, etc.)", "Envía correos usando la API HTTP de Brevo")

# Define the new sending logic
new_logic = """
def _send_brevo_email(to_email: str, subject: str, html_content: str, nombre: str = "") -> bool:
    if not settings.BREVO_API_KEY:
        logger.warning(f"[EMAIL] Correo NO enviado a {to_email}: BREVO_API_KEY no configurada.")
        return False
        
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "ENO 2026", "email": settings.BREVO_FROM_EMAIL},
        "to": [{"email": to_email, "name": nombre}],
        "subject": subject,
        "htmlContent": html_content
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201, 202):
            logger.info(f"[EMAIL] Correo enviado exitosamente a {to_email}")
            return True
        else:
            logger.error(f"[EMAIL] Error de Brevo al enviar a {to_email}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"[EMAIL] Excepción enviando correo a {to_email}: {e}")
        return False

def send_confirmation_email(to_email: str, nombre: str, token: str) -> bool:
    if not settings.BREVO_API_KEY:
        dashboard_url = f"{settings.FRONTEND_URL}/dashboard.html?token={token}"
        logger.info(f"--- MAGIC LINK LOCAL ---")
        logger.info(f"🔗 Para probar haz clic aquí: {dashboard_url}")
        logger.info(f"------------------------")
        
    html_body = _build_confirmation_email(nombre, token, settings.FRONTEND_URL)
    return _send_brevo_email(to_email, "Tu registro en ENO 2026 fue exitoso", html_body, nombre)

def send_receipt_uploaded_email(to_email: str, nombre: str) -> bool:
    html_body = _build_receipt_uploaded_email(nombre, settings.FRONTEND_URL)
    return _send_brevo_email(to_email, "Tu comprobante está en revisión", html_body, nombre)

def send_payment_status_email(to_email: str, nombre: str, status: str) -> bool:
    subject = "¡Pago Verificado! - ENO 2026" if status.lower() == "verificado" else "Atención con tu pago - ENO 2026"
    html_body = _build_payment_status_email(nombre, status, settings.FRONTEND_URL)
    return _send_brevo_email(to_email, subject, html_body, nombre)
"""

# Find where send_confirmation_email starts and replace everything after it
start_idx = content.find("def send_confirmation_email(")
if start_idx != -1:
    content = content[:start_idx] + new_logic

with open("c:\\Users\\ferjo\\Desktop\\Proyectos Personales\\Registration-Website\\server\\email_service.py", "w", encoding="utf-8") as f:
    f.write(content)
