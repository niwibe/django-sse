from django.conf import settings
import json


SSE_REDIS_BROKER_DEFAULT = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0
}


def redis_connection():
    import redis

    params = SSE_REDIS_BROKER_DEFAULT.copy()
    params.update(getattr(settings, 'SSE_REDIS_BROKER', {}))

    lowercased_params = dict((k.lower(), v) for k, v in params.iteritems())

    r = redis.StrictRedis(**lowercased_params)

    return r


def redis_add_message(event, text):
    from django_sse.utils import redis_connection

    r = redis_connection()
    r.publish('sse', json.dumps([event, text]))
