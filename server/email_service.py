"""
Email Service — ENO Portal
Envía correos usando Gmail SMTP con credenciales de App Password.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
              <h2 style="margin:0 0 8px;color:#ffffff;font-size:22px;font-weight:700;">¡Tu registro fue exitoso, {nombre}! 🎉</h2>
              <p style="margin:0 0 24px;color:#94a3b8;font-size:15px;line-height:1.6;">
                Gracias por inscribirte al <strong style="color:#ffffff;">Evento Nacional Onda 2026</strong>. Tu lugar está reservado.<br/>
                Para ver tu estado de registro y subir tu comprobante de pago, haz clic en el botón a continuación.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:linear-gradient(135deg,#2547f4,#4f6ef7);border-radius:12px;box-shadow:0 8px 30px rgba(37,71,244,0.4);">
                    <a href="{dashboard_url}"
                       style="display:inline-block;padding:16px 40px;color:#ffffff;font-size:16px;font-weight:700;text-decoration:none;letter-spacing:0.3px;">
                      Acceder a Mi Portal →
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#64748b;font-size:12px;text-align:center;">
                ⚠️ Este enlace es único y personal. No lo compartas con nadie.<br/>
                Es válido por <strong>72 horas</strong>.
              </p>

              <!-- Divider -->
              <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:32px 0;" />

              <!-- Event Details -->
              <h3 style="margin:0 0 16px;color:#ffffff;font-size:15px;font-weight:600;">📅 Detalles del Evento</h3>
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
                    <span style="color:#e2e8f0;font-size:14px;font-weight:600;">08:00 AM — 05:00 PM</span>
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
                ENO 2026 · Grupo Religioso Onda<br/>
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
    Retorna True si se envió correctamente, False si hubo error.
    """
    if not settings.GMAIL_USER or not settings.GMAIL_APP_PASSWORD:
        logger.warning("📧 Correo NO enviado: GMAIL_USER o GMAIL_APP_PASSWORD no configurados.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✅ Tu registro en ENO 2026 fue exitoso"
        msg["From"] = f"ENO 2026 <{settings.GMAIL_USER}>"
        msg["To"] = to_email

        html_body = _build_confirmation_email(nombre, token, settings.FRONTEND_URL)
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
            server.sendmail(settings.GMAIL_USER, to_email, msg.as_string())

        logger.info(f"📧 Correo enviado exitosamente a {to_email}")
        return True

    except Exception as e:
        logger.error(f"📧 Error enviando correo a {to_email}: {e}")
        return False
