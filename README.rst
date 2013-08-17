==========
django-sse
==========

Django integration with Server-Sent Events. (http://www.html5rocks.com/en/tutorials/eventsource/basics/)

This django application uses the module sse_, simple python implementation of sse protocol.


Introduction
------------

Is very similar to Django's generic views.

``django-sse`` exposes a generic view for implement the custom logic of the data stream.
Additionally, it  exposes some helper views for simple enqueuing messages for a client,
using redis or rabbitmq(not implemented).

**NOTE**: it strongly recomended expose this views with gevent pywsgi server, because every connection is
permanent blocking stream.


Implementing own view with sample stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The idea is to create a stream of data to send the current timestamp every 1 second to the client:

.. code-block:: python

    from django_sse.views import BaseSseView
    import time

    class MySseStreamView(BaseSseView):
        def iterator(self):
            while True:
                self.sse.add_message("time", str(time.time()))
                yield
                time.sleep(1)


The ``iterator()`` method must be a generator of data stream. The view has ``sse`` object,
for more information, see sse_ module documentation.

The acomulated data on sse is flushed to the client every iteration (yield statement).
You can flush the buffer, sometimes as you need.


Using a redis as message queue for push messages to client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``django-sse`` currently implements a redis helper for simple enqueuing messages for push to a clients.
For use it, the first step is a url declaration:

.. code-block:: python

    from django.conf.urls import patterns, include, url
    from django_sse.redisqueue import RedisQueueView

    urlpatterns = patterns('',
        url(r'^stream1/$', RedisQueueView.as_view(redis_channel="foo"), name="stream1"),
    )

This, on new connection is created, opens connection to redis and subscribe to a channel. On
new messages received from redis, it flushes theese to client.

And the second step, your can push messages to the queue in any other normal django views
with a simple api:

.. code-block:: python

    from django.http import HttpResponse
    from django_sse.redisqueue import send_event

    def someview(request):
        send_event("myevent", "mydata", channel="foo")
        return HttpResponse("dummy response")

``RedisQueueView`` precises of redis, put your connection params on your ``settings.py``:

.. code-block:: python

    REDIS_SSEQUEUE_CONNECTION_SETTINGS = {
        'location': 'localhost:6379',
        'db': 0,
    }



Can subscribe to a channel dynamically with some parameter on url?
------------------------------------------------------------------

Yes, you need create a subclass of ``RedisQueueView`` and overwrite the method ``get_redis_channel``.
Example:

.. code-block:: python

    # urls.py
    urlpatterns = patterns('',
        url(r'^sse/(?P<channel>\w+)/$', MyRedisQueueView.as_view(redis_channel="foo"), name="stream1"),
    )

    class MyRedisQueueView(RedisQueueView):
        def get_redis_channel(self):
            return self.kwargs['channel'] or self.redis_channel


Contributors:
-------------

* Flavio Curella / https://github.com/fcurella


License
-------

BSD License

.. _sse: https://github.com/niwibe/sse

