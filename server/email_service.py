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
    logo_url = f"{frontend_url}/img/LOGO%20VERSI%20HORIZONTAL%201.png"
    icon_url = f"{frontend_url}/img/iconos/ESTRELLA%20FUCSIA.png"

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Confirmación de Registro — ENO 2026</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
  </style>
</head>
<body style="margin:0;padding:0;background:#F9F4E0;font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1A1A1A;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;padding:40px 10px;">
    <tr>
      <td align="center">
        <!-- Logo -->
        <a href="{frontend_url}" style="display:inline-block;margin-bottom:20px;">
            <img src="{logo_url}" alt="Onda Fest Logo" style="height:50px;display:block;border:0;" />
        </a>

        <!-- Main Card -->
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;border:3px solid #1A1A1A;box-shadow:6px 6px 0px #1A1A1A;">
          
          <!-- Header -->
          <tr>
            <td style="background:#ED008C;padding:40px 20px;text-align:center;border-bottom:3px solid #1A1A1A;">
              <h1 style="margin:0;color:#ffffff;font-size:34px;font-family:'Syne',Arial,sans-serif;font-weight:800;letter-spacing:-1px;text-transform:uppercase;">Registro Exitoso</h1>
              <p style="margin:8px 0 0;color:#ffffff;font-size:14px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">Onda Fest 2026</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 30px;">
              <h2 style="margin:0 0 16px;color:#1A1A1A;font-size:24px;font-family:'Syne',Arial,sans-serif;font-weight:800;">¡Hola {nombre}!</h2>
              <p style="margin:0 0 24px;font-size:16px;line-height:1.6;color:#333333;font-weight:500;">
                Gracias por inscribirte al <strong>Evento Nacional Onda 2026</strong>. Tu lugar está reservado y estamos listos para vivir esta experiencia contigo.<br/><br/>
                Para ver tu estado, subir tu comprobante de pago o acceder a tu código QR, haz clic en el botón a continuación.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:#FEB004;border-radius:10px;border:3px solid #1A1A1A;box-shadow:4px 4px 0px #1A1A1A;text-align:center;">
                    <a href="{dashboard_url}"
                       style="display:block;padding:16px 32px;color:#1A1A1A;font-size:16px;font-weight:800;text-decoration:none;text-transform:uppercase;letter-spacing:0.5px;font-family:'Syne',Arial,sans-serif;">
                      Ir a Mi Portal
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <hr style="border:none;border-top:3px solid #1A1A1A;margin:32px 0;" />

              <!-- Event Details -->
              <h3 style="margin:0 0 16px;color:#ED008C;font-size:20px;font-family:'Syne',Arial,sans-serif;font-weight:800;text-transform:uppercase;">Detalles del Evento</h3>
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;border-radius:10px;border:3px solid #1A1A1A;box-shadow:3px 3px 0px #1A1A1A;">
                <tr>
                  <td style="padding:16px 20px;border-bottom:2px solid #1A1A1A;">
                    <span style="color:#1A1A1A;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;">Fecha</span><br/>
                    <span style="font-size:16px;font-weight:700;color:#ED008C;">13 de Diciembre, 2026</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:16px 20px;border-bottom:2px solid #1A1A1A;">
                    <span style="color:#1A1A1A;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;">Lugar</span><br/>
                    <span style="font-size:16px;font-weight:700;">Próximamente</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:16px 20px;">
                    <span style="color:#1A1A1A;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;">Precio</span><br/>
                    <span style="font-size:16px;font-weight:700;color:#13D010;">RD$600 Pesos Dominicanos</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer Inside Card -->
          <tr>
            <td style="background:#F9F4E0;border-top:3px solid #1A1A1A;padding:24px;text-align:center;">
              <p style="margin:0;color:#666666;font-size:12px;line-height:1.5;font-weight:600;">
                Este enlace es personal. No lo compartas con nadie.<br/>
                Onda Fest 2026 - Grupo Religioso Onda
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
    logo_url = f"{frontend_url}/img/LOGO%20VERSI%20HORIZONTAL%201.png"
    icon_url = f"{frontend_url}/img/iconos/SUNGLASSES.png"

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Comprobante en Revisión — ENO 2026</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
  </style>
