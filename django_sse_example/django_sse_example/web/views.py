# Create your views here.

from django.shortcuts import render_to_response
from django.views.generic import View
from django.template import RequestContext
from django.utils.timezone import now

from django_sse.views import BaseSseView

import time

class Home1(View):
    def get(self, request):
        return render_to_response('home.html', {},
            context_instance=RequestContext(request))


class Home2(View):
    def get(self, request):
        return render_to_response('home2.html', {},
            context_instance=RequestContext(request))


class MySseEvents(BaseSseView):
    DELAY_BETWEEN_MESSAGES = 1
    def iterator(self):
        while True:
            self.sse.add_message("date", unicode(now()))
            time.sleep(MySseEvents.DELAY_BETWEEN_MESSAGES)
            yield
