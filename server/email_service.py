"""
Email Service — ENO Portal
Envía correos usando la API HTTP de Resend (funciona en Render, Vercel, etc.)
"""

import logging
import resend
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
                    <span style="font-size:15px;font-weight:600;">Colegio Loyola, Av. Abraham Lincoln, Santo Domingo</span>
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


def send_confirmation_email(to_email: str, nombre: str, token: str) -> bool:
    """
    Envía el correo de confirmación con el enlace mágico al usuario.
    Usa la API HTTP de Resend (no SMTP, funciona en cualquier hosting).
    Retorna True si se envió correctamente, False si hubo error.
    """
    if not settings.RESEND_API_KEY:
        logger.warning("[EMAIL] Correo NO enviado: RESEND_API_KEY no configurada.")
        # Print link to console for easy local testing
        dashboard_url = f"{settings.FRONTEND_URL}/dashboard.html?token={token}"
        logger.info(f"--- MAGIC LINK LOCAL ---")
        logger.info(f"🔗 Para probar haz clic aquí: {dashboard_url}")
        logger.info(f"------------------------")
        return False

    try:
        resend.api_key = settings.RESEND_API_KEY

        html_body = _build_confirmation_email(nombre, token, settings.FRONTEND_URL)

        params: resend.Emails.SendParams = {
            "from": f"ENO 2026 <{settings.RESEND_FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Tu registro en ENO 2026 fue exitoso",
            "html": html_body,
        }

        email_response = resend.Emails.send(params)
        logger.info(f"[EMAIL] Correo enviado exitosamente a {to_email} | ID: {email_response.get('id', 'N/A')}")
        return True

    except Exception as e:
        logger.error(f"[EMAIL] Error enviando correo a {to_email}: {e}")
        return False