</head>
<body style="margin:0;padding:0;background:#F9F4E0;font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1A1A1A;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;padding:40px 10px;">
    <tr>
      <td align="center">
        <!-- Logo -->
        <a href="{frontend_url}" style="display:inline-block;margin-bottom:20px;">
            <img src="{logo_url}" alt="Onda Fest Logo" style="height:50px;display:block;border:0;" />
        </a>

        <!-- Main Card -->
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;border:3px solid #1A1A1A;box-shadow:6px 6px 0px #1A1A1A;">
          <!-- Header -->
          <tr>
            <td style="background:#FF7D04;padding:40px 20px;text-align:center;border-bottom:3px solid #1A1A1A;">
              <h1 style="margin:0;color:#1A1A1A;font-size:32px;font-family:'Syne',Arial,sans-serif;font-weight:800;letter-spacing:-1px;text-transform:uppercase;">Comprobante Recibido</h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px 30px;text-align:center;">
              <h2 style="margin:0 0 16px;color:#1A1A1A;font-size:24px;font-family:'Syne',Arial,sans-serif;font-weight:800;">¡Hola {nombre}! 😎</h2>
              <p style="margin:0 0 32px;font-size:16px;line-height:1.6;color:#333333;font-weight:500;">
                Tu comprobante de pago está en nuestras manos. Nuestro equipo lo está verificando en este momento.<br/><br/>
                Recibirás otro correo muy pronto cuando el estado se actualice a <strong>Verificado</strong> o si hay algún problema.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:#FEB004;border-radius:10px;border:3px solid #1A1A1A;box-shadow:4px 4px 0px #1A1A1A;text-align:center;">
                    <a href="{frontend_url}/verificar.html"
                       style="display:block;padding:16px 32px;color:#1A1A1A;font-size:16px;font-weight:800;text-decoration:none;text-transform:uppercase;letter-spacing:0.5px;font-family:'Syne',Arial,sans-serif;">
                      Ver Mi Portal
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#F9F4E0;border-top:3px solid #1A1A1A;padding:24px;text-align:center;">
              <p style="margin:0;color:#666666;font-size:12px;line-height:1.5;font-weight:600;">
                Onda Fest 2026 - Grupo Religioso Onda
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

def _build_payment_status_email(nombre: str, status: str, frontend_url: str) -> str:
    """Construye el HTML del correo de cambio de estado de pago."""
    logo_url = f"{frontend_url}/img/LOGO%20VERSI%20HORIZONTAL%201.png"
    
    if status == "verificado":
        bg_color = "#3CE705" # verde neobrutalista
        text_color = "#1A1A1A"
        titulo = "¡PAGO VERIFICADO!"
        subtitulo = "Cupo Asegurado"
        mensaje = f"Buenas noticias, <strong>{nombre}</strong>. Hemos verificado tu pago exitosamente. ¡Tu cupo en Onda Fest 2026 está totalmente asegurado! 🎉"
    else:
        bg_color = "#FF0000" # rojo neobrutalista
        text_color = "#FFFFFF"
        titulo = "PROBLEMA CON PAGO"
        subtitulo = "Acción Requerida"
        mensaje = f"Hola <strong>{nombre}</strong>, revisamos tu comprobante pero ha sido <strong>RECHAZADO</strong>. Por favor, entra a tu portal para subir uno válido o contacta a soporte."

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Actualización de Pago — ENO 2026</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
  </style>
</head>
<body style="margin:0;padding:0;background:#F9F4E0;font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1A1A1A;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F4E0;padding:40px 10px;">
    <tr>
      <td align="center">
        <!-- Logo -->
        <a href="{frontend_url}" style="display:inline-block;margin-bottom:20px;">
            <img src="{logo_url}" alt="Onda Fest Logo" style="height:50px;display:block;border:0;" />
        </a>

        <!-- Main Card -->
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;border:3px solid #1A1A1A;box-shadow:6px 6px 0px #1A1A1A;">
          <!-- Header -->
          <tr>
            <td style="background:{bg_color};padding:40px 20px;text-align:center;border-bottom:3px solid #1A1A1A;">
              <h1 style="margin:0;color:{text_color};font-size:34px;font-family:'Syne',Arial,sans-serif;font-weight:800;letter-spacing:-1px;text-transform:uppercase;">{titulo}</h1>
              <p style="margin:8px 0 0;color:{text_color};font-size:14px;letter-spacing:2px;text-transform:uppercase;font-weight:800;">{subtitulo}</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px 30px;text-align:center;">
              <p style="margin:0 0 32px;font-size:16px;line-height:1.6;color:#333333;font-weight:500;">
                {mensaje}
              </p>
              
              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="background:#FEB004;border-radius:10px;border:3px solid #1A1A1A;box-shadow:4px 4px 0px #1A1A1A;text-align:center;">
                    <a href="{frontend_url}/verificar.html"
                       style="display:block;padding:16px 32px;color:#1A1A1A;font-size:16px;font-weight:800;text-decoration:none;text-transform:uppercase;letter-spacing:0.5px;font-family:'Syne',Arial,sans-serif;">
                      Ir a Mi Portal
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#F9F4E0;border-top:3px solid #1A1A1A;padding:24px;text-align:center;">
              <p style="margin:0;color:#666666;font-size:12px;line-height:1.5;font-weight:600;">
                Onda Fest 2026 - Grupo Religioso Onda
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
        "sender": {"name": "Onda Fest 2026", "email": settings.BREVO_FROM_EMAIL},
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
    return _send_brevo_email(to_email, "Registro Exitoso - Onda Fest 2026", html_body, nombre)

def send_receipt_uploaded_email(to_email: str, nombre: str) -> bool:
    html_body = _build_receipt_uploaded_email(nombre, settings.FRONTEND_URL)
    return _send_brevo_email(to_email, "Comprobante Recibido - Onda Fest 2026", html_body, nombre)

def send_payment_status_email(to_email: str, nombre: str, status: str) -> bool:
    subject = "¡Pago Verificado! - Onda Fest 2026" if status.lower() == "verificado" else "Problema con tu pago - Onda Fest 2026"
    html_body = _build_payment_status_email(nombre, status, settings.FRONTEND_URL)
    return _send_brevo_email(to_email, subject, html_body, nombre)
