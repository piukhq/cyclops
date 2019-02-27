import time

import sentry_sdk

from cyclops.cyclops import check

if __name__ == "__main__":
    try:
        while True:
            try:
                check()
            except Exception:
                sentry_sdk.capture_exception()
            finally:
                time.sleep(60)
    except KeyboardInterrupt:
        pass
