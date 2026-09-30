"""
Email Service — ENO Portal
Envía correos usando la API HTTP de Brevo
"""

import logging
import requests
from config import settings

logger = logging.getLogger(__name__)


def _build_confirmation_email(nombre: str, token: str, frontend_url: str) -> str:
    """Construye el HTML del correo de confirmación de registro."""
    dashboard_url = f"{frontend_url}/dashboard.html?token={token}"
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Confirmación de Registro — ENO 2026</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
  </style>
</head>
<body style="margin:0;padding:0;background:#F9F4E0;font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1a1a1a;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.05);border:2px solid #FF0000;">
          
          <!-- Header -->
          <tr>
            <td style="background:#FF0000;padding:40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:36px;font-family:'Syne',Arial,sans-serif;font-weight:800;letter-spacing:-1px;text-transform:uppercase;">Onda Fest</h1>
              <p style="margin:8px 0 0;color:#F9F4E0;font-size:14px;letter-spacing:2px;text-transform:uppercase;font-weight:600;">Una Sola Onda</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 12px;color:#FF0000;font-size:24px;font-family:'Syne',Arial,sans-serif;font-weight:800;">¡Tu registro fue exitoso, {nombre}!</h2>
              <p style="margin:0 0 24px;font-size:16px;line-height:1.6;color:#333333;">
                Gracias por inscribirte al <strong>Evento Nacional Onda 2026</strong>. Tu lugar está reservado y estamos listos para vivir esta experiencia contigo.<br/><br/>
                Para ver tu estado de registro, subir tu comprobante de pago o acceder a tu código QR, haz clic en el botón a continuación.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:#FEB004;border-radius:12px;border:2px solid #1a1a1a;box-shadow:4px 4px 0px #1a1a1a;">
                    <a href="{dashboard_url}"
                       style="display:inline-block;padding:16px 40px;color:#1a1a1a;font-size:16px;font-weight:800;text-decoration:none;text-transform:uppercase;letter-spacing:1px;font-family:'Plus Jakarta Sans',Arial,sans-serif;">
                      Acceder a Mi Portal
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#666666;font-size:13px;text-align:center;">
                Este enlace es único y personal. No lo compartas con nadie.<br/>
                Es válido por <strong>72 horas</strong>.
              </p>

              <!-- Divider -->
              <hr style="border:none;border-top:2px dashed #FF7D04;margin:32px 0;" />

              <!-- Event Details -->
              <h3 style="margin:0 0 16px;color:#ED008C;font-size:18px;font-family:'Syne',Arial,sans-serif;font-weight:700;">Detalles del Evento</h3>
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;border-radius:12px;padding:20px;border:2px solid #FF7D04;">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,125,4,0.2);">
                    <span style="color:#FF0000;font-size:13px;font-weight:700;text-transform:uppercase;">Fecha</span><br/>
                    <span style="font-size:15px;font-weight:600;">13 de Diciembre, 2026</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,125,4,0.2);">
                    <span style="color:#FF0000;font-size:13px;font-weight:700;text-transform:uppercase;">Lugar</span><br/>
                    <span style="font-size:15px;font-weight:600;">Próximamente</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,125,4,0.2);">
                    <span style="color:#FF0000;font-size:13px;font-weight:700;text-transform:uppercase;">Hora</span><br/>
                    <span style="font-size:15px;font-weight:600;">08:00 AM - 05:00 PM</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;">
                    <span style="color:#FF0000;font-size:13px;font-weight:700;text-transform:uppercase;">Precio</span><br/>
                    <span style="font-size:15px;font-weight:600;">RD$600 Pesos Dominicanos</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#F9F4E0;border-top:2px solid #FF0000;padding:24px 40px;text-align:center;">
              <p style="margin:0;color:#666666;font-size:12px;line-height:1.6;font-weight:600;">
                ENO 2026 - Grupo Religioso Onda<br/>
                Si no realizaste este registro, ignora este correo.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""



def _build_receipt_uploaded_email(nombre: str, frontend_url: str) -> str:
    """Construye el HTML del correo de comprobante subido."""
    return f"""
<!DOCTYPE html>
<html lang="es">
<body style="margin:0;padding:0;background:#F9F4E0;font-family:Arial,sans-serif;color:#1a1a1a;">
  <div style="max-width:600px;margin:0 auto;background:#ffffff;padding:40px;border-radius:16px;border:2px solid #FF0000;text-align:center;">
    <h2 style="color:#FF0000;">¡Hola {nombre}, hemos recibido tu comprobante!</h2>
    <p>Tu comprobante de pago está siendo revisado por nuestro equipo. Te notificaremos cuando el estado de tu pago se actualice a Verificado o Rechazado.</p>
    <a href="{frontend_url}/verificar.html" style="display:inline-block;padding:12px 24px;background:#FEB004;color:#1a1a1a;font-weight:bold;text-decoration:none;border-radius:8px;">Ver Mi Portal</a>
  </div>
</body>
</html>
"""

def _build_payment_status_email(nombre: str, status: str, frontend_url: str) -> str:
    """Construye el HTML del correo de cambio de estado de pago."""
    color = "#28a745" if status == "verificado" else "#dc3545"
    mensaje = "¡Tu pago ha sido verificado exitosamente! Tu cupo en el Onda Fest 2026 está totalmente asegurado." if status == "verificado" else "Ha habido un problema con tu comprobante de pago y ha sido rechazado. Por favor, accede a tu portal para subir un comprobante válido."
    return f"""
<!DOCTYPE html>
<html lang="es">
<body style="margin:0;padding:0;background:#F9F4E0;font-family:Arial,sans-serif;color:#1a1a1a;">
  <div style="max-width:600px;margin:0 auto;background:#ffffff;padding:40px;border-radius:16px;border:2px solid {color};text-align:center;">
    <h2 style="color:{color};">Actualización de Pago: {status.upper()}</h2>
    <p>Hola {nombre}, te informamos que el estado de tu pago ha cambiado.</p>
    <p><strong>{mensaje}</strong></p>
    <a href="{frontend_url}/verificar.html" style="display:inline-block;padding:12px 24px;background:#FEB004;color:#1a1a1a;font-weight:bold;text-decoration:none;border-radius:8px;">Ver Mi Portal</a>
  </div>
</body>
</html>
"""

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
