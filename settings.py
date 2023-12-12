import base64
import json
from os import getenv, environ

import sentry_sdk
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

SPREEDLY_AUTH = None
MAILGUN_API_KEY = None
MAILGUN_API = None

if "KEYVAULT_URI" in environ:
    KEYVAULT_URI = getenv("KEYVAULT_URI")
    kvcredential = DefaultAzureCredential()
    kvclient = SecretClient(vault_url=KEYVAULT_URI, credential=kvcredential)

    SPREEDLY_USER = json.loads(kvclient.get_secret("spreedly-oAuthUsername").value)["value"]
    SPREEDLY_PASS = json.loads(kvclient.get_secret("spreedly-oAuthPassword").value)["value"]
    SPREEDLY_AUTH = base64.b64encode(f"{SPREEDLY_USER}:{SPREEDLY_PASS}".encode()).decode()

    MAILGUN = json.loads(kvclient.get_secret("mailgun").value)
    MAILGUN_API_KEY = MAILGUN["MAILGUN_API_KEY"]
    MAILGUN_API = f"{MAILGUN['MAILGUN_API']}/{MAILGUN['MAILGUN_DOMAIN']}/messages"


MAILGUN_SENDER = getenv("MAILGUN_SENDER", "itapps@bink.com")
MAILGUN_TARGET = getenv("MAILGUN_TARGET", "cyclops@bink.com")

SPREEDLY_BASE_URL = "https://core.spreedly.com"

TEAMS_WEBHOOK = getenv(
    "TEAMS_WEBHOOK",
    "https://hellobink.webhook.office.com/webhookb2/bf220ac8-d509-474f-a568-148982784d19@a6e2367a-92ea-4e5a-b565-723830bcc095/IncomingWebhook/5931605317444706be22208c6f394f4c/48aca6b1-4d56-4a15-bc92-8aa9d97300df",  # noqa: E501
)

XMATTERS_WEBHOOK = getenv(
    "XMATTERS_WEBHOOK",
    "https://bink.xmatters.com/api/integration/1/functions/83fd7b90-28c5-4323-8ebb-a6010c976634/triggers?apiKey=78c63de7-1ab8-4cf0-80d3-745755fe30b2",  # noqa: E501
)

sentry_sdk.init()

HEALTHCHECK_URL = getenv("HEALTHCHECK_URL", "https://ping.checklyhq.com/2b3ea388-58d5-439a-9310-dd01fefae469")
