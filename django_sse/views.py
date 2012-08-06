# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
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

        response = HttpResponse(self._iterator(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['Software'] = 'django-sse'
        return response

    def iterator(self):
        """
        This is a source of stream.
        Must be use sentence ``yield`` for flush
        content fon sse object to the client.

        Example:

        def iterator(self):
            counter = 0
            while True:
                self.sse.add_message('foo', 'bar')
                self.sse.add_message('bar', 'foo')
                yield

        Note: This method must be reimplemented.

        """
        raise NotImplementedError
