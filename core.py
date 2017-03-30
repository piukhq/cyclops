import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import settings
from cyclops_email import send_email
from slack import payment_card_notify

sched = BlockingScheduler()

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
                    elif settings.DEBUG:
                        print("Failed to redact gateway {} with token {}".format(count, g['token']))
                elif settings.DEBUG:
                        print("Gateway {} with token {} already redacted".format(count, g['token']))
        elif settings.DEBUG:
            print("No gateways defined.\n")
    elif settings.DEBUG:
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


@sched.scheduled_job('interval', seconds=10)
def check_for_breach():
    redacted_gateways, total = check_gateways()

    if total > 0:
        transactions = get_transactions(headers, params)
        email_content = redacted_gateways + '\n' + transactions
        payment_card_notify("Spreedly gateway BREACHED!  Please check an email address "
                            "from the distribution list for details.")
        send_email(email_content)


if __name__ == '__main__':
    sched.start()
