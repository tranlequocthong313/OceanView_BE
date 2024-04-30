from firebase_admin import messaging


def subscribe_to_topic(fcm_tokens, topic):
    response = messaging.subscribe_to_topic(fcm_tokens, topic)
    print(response.success_count, "tokens were subscribed successfully")
    return response


def unsubscribe_from_topic(fcm_tokens, topic):
    response = messaging.unsubscribe_from_topic(fcm_tokens, topic)
    print(response.success_count, "tokens were unsubscribed successfully")
    return response
