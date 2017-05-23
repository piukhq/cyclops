import logging
import time

import requests
import arrow

from cyclops.slack import payment_card_notify
from cyclops.email import send_email
from cyclops import settings


logging.basicConfig(level=logging.INFO)

SPREEDLY_PAGE_SIZE = 20


def spreedly_endpoint(endpoint):
    return '{}{}'.format(settings.SPREEDLY_BASE_URL, endpoint)


def get_gateways(since_token=None):
    url = spreedly_endpoint('/v1/gateways.json')
    headers = {
        'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
        'Content-Type': 'application/json'
    }
    params = {
        'order': 'desc'
    }
    if since_token:
        params['since_token'] = since_token

    resp = requests.get(url=url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()['gateways']


def get_all_gateways():
    gateways = get_gateways()
    while True:
        if arrow.get(gateways[-1]['created_at']) < arrow.now().replace(days=-7):
            break

        if len(gateways) != SPREEDLY_PAGE_SIZE:
            break

        time.sleep(1)
        token = gateways[-1]['token']
        gateways.extend(get_gateways(since_token=token))
    return gateways


def redact(gateways):
    url = spreedly_endpoint('/v1/gateways/{}/redact.json')
    headers = {
        'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
        'Content-Type': 'application/json'
    }

    responses = []
    for gateway in gateways:
        try:
            resp = requests.put(
                url=url.format(gateway['token']),
                headers=headers)
            responses.append(resp)
            resp.raise_for_status()
            logging.info('Requested to redact gateway {}. Response: {}'.format(gateway['token'], resp.json()))
        except Exception as e:
            logging.error('Failed to redact gateway {} with error: {}'.format(gateway['token'], e))
    return responses


def notify(gateways, responses):
    message_parts = []
    for gateway, response in zip(gateways, responses):
        url = spreedly_endpoint('/v1/gateways/{}/transactions.json'.format(gateway['token']))
        headers = {
            'Authorization': 'Basic {}'.format(settings.AUTH_KEY),
            'Content-Type': 'application/json'
        }
        resp = requests.get(url=url, headers=headers, params={'order': 'desc'})

        try:
            resp.raise_for_status()
            transactions = resp.json()['transactions']
            if transactions:
                transaction_message = repr(transactions)
            else:
                transaction_message = 'No transactions to retrieve.'
        except:
            transaction_message = 'Failed to retrieve transactions.'

        lines = ('Successfully redacted gateway with token {}.'.format(gateway['token']),
                 '',
                 'Redacted gateway transaction: {}'.format(response.json()),
                 '',
                 'Transactions: (paginated, most recent first)...',
                 '',
                 'Transactions for gateway with token {} follow:'.format(gateway['token']),
                 transaction_message)

        message_parts.append('\n'.join(lines))
    send_email('\n\n---\n\n'.join(message_parts))
    payment_card_notify(
        'Spreedly gateway BREACHED! An email has been sent to {}'.format(', '.join(settings.EMAIL_TARGETS)))


def redact_and_notify(gateways):
    responses = redact(gateways)
    notify(gateways, responses=responses)


def check():
    requests.get(settings.HEALTHCHECK_URL)
    non_redacted_gateways = [g for g in get_all_gateways() if not g['redacted']]
    if non_redacted_gateways:
        redact_and_notify(non_redacted_gateways)
