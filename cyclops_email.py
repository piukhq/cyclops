import smtplib
import email.utils
from email.mime.text import MIMEText
import settings


def send_email(text):
    to_email = settings.EMAIL_TARGETS
    servername = settings.EMAIL_SOURCE_CONFIG[2]
    username = settings.EMAIL_SOURCE_CONFIG[0]
    password = settings.EMAIL_SOURCE_CONFIG[1]
    port = settings.EMAIL_SOURCE_CONFIG[3]

    # Create the message
    msg = MIMEText(text)
    msg['To'] = ", ".join(to_email)
    msg['From'] = username
    msg['Subject'] = 'Spreedly gateway BREACHED!'

    server = smtplib.SMTP(host=servername, port=port)
    try:
        server.set_debuglevel(True)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection

        server.login(username, password)
        server.sendmail(settings.EMAIL_SOURCE_CONFIG[0], to_email, msg.as_string())
    finally:
        server.quit()
