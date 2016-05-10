# -*- coding: utf-8 -*-

import django
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

try:
    if django.VERSION < (1, 7):
        from django.http import StreamingHttpResponse as HttpResponse
    else:
        from django.http.response import StreamingHttpResponse as HttpResponse
except ImportError:
    from django.http import HttpResponse, StreamingHttpResponse

from django.utils.decorators import method_decorator
from sse import Sse


class BaseSseView(View):
    """
    This is a base class for sse streaming.
    """

    def get_last_id(self):
        if "HTTP_LAST_EVENT_ID" in self.request.META:
            return self.request.META['HTTP_LAST_EVENT_ID']
        return None

    def _iterator(self):
        for subiterator in self.iterator():
            for bufferitem in self.sse:
                yield bufferitem

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.sse = Sse()

        self.request = request
        self.args = args
        self.kwargs = kwargs

        response = StreamingHttpResponse(self._iterator(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['Software'] = 'django-sse'
        return response

    def iterator(self):
        """
        This is a source of stream.
        Must use ``yield`` statement to flush
        content from sse object to the client.

        Example:

        def iterator(self):
            counter = 0
            while True:
                self.sse.add_message('foo', 'bar')
                self.sse.add_message('bar', 'foo')
                yield

        """
        raise NotImplementedError
