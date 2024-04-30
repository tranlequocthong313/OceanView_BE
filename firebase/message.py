from firebase_admin import messaging


def send(tokens, notification=None, data=None):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(**notification) if notification else None,
        data=data,
        tokens=tokens,
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


def send_notification_to_admin(
    title=None, body=None, link=None, request=None, data=None
):
    return send_to_topic(
        topic="admin",
        notification=messaging.Notification(
            title=title,
            body=body,
            image=request.user.avatar_url,
        ),
        webpush=messaging.WebpushConfig(
            headers={"Urgency": "high"},
            fcm_options=messaging.WebpushFCMOptions(link=link),
            data=data,
        ),
    )
