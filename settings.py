import sentry_sdk

from environment import env_var, read_env

read_env()

SPREEDLY_BASE_URL = "https://core.spreedly.com"

AUTH_KEY = env_var("CYCLOPS_AUTH_KEY")

EMAIL_USERNAME = env_var("EMAIL_USERNAME")
EMAIL_PASSWORD = env_var("EMAIL_PASSWORD")
EMAIL_HOST = env_var("EMAIL_HOST")
EMAIL_PORT = env_var("EMAIL_PORT")

EMAIL_TARGETS = ["development@bink.com"]

SLACK_API_TOKEN = env_var("SLACK_API_TOKEN")

SENTRY_DSN = env_var("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN)

HEALTHCHECK_URL = env_var("HEALTHCHECK_URL")
