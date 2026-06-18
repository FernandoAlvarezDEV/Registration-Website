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
</head>
<body style="margin:0;padding:0;background:#0f1629;font-family:'Inter',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1629;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a2550 0%,#2547f4 100%);border-radius:16px 16px 0 0;padding:40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:32px;font-weight:900;letter-spacing:-1px;">ENO 2026</h1>
              <p style="margin:8px 0 0;color:rgba(255,255,255,0.7);font-size:14px;letter-spacing:2px;text-transform:uppercase;">Grupo Religioso Onda</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#1a2035;padding:40px;border-left:1px solid rgba(37,71,244,0.2);border-right:1px solid rgba(37,71,244,0.2);">
              <h2 style="margin:0 0 8px;color:#ffffff;font-size:22px;font-weight:700;">Tu registro fue exitoso, {nombre}!</h2>
              <p style="margin:0 0 24px;color:#94a3b8;font-size:15px;line-height:1.6;">
                Gracias por inscribirte al <strong style="color:#ffffff;">Evento Nacional Onda 2026</strong>. Tu lugar esta reservado.<br/>
                Para ver tu estado de registro y subir tu comprobante de pago, haz clic en el boton a continuacion.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:linear-gradient(135deg,#2547f4,#4f6ef7);border-radius:12px;box-shadow:0 8px 30px rgba(37,71,244,0.4);">
                    <a href="{dashboard_url}"
                       style="display:inline-block;padding:16px 40px;color:#ffffff;font-size:16px;font-weight:700;text-decoration:none;letter-spacing:0.3px;">
                      Acceder a Mi Portal
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#64748b;font-size:12px;text-align:center;">
                Este enlace es unico y personal. No lo compartas con nadie.<br/>
                Es valido por <strong>72 horas</strong>.
              </p>

              <!-- Divider -->
              <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:32px 0;" />

              <!-- Event Details -->
              <h3 style="margin:0 0 16px;color:#ffffff;font-size:15px;font-weight:600;">Detalles del Evento</h3>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                    <span style="color:#64748b;font-size:13px;">Fecha</span><br/>
                    <span style="color:#e2e8f0;font-size:14px;font-weight:600;">13 de Diciembre, 2026</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                    <span style="color:#64748b;font-size:13px;">Lugar</span><br/>
                    <span style="color:#e2e8f0;font-size:14px;font-weight:600;">Colegio Loyola, Av. Abraham Lincoln, Santo Domingo</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                    <span style="color:#64748b;font-size:13px;">Hora</span><br/>
                    <span style="color:#e2e8f0;font-size:14px;font-weight:600;">08:00 AM - 05:00 PM</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;">
                    <span style="color:#64748b;font-size:13px;">Precio</span><br/>
                    <span style="color:#e2e8f0;font-size:14px;font-weight:600;">RD$700 Pesos Dominicanos</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#131929;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border:1px solid rgba(37,71,244,0.1);border-top:none;">
              <p style="margin:0;color:#475569;font-size:12px;line-height:1.6;">
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
