import requests
import settings
import yagmail


def check_gateways():

    url = 'https://core.spreedly.com/v1/gateways.json'
    headers = {'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
               'Content-Type': 'application/json',}
    params = {'order': 'desc',}

    r = requests.get(url=url, headers=headers, params=params)

    if r.ok:
        gateways = r.json()['gateways']
        if len(gateways) > 0:
            for count, g in enumerate(gateways):
                if not g['redacted']:
                    # unprovision the gateway
                    url = 'https://core.spreedly.com/v1/gateways/{}/redact.json'.format(g['token'])
                    r = requests.put(url=url, headers=headers)
                    if r.ok:
                        text = "Successfully redacted gateway {} with token {}.\n" \
                               "JSON response from Spreedly follows:\n\n".format(count, g['token'])
                        t = r.json()
                        print(t['transaction'])
                        send_email(text + ' ' + str(t['transaction']))
                    else:
                        print("Failed to redact gateway {} with token {}".format(count, g['token']))
                else:
                    print("Gateway {} with token {} already redacted".format(count, g['token']))
        else:
            print("No gateways defined.\n")
    else:
        print("Invalid Spreedly request attempting to list gateways.\n")

def send_email(text):
    """Send an email"""
    yag = yagmail.SMTP(user=settings.EMAIL_SOURCE_CONFIG[0], password=settings.EMAIL_SOURCE_CONFIG[1],
                       host=settings.EMAIL_SOURCE_CONFIG[2], port=settings.EMAIL_SOURCE_CONFIG[3],
                       smtp_starttls=False, smtp_skip_login=True)

    yag.send(settings.EMAIL_TARGETS[0], 'Spreedly gateway BREACHED!', text)

if __name__ == '__main__':
    check_gateways()
