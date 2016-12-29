"""
Example test for django_sse  -  server sent event streaming
"""

from django.test import TestCase
import unittest
from django.test.client import Client, RequestFactory
from .views import MySseEvents

try:
    from django.http import StreamingHttpResponse
    django_version_supports_streaming = True
except ImportError:
    django_version_supports_streaming = False


class TestMySseEvents(TestCase):
    @unittest.skipUnless(django_version_supports_streaming,
                         "This version of django does not support streaming responses, "
                         "so any test would hang.")
    def test_MySseEvents(self):
        """
        Test the MySseEvents class
        """
        factory = RequestFactory()
        request = factory.get('/blah')
        
        MySseEvents.DELAY_BETWEEN_MESSAGES = 0  # No delay so the test goes fast
        response = MySseEvents.as_view()(request)

        self.assertTrue(response.streaming)
        
        # the response always starts with the retry value
        self.assertIn("retry:", next(response.streaming_content))

        for i in range(0,5):  # Lets test for 5 messages
            self.assertIn("event: date", next(response.streaming_content))
            self.assertIn("data:", next(response.streaming_content))
            # blank line padding between messages
            self.assertEqual("\n", next(response.streaming_content))
            
        
