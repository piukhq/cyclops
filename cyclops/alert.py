from settings import MAILGUN_API, MAILGUN_TARGET, MAILGUN_SENDER, MAILGUN_API_KEY, OPSGENIE_API_KEY, OPSGENIE_URL, TEAMS_WEBHOOK, XMATTERS_WEBHOOK
from cyclops.requests_retry import requests_retry_session
from requests.auth import HTTPBasicAuth
import logging


def microsoft_teams(message):
    try:
        session = requests_retry_session()
        template = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF2D00",
            "summary": "Cyclops Event Notification",
            "Sections": [
                {
                    "activityTitle": "Cyclops Event Notification",
                    "facts": [{"name": "Message", "value": message}],
                    "markdown": False,
                }
            ],
        }
        session.post(TEAMS_WEBHOOK, json=template)
    except Exception:
        logging.exception("Microsoft Teams Request Failed")
        pass


def mailgun(message):
    try:
        session = requests_retry_session()
        session.post(
            MAILGUN_API,
            auth=HTTPBasicAuth("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_SENDER,
                "to": MAILGUN_TARGET,
                "subject": "Spreedly gateway BREACHED!",
                "text": message,
            },
        )
    except Exception:
        logging.exception("Mailgun Request Failed")
        pass


def xmatters(message):
    try:
        session = requests_retry_session()
        session.post(XMATTERS_WEBHOOK, json={"message": message})
    except Exception:
        logging.exception("xMatters Request Failed")
        pass


def opsgenie(message):
    try:
        session = requests_retry_session()
        session.post(
            OPSGENIE_URL,
            auth=HTTPBasicAuth('GenieKey', OPSGENIE_API_KEY),
            data={
                "message": message
            }
        )
    except Exception:
        logging.exception("Opsgenie Request Failed")
        pass

def alert(message):
    microsoft_teams(message)
    mailgun(message)
    xmatters(message)
    opsgenie(message)
