from environment import env_var, read_env

read_env()

SPREEDLY_BASE_URL = 'https://core.spreedly.com'

AUTH_KEY = env_var('CYCLOPS_AUTH_KEY', 'MUxmN0RpS2drY3g1QW53N1F4V2REeGFLdFRhOjRtOHRWS1dIdmFramhmQlhuUlZEYm'
                                       'ZrT0FyQjlOdkF5bzlVNmxXdFZ1bGIydGh1STZUNDM5YmxSYlFXR3dRY0g=')

EMAIL_USERNAME = env_var('EMAIL_USERNAME', 'itapps@bink.com')
EMAIL_PASSWORD = env_var('EMAIL_PASSWORD', '$NickCisEcbeu1')
EMAIL_HOST = env_var('EMAIL_HOST', 'smtp.office365.com')
EMAIL_PORT = env_var('EMAIL_PORT', 587)

EMAIL_TARGETS = ['development@bink.com']

SLACK_API_TOKEN = 'xoxb-119487439522-Lsefc6ykOx3RIXC89WN8wx3h'

SENTRY_DSN = env_var('CYCLOPS_SENTRY_DSN',
                     ('https://ac61a7968c43427c90542ffff74d5f1f:6d26fffe2d9c4c79bd28204899229d6f'
                      '@sentry.loyaltyangels.com:8999/17'))

HEALTHCHECK_URL = env_var('HEALTHCHECK_URL', 'https://hchk.io/92429b19-1ea5-4f45-8abf-ee93c943ac39')
