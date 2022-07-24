from django.test import SimpleTestCase
from django.urls import reverse, resolve

from chat.views import ThreadView, InboxView


class TestUrls(SimpleTestCase):

    def test_thread_url_is_resolved(self):
        url = reverse('chat',args="0")
        self.assertEquals(resolve(url).func.view_class, ThreadView)


