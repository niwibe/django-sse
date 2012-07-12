# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.encoding import force_unicode

import functools
import io
import re
import uuid

import json
import threading


DEFAULT_RETRY_TIMEOUT = getattr(settings, 'DJANGO_SSE_DEFAULT_RETRY', 2000)
DEFAULT_SLEEP = getattr(settings, 'DJANGO_SSE_DEFAULT_SLEEP', 1)

class Response(object):
    _retry = DEFAULT_RETRY_TIMEOUT
    _buffer = None
    _current_event = 'message'
    _prev_event = 'message'
    _rx_event = re.compile(r'^event_([\w\d\_]+)$', flags=re.U)
    _last_id = None
    _current_id = None

    def __init__(self):
        self._current_id = self.uuid()
        self._buffer = io.StringIO()
        self._buffer.write(u'retry: {0}\nid: {1}\n\n'.format(self._retry, self._current_id))

    def set_retry(self, retrynum):
        """
        Set distinct retry timeout instead the default
        value. You can only assign the value before adding messages.
        """

        self._retry = retrynum

    def add_message(self, event, text, split=True):
        """
        Add messaget with eventname to the buffer.
        """

        buffer_texts = [force_unicode(text)]
        if split:
            buffer_texts = force_unicode(text).splitlines()
        
        self._current_event = event
        if self._current_event != self._prev_event:
            self._buffer.write(u'event: {0}\n'.format(event))
        
        for text_item in buffer_texts:
            self._buffer.write(u'data: {0}\n'.format(text_item))

        self._buffer.write(u'\n')

    def __getattr__(self, attr):
        """
        Make a dinamic method for add messages to specific events
        like event_<eventname>(text="Hello")

        Examples:
            response.add_foo(text="bar")

        This sets event to "foo" and put "bar" as content.
        """

        res = self._rx_event.search(attr)
        if not res:
            return super(Response, self).__getattr__(attr)
        return functools.partial(self.add_message, event=res.group(1))
        
    def get_unicode(self):
        """
        Obtain raw unicode buffer content.
        """

        result = self._buffer.getvalue()
        self._buffer.close()
        self._buffer = io.StringIO()
        return result
    
    def uuid(self):
        return unicode(uuid.uuid1())

    @property
    def last_id(self):
        """ 
        Obtain the last uuid, if this is a first
        response, last_id is None.
        """

        return self._last_id

    @property
    def current_id(self):
        """
        Obtain current responde uuid. 
        """

        return self._current_id

    @property
    def is_first(self):
        """
        Return True if this is a first response.
        """

        return self.last_id is None


class RedisPubSubResponse(Response):
    def __init__(self, *args, **kwargs):
        super(RedisPubSubResponse, self).__init__(*args, **kwargs)

        t1 = threading.Thread(target=self.listener)
        t1.start()

    def listener(self):
        from django_sse.utils import redis_connection

        r = redis_connection()
        r = r.pubsub()

        r.subscribe('sse')

        for m in r.listen():
            if m['type'] == 'message':
                data = json.loads(m['data'])
                self.add_message(*data)
