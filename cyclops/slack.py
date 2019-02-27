from slackclient import SlackClient

import settings


client = SlackClient(settings.SLACK_API_TOKEN)


def payment_card_notify(message):
    """
    Sends `message` to the #payment-card-notify channel on Slack.
    """
    return client.api_call(
        "chat.postMessage",
        channel="#payment-card-notify",
        text=message,
        as_user=True,
    )
