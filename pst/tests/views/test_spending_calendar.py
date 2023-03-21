from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, date
from django.utils import timezone
from pst.models import Spending, Categories, User

class GetSpendingCalendarContextTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        year = datetime.now().year
        month = datetime.now().month
        self.url = reverse('spending_calendar', kwargs={'year': year, 'month': month})

    def test_spending_report_page_loads_successfully(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_calendar.html')

    def test_view_spending_calendar_with_valid_data(self):
        Spending.objects.create(
            title='Test Spending',
            amount=100,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''
        )

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_calendar.html')