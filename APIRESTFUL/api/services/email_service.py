import smtplib
from email.message import EmailMessage
import os

def enviar_mail(destinatario, asunto, cuerpo, archivo_adjunto=None):
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = "tuemail@gmail.com"
    msg["To"] = destinatario

    msg.set_content(cuerpo)

    # Adjuntar QR si existe
    if archivo_adjunto:
        with open(archivo_adjunto, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(archivo_adjunto)

        msg.add_attachment(
            file_data,
            maintype="image",
            subtype="png",
            filename=file_name
        )

    # SMTP Gmail (ejemplo)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("noreply.reservas.app@gmail.com", "dqtt pwep ymnu lrii ")
        smtp.send_message(msg)