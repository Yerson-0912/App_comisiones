"""
Funciones para enviar emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de email (cambiar antes de producción)
EMAIL_SENDER = 'noreply@comisiones.com'
EMAIL_PASSWORD = 'tu_contraseña_aqui'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def enviar_email(destinatario, asunto, cuerpo_html, cuerpo_texto=None):
    """
    Envía un email
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        cuerpo_html: Cuerpo en HTML
        cuerpo_texto: Cuerpo en texto plano (opcional)
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = EMAIL_SENDER
        msg['To'] = destinatario
        
        if cuerpo_texto:
            msg.attach(MIMEText(cuerpo_texto, 'plain'))
        msg.attach(MIMEText(cuerpo_html, 'html'))
        
        # Nota: Para desarrollo, usa credenciales de Gmail con contraseña de app
        # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # server.starttls()
        # server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        # server.sendmail(EMAIL_SENDER, destinatario, msg.as_string())
        # server.quit()
        
        # Por ahora, simular envío
        print(f'EMAIL SIMULADO: Enviado a {destinatario}')
        print(f'Asunto: {asunto}')
        return True
        
    except Exception as e:
        print(f'Error al enviar email: {str(e)}')
        return False

def enviar_email_recuperacion(email, username, token, link_base='http://localhost:5000'):
    """Envía email de recuperación de contraseña"""
    link_recuperacion = f"{link_base}/recuperar-contraseña?email={email}&token={token}"
    
    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px;">
            <div style="background: white; border-radius: 8px; padding: 30px; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #1d4ed8;">Panel de Comisiones</h2>
                <p>Hola <strong>{username}</strong>,</p>
                <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva contraseña.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link_recuperacion}" style="background: #1d4ed8; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Restablecer Contraseña</a>
                </div>
                <p style="color: #64748b; font-size: 12px;">Este enlace expira en 1 hora. Si no solicitaste restablecer tu contraseña, ignora este email.</p>
                <p style="color: #64748b; font-size: 12px; margin-top: 20px;">© 2026 Panel de Comisiones</p>
            </div>
        </body>
    </html>
    """
    
    cuerpo_texto = f"""
    Panel de Comisiones
    
    Hola {username},
    
    Recibimos una solicitud para restablecer tu contraseña. Haz clic en el enlace de abajo para crear una nueva contraseña.
    
    {link_recuperacion}
    
    Este enlace expira en 1 hora. Si no solicitaste restablecer tu contraseña, ignora este email.
    
    © 2026 Panel de Comisiones
    """
    
    return enviar_email(email, 'Restablecer contraseña - Panel de Comisiones', cuerpo_html, cuerpo_texto)
