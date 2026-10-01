
def _build_receipt_uploaded_email(nombre: str, frontend_url: str) -> str:
    dashboard_url = f"{frontend_url}/dashboard.html"
    return f"""<!DOCTYPE html>
<html lang="es">
<body style="font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1a1a1a;background:#F9F4E0;padding:40px 0;">
  <div style="max-width:600px;margin:0 auto;background:#fff;padding:40px;border-radius:16px;border:2px solid #FF0000;text-align:center;">
    <h1 style="color:#FF0000;font-size:24px;">¡Comprobante Recibido, {nombre}!</h1>
    <p style="font-size:16px;line-height:1.6;color:#333;">Hemos recibido tu comprobante de pago con éxito. Nuestro equipo de administración lo estará validando en las próximas 24 a 48 horas.</p>
    <p style="font-size:16px;line-height:1.6;color:#333;">Te enviaremos otro correo cuando tu estado cambie, o puedes revisar el estado actual en tu portal en cualquier momento.</p>
    <a href="{dashboard_url}" style="display:inline-block;padding:16px 40px;background:#FEB004;color:#1a1a1a;font-weight:bold;text-decoration:none;border-radius:12px;margin-top:20px;">IR AL PORTAL</a>
  </div>
</body>
</html>"""

def _build_payment_status_email(nombre: str, status: str, frontend_url: str) -> str:
    dashboard_url = f"{frontend_url}/dashboard.html"
    if status.lower() == "verificado":
        title = "¡Tu pago ha sido Verificado!"
        color = "#10B981"
        msg = "Felicidades, hemos verificado tu pago y tu inscripción al evento está 100% confirmada. ¡Nos vemos en Onda Fest 2026!"
    else:
        title = "Inconveniente con tu comprobante"
        color = "#EF4444"
        msg = "Hemos revisado tu comprobante y lamentablemente ha sido <strong>Rechazado</strong>. Por favor, ingresa a tu portal para subir un nuevo comprobante válido."

    return f"""<!DOCTYPE html>
<html lang="es">
<body style="font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#1a1a1a;background:#F9F4E0;padding:40px 0;">
  <div style="max-width:600px;margin:0 auto;background:#fff;padding:40px;border-radius:16px;border:2px solid {color};text-align:center;">
    <h1 style="color:{color};font-size:24px;">{title}</h1>
    <p style="font-size:16px;line-height:1.6;color:#333;">Hola {nombre},</p>
    <p style="font-size:16px;line-height:1.6;color:#333;">{msg}</p>
    <a href="{dashboard_url}" style="display:inline-block;padding:16px 40px;background:#FEB004;color:#1a1a1a;font-weight:bold;text-decoration:none;border-radius:12px;margin-top:20px;">IR AL PORTAL</a>
  </div>
</body>
</html>"""

def send_receipt_uploaded_email(to_email: str, nombre: str) -> bool:
    if not settings.RESEND_API_KEY:
        return False
    try:
        resend.api_key = settings.RESEND_API_KEY
        params: resend.Emails.SendParams = {
            "from": f"ENO 2026 <{settings.RESEND_FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Tu comprobante está en revisión",
            "html": _build_receipt_uploaded_email(nombre, settings.FRONTEND_URL),
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Error: {e}")
        return False

def send_payment_status_email(to_email: str, nombre: str, status: str) -> bool:
    if not settings.RESEND_API_KEY:
        return False
    try:
        resend.api_key = settings.RESEND_API_KEY
        subject = "¡Pago Verificado! - ENO 2026" if status.lower() == "verificado" else "Atención con tu pago - ENO 2026"
        params: resend.Emails.SendParams = {
            "from": f"ENO 2026 <{settings.RESEND_FROM_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": _build_payment_status_email(nombre, status, settings.FRONTEND_URL),
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Error: {e}")
        return False
