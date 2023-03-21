from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from pst.models import Spending, Categories, User

class SpendingReportTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.url = reverse('spending_report')

    def test_spending_report_page_loads_successfully(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_report.html')
        self.assertEqual(response.context['sorted_spendings'].count(), 0)
        self.assertEqual(response.context['page_obj'].number, 1)
        
    def test_spending_report_displays_correct_data(self):
        Spending.objects.create(
            title='test_spending',
            spending_owner=self.user,
            amount=10.00,
            date=date.today(),
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
        self.assertContains(response, 'Expenditure')
        self.assertContains(response, 'test_spending')
        self.assertContains(response, 'test_category')
        self.assertContains(response, '10.00')

    def test_spending_report_filters_by_date_range(self):
        Spending.objects.create(
            title='test_expenditure',
            spending_owner=self.user,
            amount=10.00,
            date=date.today(),
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
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        url = reverse('spending_report') + f'?start_date={start_date}&end_date={end_date}'
        response = self.client.get(url)

        self.assertContains(response, 'Expenditure')
        self.assertContains(response, 'test_expenditure')
        self.assertContains(response, 'test_category')
        self.assertContains(response, '10.00')

    def test_spending_report_filters_by_income_type(self):
        Spending.objects.create(
            title='test_income',
            spending_owner=self.user,
            amount=20.00,
            date=date.today(),
            spending_type='Income',
            spending_category=Categories.objects.create(
                name='test_category',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions=''
        )

        self.url = reverse('spending_report') + '?selected_categories=Income'
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertContains(response, 'Income')
        self.assertContains(response, 'test_income')
        self.assertContains(response, 'test_category')
        self.assertContains(response, '20.00')

    def test_spending_report_filters_by_expenditure_type(self):
        Spending.objects.create(
            title='test_expenditure',
            spending_owner=self.user,
            amount=10.00,
            date=date.today(),
            spending_category=Categories.objects.create(
                name='test_category_b',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''
        )

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertContains(response, 'Expenditure')
        self.assertContains(response, 'test_expenditure')
        self.assertContains(response, 'test_category')
        self.assertContains(response, '10.00')

    def test_paginator(self):
        sorted_spendings = [Spending.objects.create(
        title=f'Test Spending {i}',
        spending_owner=self.user,
        amount=10.0,
        descriptions='This is a test spending',
        date=date.today(),
        spending_category=Categories.objects.create(
            name='Food',
            owner=self.user,
            categories_type='Expenditure',
            default_category=False
        )
        ) for i in range(15)]

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sorted_spendings'].count(), 15)
        self.assertEqual(response.context['page_obj'].number, 1)

        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.count, 15)
        self.assertEqual(paginator.num_pages, 2)
        self.assertEqual(list(paginator.page_range), [1, 2])

        page_obj = response.context['page_obj']
        self.assertEqual(list(page_obj), sorted_spendings[:10])

        response = self.client.get(self.url + '?page=2')
        page_obj = response.context['page_obj']
        self.assertEqual(list(page_obj), sorted_spendings[10:])

    def test_spending_report_ajax_request(self):
        self.client.login(username=self.user.email, password='Password123')
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        response = self.client.get(f"{self.url}?start_date={start_date}&end_date={end_date}", HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_report.html')