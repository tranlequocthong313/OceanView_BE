from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from app import settings

"""
Generate a token by serializing the provided payload using the application's secret key and hashing salt.

Args:
    payload (dict): The data payload to be included in the token.

Returns:
    str: The generated token string.
"""


def generate_token(payload=None):
    s = Serializer(settings.SECRET_KEY)
    return s.dumps(payload, salt=settings.HASHING_SALT)


"""
Verify and decode a token to retrieve the payload using the application's secret key and hashing salt.

Args:
    token (str): The token to verify and decode.
    max_age (int, optional): The maximum age of the token in seconds. Defaults to 3600.

Returns:
    dict: The decoded payload if the token is valid and within the specified age limit, None otherwise.
"""


def verify_token(token, max_age=3600):
    s = Serializer(settings.SECRET_KEY)
    try:
        return s.loads(s=token, salt=settings.HASHING_SALT, max_age=max_age)
    except Exception as e:
        return None
