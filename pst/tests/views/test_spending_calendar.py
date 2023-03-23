import calendar
from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, date
from pst.models import Spending, Categories, User

class GetSpendingCalendarContextTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.month_name = calendar.month_name[self.month]
        self.url = reverse('spending_calendar', kwargs={'year': self.year, 'month': self.month})

    def test_spending_calendar_page_loads_successfully(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_calendar.html')


    def test_view_spendings_daily_with_valid_data(self):
        spendings_daily = [Spending.objects.create(
            title='test_spending1',
            amount=10.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category1',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending2',
            amount=20.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category2',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions='')]

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_calendar.html')
        self.assertEqual(response.context['year'], self.year)
        self.assertEqual(response.context['month'], self.month_name)

        if self.month == 1:
            self.assertEqual(response.context['previous_year'], self.year-1)
            self.assertEqual(response.context['previous_month'], 12)
            self.assertEqual(response.context['next_year'], self.year)
            self.assertEqual(response.context['next_month'], 2)
        elif self.month == 12:
            self.assertEqual(response.context['previous_year'], self.year)
            self.assertEqual(response.context['previous_month'], 11)
            self.assertEqual(response.context['next_year'], self.year+1)
            self.assertEqual(response.context['next_month'], 1)
        else:
            self.assertEqual(response.context['previous_year'], self.year)
            self.assertEqual(response.context['previous_month'], self.month-1)
            self.assertEqual(response.context['next_year'], self.year)
            self.assertEqual(response.context['next_month'], self.month+1)
            
        self.assertEqual(len(spendings_daily), 2)
        self.assertEqual(spendings_daily[0].amount, 10.00)
        self.assertEqual(spendings_daily[0].title, 'test_spending1')
        self.assertEqual(spendings_daily[0].spending_category.name, 'test_category1')
        self.assertEqual(spendings_daily[0].spending_category.categories_type, 'Expenditure')

        self.assertEqual(spendings_daily[1].amount, 20.00)
        self.assertEqual(spendings_daily[1].title, 'test_spending2')
        self.assertEqual(spendings_daily[1].spending_category.name, 'test_category2')
        self.assertEqual(spendings_daily[1].spending_category.categories_type, 'Income')

    def test_view_month_calendar_list_with_valid_data(self):
        spendings_daily1 = [Spending.objects.create(
            title='test_spending1',
            amount=10.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category1',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending2',
            amount=20.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category2',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions='')]
        
        spendings_daily2 = [Spending.objects.create(
            title='test_spending3',
            amount=30.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category3',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending4',
            amount=40.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category4',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending5',
            amount=100.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category5',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending6',
            amount=20.00,
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='test_category6',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions='')]
        
        exp_sum1 = spendings_daily1[0].amount 
        income_sum1 = spendings_daily1[1].amount
        exp_sum2 = spendings_daily2[0].amount + spendings_daily2[1].amount
        income_sum2 = spendings_daily2[2].amount + spendings_daily2[3].amount
        month_calendar_list = [[exp_sum1, income_sum1], [exp_sum2, income_sum2]]

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_calendar.html')
        self.assertEqual(response.context['year'], self.year)
        self.assertEqual(response.context['month'], self.month_name)

        if self.month == 1:
            self.assertEqual(response.context['previous_year'], self.year-1)
            self.assertEqual(response.context['previous_month'], 12)
            self.assertEqual(response.context['next_year'], self.year)
            self.assertEqual(response.context['next_month'], 2)
        elif self.month == 12:
            self.assertEqual(response.context['previous_year'], self.year)
            self.assertEqual(response.context['previous_month'], 11)
            self.assertEqual(response.context['next_year'], self.year+1)
            self.assertEqual(response.context['next_month'], 1)
        else:
            self.assertEqual(response.context['previous_year'], self.year)
            self.assertEqual(response.context['previous_month'], self.month-1)
            self.assertEqual(response.context['next_year'], self.year)
            self.assertEqual(response.context['next_month'], self.month+1)

        self.assertEqual(month_calendar_list[0][0], 10.00)
        self.assertEqual(month_calendar_list[0][1], 20.00)
        self.assertEqual(month_calendar_list[1][0], 70.00)
        self.assertEqual(month_calendar_list[1][1], 120.00)