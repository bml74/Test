import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.utils import (
    getDomain
)


load_dotenv()


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL_ADDRESS = os.getenv("SENDER_EMAIL_ADDRESS")


def sendEmail(subject, html_content, to_emails, from_email=SENDER_EMAIL_ADDRESS):
    try:
        BASE_DOMAIN = getDomain()
        message = Mail(from_email="bml74@georgetown.edu", to_emails="bml74@georgetown.edu", subject=subject, html_content=html_content)
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(response)
        print("Working")
    except Exception as e:
        print(e)
