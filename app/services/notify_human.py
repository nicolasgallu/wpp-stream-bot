import smtplib
import ast
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.logger import logger
from app.config.config import SENDER_EMAIL,SENDER_PASSWORD,RECIPIENT_EMAIL

def notify_human(subject, chat):
    """Envía un correo con los detalles de la conversación en formato estructurado."""

    chat = ast.literal_eval(chat)
    
    lines = []
    for timestamp, message, sender in chat:
        emoji = "🤖" if sender.lower() == "bot" else "👤"
        line = f"[{timestamp}] {emoji} {sender}: {message}"
        lines.append(line)

    email_body = "\n".join(lines)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
 

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(email_body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logger.info("Chat Email send it correctly.")
    except Exception as e:
        logger.error(f"Error sending Chat Email: {e}")
