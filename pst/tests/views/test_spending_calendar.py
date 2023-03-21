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


    # def setUp(self):
    #     self.user = User.objects.create_user(
    #         username='testuser', password='testpass'
    #     )
    #     self.category = Categories.objects.create(
    #         name='Test category',
    #         owner=self.user,
    #         categories_type='EXPENDITURE',
    #         default_category=False
    #     )
    #     self.spending = Spending.objects.create(
    #         title='Test spending',
    #         spending_owner=self.user,
    #         amount=10.0,
    #         descriptions='Test description',
    #         date=datetime.now(),
    #         spending_type='EXPENDITURE',
    #         spending_category=self.category
    #     )

    # def test_get_spending_calendar_context(self):
    #     url = reverse('spending_calendar')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'spending_calendar.html')
        
    #     now = timezone.now()
    #     year = now.year
    #     month = now.month
    #     month_name = now.strftime('%B')
        
    #     expected_context = {
    #         'month_calendar_list': [
    #             [(1, 2, 10.0, 0), (2, 3, 0, 0), ...],
    #             [(3, 4, 0, 0), (4, 5, 0, 0), ...],
    #             ...
    #         ],
    #         'year': year,
    #         'month': month_name,
    #         'previous_month': month - 1,
    #         'previous_year': year,
    #         'next_month': month + 1,
    #         'next_year': year,
    #         'exp_amount': 10.0,
    #         'income_amount': 0
    #     }
        
    #     self.assertDictEqual(response.context, expected_context)