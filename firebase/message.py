from firebase_admin import messaging

from notification.types import MessageTarget


def send(tokens, notification=None, data=None, **kwargs):
    message = messaging.MulticastMessage(
        notification=notification, data=data, tokens=tokens, **kwargs
    )
    response = messaging.send_multicast(message)
    print("{0} messages were sent successfully".format(response.success_count))
    return response


def send_to_topic(topic, notification=None, data=None, **kwargs):
    message = messaging.Message(
        notification=notification, data=data, topic=topic, **kwargs
    )
    response = messaging.send(message)
    print("Successfully sent message:", response)
    return response


def send_notification(
    title=None,
    body=None,
    image=None,
    link=None,
    data=None,
    target=MessageTarget.ADMIN,
    tokens=None,
):
    if target == MessageTarget.ADMIN:
        return send_to_topic(
            topic="admin",
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image,
            ),
            webpush=messaging.WebpushConfig(
                headers={"Urgency": "high"},
                fcm_options=messaging.WebpushFCMOptions(link=link),
                data=data,
            ),
        )
    elif target == MessageTarget.RESIDENTS:
        return send_to_topic(
            topic="resident",
            notification=messaging.Notification(title=title, body=body, image=image),
            android=messaging.AndroidConfig(data=data, priority="high"),
        )
    elif target == MessageTarget.RESIDENT and tokens:
        return send(
            tokens=list(tokens) or [],
            notification=messaging.Notification(title=title, body=body, image=image),
            android=messaging.AndroidConfig(data=data, priority="high"),
        )
