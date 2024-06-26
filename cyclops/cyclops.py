import logging
import time

import arrow

from cyclops.requests_retry import requests_retry_session
from cyclops.alert import alert
import settings


logging.basicConfig(level=logging.INFO)

SPREEDLY_PAGE_SIZE = 20

TOKEN_WHITELIST = ["D5lARug9NzuUfrFNkbeiWYSdHtx", "EK2Lv2jRNN2AVXjtso5V5fyv4lv"]


def get_gateways(since_token=None):
    session = requests_retry_session()
    url = f"{settings.SPREEDLY_BASE_URL}/v1/gateways.json"
    headers = {
        "Authorization": f"Basic {settings.SPREEDLY_AUTH}",
        "Content-Type": "application/json",
    }
    params = {"order": "desc"}
    if since_token:
        params["since_token"] = since_token

    resp = session.get(url=url, headers=headers, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()["gateways"]


def get_all_gateways():
    gateways = get_gateways()
    while True:
        if arrow.get(gateways[-1]["created_at"]) < arrow.now().shift(days=-7):
            break

        if len(gateways) != SPREEDLY_PAGE_SIZE:
            break

        time.sleep(1)
        token = gateways[-1]["token"]
        gateways.extend(get_gateways(since_token=token))
    return gateways


def redact(gateways):
    session = requests_retry_session()
    headers = {
        "Authorization": f"Basic {settings.SPREEDLY_AUTH}",
        "Content-Type": "application/json",
    }

    responses = []
    for gateway in gateways:
        try:
            resp = session.put(
                url=f"{settings.SPREEDLY_BASE_URL}/v1/gateways/{gateway['token']}/redact.json",
                headers=headers,
                timeout=60,
            )
            responses.append(resp)
            resp.raise_for_status()
            logging.info(f"Requested to redact gateway {gateway['token']}. Response: {resp.json()}")
        except Exception as e:
            logging.error(f"Failed to redact gateway {gateway['token']} with error: {e}")
    return responses


def notify(gateways, responses):
    session = requests_retry_session()
    message_parts = []
    for gateway, response in zip(gateways, responses):
        url = f"{settings.SPREEDLY_BASE_URL}/v1/gateways/{gateway['token']}/transactions.json"
        headers = {
            "Authorization": f"Basic {settings.SPREEDLY_AUTH}",
            "Content-Type": "application/json",
        }
        resp = session.get(url=url, headers=headers, params={"order": "desc"}, timeout=60)

        try:
            resp.raise_for_status()
            transactions = resp.json()["transactions"]
            if transactions:
                transaction_message = repr(transactions)
            else:
                transaction_message = "No transactions to retrieve."
        except Exception:
            transaction_message = "Failed to retrieve transactions."

        lines = (
            f"Successfully redacted gateway with token {gateway['token']}.",
            "",
            f"Redacted gateway transaction: {response.json()}",
            "",
            "Transactions: (paginated, most recent first)...",
            "",
            f"Transactions for gateway with token {gateway['token']} follow:",
            transaction_message,
        )

        message_parts.append("\n".join(lines))
    alert("\n\n---\n\n".join(message_parts))


def redact_and_notify(gateways):
    responses = redact(gateways)
    notify(gateways, responses=responses)


def check():
    session = requests_retry_session()
    session.get(settings.HEALTHCHECK_URL, timeout=5)
    non_redacted_gateways = [g for g in get_all_gateways() if not g["redacted"]]
    non_whitelisted_gateways = [g for g in non_redacted_gateways if g["token"] not in TOKEN_WHITELIST]
    if non_whitelisted_gateways:
        redact_and_notify(non_whitelisted_gateways)
