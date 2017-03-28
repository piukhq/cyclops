import requests
import settings
import yagmail

headers = {'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
           'Content-Type': 'application/json', }
params = {'order': 'desc', }


def check_gateways():
    url = 'https://core.spreedly.com/v1/gateways.json'

    r = requests.get(url=url, headers=headers, params=params)

    redacted_gateways = ''
    total = 0

    if r.ok:
        gateways = r.json()['gateways']
        if len(gateways) > 0:

            for count, g in enumerate(gateways):
                if not g['redacted']:
                    # unprovision the gateway
                    url = 'https://core.spreedly.com/v1/gateways/{}/redact.json'.format(g['token'])
                    r = requests.put(url=url, headers=headers)
                    if r.ok:
                        text = "Successfully redacted gateway {} with token {}.\n\n".format(count, g['token'])
                        t = r.json()

                        redacted_gateways += text + 'Redacted gateway transaction: ' + str(t['transaction']) + '\n'
                        total += 1
                    else:
                        print("Failed to redact gateway {} with token {}".format(count, g['token']))
                else:
                    print("Gateway {} with token {} already redacted".format(count, g['token']))
        else:
            print("No gateways defined.\n")
    else:
        print("Invalid Spreedly request attempting to list gateways.\n")

    return redacted_gateways, total


def get_transactions(headers, params):
    url = 'https://core.spreedly.com/v1/transactions.json'
    r = requests.get(url=url, headers=headers, params=params)
    transactions = 'Transactions follow:\n'
    if r.ok:
        j = r.json()
        for transaction in j['transactions']:
            transactions += str(transaction) + '\n'
    else:
        transactions += "No transactions to retrieve."

    return transactions


def send_email(text):
    """Send an email"""
    yag = yagmail.SMTP(user=settings.EMAIL_SOURCE_CONFIG[0], password=settings.EMAIL_SOURCE_CONFIG[1],
                       host=settings.EMAIL_SOURCE_CONFIG[2], port=settings.EMAIL_SOURCE_CONFIG[3],
                       smtp_starttls=True, smtp_skip_login=False)

    yag.send(settings.EMAIL_TARGETS[0], 'Spreedly gateway BREACHED!', text)


if __name__ == '__main__':
    redacted_gateways, total = check_gateways()
    print(total)
    if total > 0:
        transactions = get_transactions(headers, params)
        email_content = redacted_gateways + '\n' + transactions
        send_email(email_content)
