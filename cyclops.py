import time

from raven import Client

from cyclops.cyclops import check
import settings

sentry = Client(settings.SENTRY_DSN)

if __name__ == "__main__":
    try:
        while True:
            try:
                check()
            except Exception:
                sentry.captureException()
            finally:
                time.sleep(60)
    except KeyboardInterrupt:
        pass
