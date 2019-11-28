from django.test import TestCase, Client
from django.urls import reverse
from events.models import Event, Account, Organization

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home = reverse('events-home')
        self.login = reverse('events-login')
        self.register = reverse('events-register')
        self.organizations = reverse('events-organizations')
        self.account_details = reverse('events-account-details')
        self.event_details = reverse('events-event-details')
        self.org_details = reverse('events-org-details')
        self.add_event = reverse('events-add-event')


    def test_home_GET(self):
        response = self.client.get(self.home)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_login_GET(self):
        response = self.client.get(self.login)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_GET(self):
        response = self.client.get(self.register)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_organizations_GET(self):
        response = self.client.get(self.organizations)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'organizations.html')

    def test_account_details_GET(self):
        response = self.client.get(self.account_details)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'account-detail.html')

    def test_event_details_GET(self):
        response = self.client.get(self.event_details)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'event-detail.html')

    def test_org_details_GET(self):
        response = self.client.get(self.org_details)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'org-detail.html')

    def test_add_event_GET(self):
        response = self.client.get(self.add_event)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'add-event.html')

    
