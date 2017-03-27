from environment import env_var, read_env
import os


read_env()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = env_var('CYCLOPS_DEBUG', False)

# user name
KEY = env_var('CYCLOPS_KEY', 'Yc7xn3gDP73PPOQLEB2BYpv31EV')

# password
ACCESS_SECRET = env_var('CYCLOPS_ACCESS_SECRET', '4m8tVKWHvakjhfBXnRVDbfkOArB9NvAyo9U6lWtVulb2thuI6T439blRbQWGwQcH')

# This AUTH_KEY is the interpreted key based on the ACCESS_SECRET and KEY above
AUTH_KEY = env_var('CYCLOPS_AUTH_KEY', 'WWM3eG4zZ0RQNzNQUE9RTEVCMkJZcHYzMUVWOjRtOHRWS1dIdmFramhmQlhuUlZEYmZrT0FyQj' \
                                       'lOdkF5bzlVNmxXdFZ1bGIydGh1STZUNDM5YmxSYlFXR3dRY0g=')

EMAIL_SOURCE_CONFIG = [
    # user | password | host | port
    env_var('EMAIL_USER', 'noreply@bink.com'), env_var('EMAIL_PASSWORD', 'Gibbon^egg^Change^^'),
    env_var('EMAIL_HOST', 'mail.bink.com'), env_var('EMAIL_PORT', 587), # 'smtp.office365.com', 587,
]

EMAIL_TARGETS = [env_var('EMAIL_TARGET', 'oe@bink.com, ml@bink.com, pb@bink.com'),]

