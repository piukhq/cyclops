from email.mime.text import MIMEText
import smtplib

import settings


def send_email(text):
    to_email = settings.EMAIL_TARGETS
    servername = settings.EMAIL_HOST
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    port = int(settings.EMAIL_PORT)

    # Create the message
    msg = MIMEText(text)
    msg["To"] = ", ".join(to_email)
    msg["From"] = username
    msg["Subject"] = "Spreedly gateway BREACHED!"

    server = smtplib.SMTP(host=servername, port=port)
    try:
        server.set_debuglevel(True)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection

        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())
    finally:
        server.quit()
