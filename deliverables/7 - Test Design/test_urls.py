from django.test import SimpleTestCase
from django.urls import reverse, resolve
from events import views


class TestUrls(SimpleTestCase):

    def test_home_url(self):
        url = reverse('events-home')
        self.assertEquals(resolve(url).func, views.home)

    def test_login_url(self):
        url = reverse('events-login')
        self.assertEquals(resolve(url).func, views.login)

    def test_register_url(self):
        url = reverse('events-register')
        self.assertEquals(resolve(url).func, views.register)

    def test_organizations_url(self):
        url = reverse('events-organizations')
        self.assertEquals(resolve(url).func, views.organizations)

    def test_account_details_url(self):
        url = reverse('events-account-details')
        self.assertEquals(resolve(url).func, views.account_details)

    def test_event_details_url(self):
        url = reverse('events-event-details')
        self.assertEquals(resolve(url).func, views.event_details)

    def test_org_details_url(self):
        url = reverse('events-org-details')
        self.assertEquals(resolve(url).func, views.org_details)

    def test_add_event_url(self):
        url = reverse('events-add-event')
        self.assertEquals(resolve(url).func, views.add_event)
