import logging
import time

import requests
import arrow

from cyclops.slack import payment_card_notify
from cyclops.email import send_email
import settings


logging.basicConfig(level=logging.INFO)

SPREEDLY_PAGE_SIZE = 20


def spreedly_endpoint(endpoint):
    return f"{settings.SPREEDLY_BASE_URL}{endpoint}"


def get_gateways(since_token=None):
    url = spreedly_endpoint("/v1/gateways.json")
    headers = {
        "Authorization": f"Basic {settings.AUTH_KEY}",
        "Content-Type": "application/json",
    }
    params = {"order": "desc"}
    if since_token:
        params["since_token"] = since_token

    resp = requests.get(url=url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()["gateways"]


def get_all_gateways():
    gateways = get_gateways()
    while True:
        if arrow.get(gateways[-1]["created_at"]) < arrow.now().replace(
            days=-7
        ):
            break

        if len(gateways) != SPREEDLY_PAGE_SIZE:
            break

        time.sleep(1)
        token = gateways[-1]["token"]
        gateways.extend(get_gateways(since_token=token))
    return gateways


def redact(gateways):
    url = spreedly_endpoint("/v1/gateways/{}/redact.json")
    headers = {
        "Authorization": f"Basic {settings.AUTH_KEY}",
        "Content-Type": "application/json",
    }

    responses = []
    for gateway in gateways:
        try:
            resp = requests.put(
                url=url.format(gateway["token"]), headers=headers
            )
            responses.append(resp)
            resp.raise_for_status()
            logging.info(
                f"Requested to redact gateway {gateway['token']}. Response: {resp.json()}"
            )
        except Exception as e:
            logging.error(
                f"Failed to redact gateway {gateway['token']} with error: {e}"
            )
    return responses


def notify(gateways, responses):
    message_parts = []
    for gateway, response in zip(gateways, responses):
        url = spreedly_endpoint(
            f"/v1/gateways/{gateway['token']}/transactions.json"
        )
        headers = {
            f"Authorization": "Basic {settings.AUTH_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.get(url=url, headers=headers, params={"order": "desc"})

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
    send_email("\n\n---\n\n".join(message_parts))
    payment_card_notify(
        f"Spreedly gateway BREACHED! An email has been sent to {', '.join(settings.EMAIL_TARGETS)}"
    )


def redact_and_notify(gateways):
    responses = redact(gateways)
    notify(gateways, responses=responses)


def check():
    requests.get(settings.HEALTHCHECK_URL)
    non_redacted_gateways = [
        g for g in get_all_gateways() if not g["redacted"]
    ]
    if non_redacted_gateways:
        redact_and_notify(non_redacted_gateways)
