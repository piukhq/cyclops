from unittest.mock import patch, MagicMock
from unittest import TestCase
import re

import responses

from cyclops.cyclops import redact, notify, get_gateways


def add_redact_route():
    responses.add(
        responses.PUT,
        re.compile("https://core.spreedly.com/v1/gateways/.*/redact\\.json"),
        body=b'{"status": "redact works"}',
        status=200,
        content_type="application/json",
    )


def add_transactions_route():
    responses.add(
        responses.GET,
        re.compile("https://core.spreedly.com/v1/gateways/.*/transactions\\.json"),
        body=b'{"transactions": [{"status": "transactions work"}]}',
        status=200,
        content_type="application/json",
    )


def add_transactions_empty_route():
    responses.add(
        responses.GET,
        re.compile("https://core.spreedly.com/v1/gateways/.*/transactions\\.json"),
        body=b'{"transactions": []}',
        status=200,
        content_type="application/json",
    )


def add_transactions_bad_request_route():
    responses.add(
        responses.GET,
        re.compile("https://core.spreedly.com/v1/gateways/.*/transactions\\.json"),
        body=b'{"status": "failure"}',
        status=400,
        content_type="application/json",
    )


def add_gateways_route():
    responses.add(
        responses.GET,
        "https://core.spreedly.com/v1/gateways.json",
        body=b'{"gateways": [{"status": "gateways work"}]}',
        status=200,
        content_type="application/json",
    )


class TestCyclops(TestCase):
    @responses.activate
    def test_redact(self):
        add_redact_route()
        responses = redact([{"token": "test"}])
        self.assertEqual(responses[0].json()["status"], "redact works")

    @responses.activate
    @patch("cyclops.cyclops.send_email")
    @patch("cyclops.cyclops.payment_card_notify")
    def test_notify(self, mock_payment_card_notify, mock_send_email):
        add_transactions_route()

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "transactions work"}

        notify([{"token": "test"}], [mock_response])

        mock_payment_card_notify.assert_called_once_with(
            "Spreedly gateway BREACHED! An email has been sent to development@bink.com"
        )

        mock_send_email.assert_called_once_with(
            "Successfully redacted gateway with token test.\n\nRedacted gateway "
            "transaction: {'status': 'transactions work'}\n\nTransactions: "
            "(paginated, most recent first)...\n\nTransactions for gateway with "
            "token test follow:\n[{'status': 'transactions work'}]"
        )

    @responses.activate
    @patch("cyclops.cyclops.send_email")
    @patch("cyclops.cyclops.payment_card_notify")
    def test_notify_empty_transactions(self, mock_payment_card_notify, mock_send_email):
        add_transactions_empty_route()

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "transactions work"}

        notify([{"token": "test"}], [mock_response])

        mock_payment_card_notify.assert_called_once_with(
            "Spreedly gateway BREACHED! An email has been sent to development@bink.com"
        )

        mock_send_email.assert_called_once_with(
            "Successfully redacted gateway with token test.\n\nRedacted gateway "
            "transaction: {'status': 'transactions work'}\n\nTransactions: "
            "(paginated, most recent first)...\n\nTransactions for gateway with "
            "token test follow:\nNo transactions to retrieve."
        )

    @responses.activate
    @patch("cyclops.cyclops.send_email")
    @patch("cyclops.cyclops.payment_card_notify")
    def test_notify_bad_request(self, mock_payment_card_notify, mock_send_email):
        add_transactions_bad_request_route()

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "transactions work"}

        notify([{"token": "test"}], [mock_response])

        mock_payment_card_notify.assert_called_once_with(
            "Spreedly gateway BREACHED! An email has been sent to development@bink.com"
        )

        mock_send_email.assert_called_once_with(
            "Successfully redacted gateway with token test.\n\nRedacted gateway "
            "transaction: {'status': 'transactions work'}\n\nTransactions: "
            "(paginated, most recent first)...\n\nTransactions for gateway with "
            "token test follow:\nFailed to retrieve transactions."
        )

    @responses.activate
    def test_get_gateways(self):
        add_gateways_route()
        gateways = get_gateways()
        self.assertEqual(gateways[0]["status"], "gateways work")
