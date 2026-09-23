from brevo import Brevo
from config import config
from brevo.transactional_emails import (SendTransacEmailRequestSender, SendTransacEmailRequestToItem)

def send_verification_email(email, subject, html):
    client = Brevo(api_key=config["BREVO_API_KEY"])

    client.transactional_emails.send_transac_email(
        subject=subject,
        html_content=html,
        name=config["MAIL_FROM_TITLE"],
        email=config["MAIL_FROM"],
        to=[SendTransacEmailRequestToItem(email=email)]
    )