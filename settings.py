from environment import env_var, read_env
import os


read_env()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = env_var('CYCLOPS_DEBUG', False)

# This AUTH_KEY is the interpreted key based on the ACCESS_SECRET and KEY above
AUTH_KEY = env_var('CYCLOPS_AUTH_KEY', 'MUxmN0RpS2drY3g1QW53N1F4V2REeGFLdFRhOjRtOHRWS1dIdmFramhmQlhuUlZEYm'
                                       'ZrT0FyQjlOdkF5bzlVNmxXdFZ1bGIydGh1STZUNDM5YmxSYlFXR3dRY0g=')

EMAIL_SOURCE_CONFIG = [
    # user | password | host | port
    env_var('EMAIL_USER', 'oe@bink.com'), env_var('EMAIL_PASSWORD', 'BINK*2016@HOME'),
    # 'noreply@bink.com', 'Gibbon^egg^Change^^'),
    env_var('EMAIL_HOST', 'smtp.office365.com'), env_var('EMAIL_PORT', 587),
]

EMAIL_TARGETS = env_var('EMAIL_TARGET', 'oe@bink.com, pb@bink.com, ml@bink.com', )

SLACK_API_TOKEN = 'xoxb-119487439522-Lsefc6ykOx3RIXC89WN8wx3h'
