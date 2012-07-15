# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from redis import ConnectionPool as RedisConnectionPool
from redis import Redis

from redis.connection import UnixDomainSocketConnection, Connection
from redis.connection import DefaultParser

from .views import BaseSseView

import json


CONNECTION_KWARGS = getattr(settings, 'REDIS_SSEQUEUE_CONNECTION_SETTINGS', {})
DEFAULT_CHANNEL = getattr(settings, 'REDIS_SSEQUEUE_CHANEL_NAME', 'sse')


class ConnectionPoolManager(object):
    pools = {}

    @classmethod
    def key_for_kwargs(cls, kwargs):
        return ":".join([str(v) for v in kwargs.values()])

    @classmethod
    def connection_pool(cls, **kwargs):
        pool_key = cls.key_for_kwargs(kwargs)
        if pool_key in cls.pools:
            return cls.pools[pool_key]

        location = kwargs.get('location', None)
        if not location:
            raise ImproperlyConfigured("no `location` key on connection kwargs")

        params = {
            'connection_class': Connection,
            'db': kwargs.get('db', 0),
            'password': kwargs.get('password', None),
        }

        if location.startswith("unix:"):
            params['connection_class'] = UnixDomainSocketConnection
            params['path'] = location[5:]
        else:
            try:
                params['host'], params['port'] = location.split(":")
                params['port'] = int(params['port'])

            except ValueError:
                raise ImproperlyConfigured("Invalid `location` key syntax on connection kwargs")

        cls.pools[pool_key] = RedisConnectionPool(**params)
        return cls.pools[pool_key]


class RedisQueueView(BaseSseView):
    redis_channel = DEFAULT_CHANNEL

    def iterator(self):
        connection = _connect()
        pubsub = connection.pubsub()
        pubsub.subscribe(self.get_redis_channel())

        for message in pubsub.listen():
            if message['type'] == 'message':
                event, data = json.loads(message['data'])
                self.sse.add_message(event, data)
                yield

    def get_redis_channel(self):
        return self.redis_channel


def _connect():
    pool = ConnectionPoolManager.connection_pool(**CONNECTION_KWARGS)
    return Redis(connection_pool=pool)


def send_event(event_name, data, channel=DEFAULT_CHANNEL):
    connection = _connect()
    connection.publish(channel, json.dumps([event_name, data]))


__all__ = ['send_event', 'RedisQueueView']
