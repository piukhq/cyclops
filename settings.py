import sentry_sdk

from environment import env_var, read_env

read_env()

SPREEDLY_BASE_URL = "https://core.spreedly.com"

AUTH_KEY = env_var("CYCLOPS_AUTH_KEY")

MAILGUN_API_KEY = env_var("MAILGUN_API_KEY", "key-63iepgmkm8qdzs0fxm05jy0oq3c1yd42")
MAILGUN_SENDER = env_var("MAILGUN_SENDER", "support@uk.bink.com")
MAILGUN_API = env_var("MAILGUN_URL", "https://api.mailgun.net/v3/uk.bink.com/messages")
MAILGUN_TARGET = env_var("MAILGUN_TARGET", "cyclops@bink.com")

TEAMS_WEBHOOK = env_var(
    "TEAMS_WEBHOOK",
    "https://outlook.office.com/webhook/bf220ac8-d509-474f-a568-148982784d19@a6e2367a-92ea-4e5a-b565-723830bcc095/IncomingWebhook/5931605317444706be22208c6f394f4c/48aca6b1-4d56-4a15-bc92-8aa9d97300df",  # noqa: E501
)

XMATTERS_WEBHOOK = env_var(
    "XMATTERS_WEBHOOK",
    "https://bink.xmatters.com/api/integration/1/functions/83fd7b90-28c5-4323-8ebb-a6010c976634/triggers?apiKey=78c63de7-1ab8-4cf0-80d3-745755fe30b2",  # noqa: E501
)

SENTRY_DSN = env_var("SENTRY_DSN")
SENTRY_ENV = env_var("SENTRY_ENV")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, environment=SENTRY_ENV)

HEALTHCHECK_URL = env_var("HEALTHCHECK_URL", "https://hchk.io/92429b19-1ea5-4f45-8abf-ee93c943ac39")
