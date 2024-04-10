from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from app import settings


def generate_token(payload):
    s = Serializer(settings.SECRET_KEY)
    return s.dumps(payload, salt=settings.HASHING_SALT)


def verify_token(token, max_age=3600):
    s = Serializer(settings.SECRET_KEY)
    try:
        payload = s.loads(s=token, salt=settings.HASHING_SALT, max_age=max_age)
        return payload
    except Exception as e:
        return None
