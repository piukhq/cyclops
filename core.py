import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import settings
from cyclops_email import send_email
from slack import payment_card_notify
import arrow

sched = BlockingScheduler()

headers = {'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
           'Content-Type': 'application/json', }

params = {'order': 'desc', }

def redact_gateway(output_text, total, g):
    # get all transactions for this gateway based on it's token
    transactions = get_gateway_transactions(headers, params, g['token'])

    # unprovision the gateway
    url = 'https://core.spreedly.com/v1/gateways/{}/redact.json'.format(g['token'])
    r = requests.put(url=url, headers=headers)
    if r.ok:
        text = "Successfully redacted gateway with token {}.\n\n".format(g['token'])
        t = r.json()

        redacted_gateways = text + 'Redacted gateway transaction: ' + str(t['transaction']) + '\n\n'
        total += 1

        output_text += redacted_gateways
        if len(transactions):
            output_text += 'Transactions: (paginated, most recent first)' \
                           '...\n\n' + transactions
        else:
            output_text += 'No transactions occurred with this gateway.\n\n'
    elif settings.DEBUG:
        print("Failed to redact gateway with token {}".format(g['token']))

    return output_text, total


def handle_redactions(gateways, output_text, total):
    token = ''
    if len(gateways) > 0:
        for count, g in enumerate(gateways):
            if not g['redacted']:
                include_output_in_email = False
                ca = g['created_at']  # Format looks like: 2017-03-16T18:14:11Z
                timestamp = arrow.get(int(ca[:4]), int(ca[5:7]), int(ca[8:10]),
                                      int(ca[11:13]), int(ca[14:16]), int(ca[17:19]))
                now_minus_two_mins = arrow.utcnow().replace(minutes=-2)
                if timestamp > now_minus_two_mins:
                    include_output_in_email = True
                output, total = redact_gateway(output_text, total, g)
                if include_output_in_email:
                    output_text = output
            elif settings.DEBUG:
                print("Gateway with token {} already redacted".format(g['token']))
            token = g['token']
    elif settings.DEBUG:
        print("No gateways defined.\n")

    return output_text, total, token


def check_gateways():
    url = 'https://core.spreedly.com/v1/gateways.json'
    list_gateways_params = {'order': 'desc', }

    r = requests.get(url=url, headers=headers, params=list_gateways_params)

    total = 0
    output_text = ''

    if r.ok:
        gateways = r.json()['gateways']
        output_text, total, token = handle_redactions(gateways, output_text, total)
        while len(gateways) == 20:
            list_gateways_params['since_token'] = token
            r = requests.get(url=url, headers=headers, params=list_gateways_params)
            if r.ok:
                gateways = r.json()['gateways']
                output_text, total, token = handle_redactions(gateways, output_text, total)

    elif settings.DEBUG:
        print("Invalid Spreedly request attempting to list gateways.\n")

    return output_text, total


def get_gateway_transactions(headers, params, token):
    url = 'https://core.spreedly.com/v1/{}/transactions.json'.format(token)
    r = requests.get(url=url, headers=headers, params=params)
    transactions = 'Transactions for gateway with token {} follow:\n'.format(token)
    if r.ok:
        j = r.json()
        for transaction in j['transactions']:
            transactions += str(transaction) + '\n\n'
    else:
        transactions += "No transactions to retrieve.\n\n"

    return transactions


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
    email_text, total = check_gateways()

    if total > 0 and len(email_text):
        payment_card_notify("Spreedly gateway BREACHED!  Please check an email address "
                            "from the cyclops distribution list for details.")
        send_email(email_text)


if __name__ == '__main__':
    sched.start()
