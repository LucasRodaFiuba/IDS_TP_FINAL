import smtplib
from email.message import EmailMessage
import os
from ..constantes import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

def enviar_mail(destinatario, asunto, cuerpo, archivo_adjunto=None):
    #Creo email vacio
    msg = EmailMessage()

    #Defino datos importantes del gmail
    msg["Subject"] = asunto
    msg["From"] = "tuemail@gmail.com"
    msg["To"] = destinatario

    msg.set_content(cuerpo)

    # Adjunto el QR si el mismo existe
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

    #Envio el email
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)