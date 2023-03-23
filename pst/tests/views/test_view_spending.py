from django.test import TestCase, RequestFactory
from pst.models import Spending, User
from pst.forms import AddSpendingForm, EditSpendingForm, Categories
from django.urls import reverse
from datetime import date, datetime, timedelta
from django.shortcuts import render
import datetime

class ViewSpendingTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email = "johndoe@example.org")
        self.url = reverse('view_spendings')
    
    def test_view_requests_success(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spendings.html')
        self.assertContains(response, 'Add Spending')
        self.assertContains(response, 'Edit')
        self.assertIsInstance(response.context['add_form'], AddSpendingForm)
        self.assertIsInstance(response.context['edit_form'], EditSpendingForm)
        self.assertEqual(response.context['spending'].count(), 0)
        self.assertEqual(response.context['page_obj'].number, 1)

    def test_view_spendings_with_valid_data(self):
        Spending.objects.create(
            title='Test Spending',
            amount=100,
            descriptions='This is a test spending',
            date=date.today(),
            spending_owner=self.user,
            spending_category=Categories.objects.create(
                name='Food',
                owner=self.user
            )
        )

        self.client.login(username=self.user.email, password='Password123')
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        response = self.client.get(f"{self.url}?start_date={start_date}&end_date={end_date}")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spendings.html')
        self.assertContains(response, 'Add Spending')
        self.assertContains(response, 'Edit')
        self.assertIsInstance(response.context['add_form'], AddSpendingForm)
        self.assertIsInstance(response.context['edit_form'], EditSpendingForm)
        self.assertEqual(response.context['spending'].count(), 1)
        self.assertEqual(response.context['page_obj'].number, 1)

    def test_spending_report_sorts_by_amount(self):
        spending_list = [
            Spending.objects.create(
            title='test_spending1',
            spending_owner=self.user,
            amount=500.00,
            date=datetime.date(2023, 3, 19),
            spending_category=Categories.objects.create(
                name='test_expenditure',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending2',
            spending_owner=self.user,
            amount=200.00,
            date=datetime.date(2023, 3, 31),
            spending_category=Categories.objects.create(
                name='test_expenditure',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending3',
            spending_owner=self.user,
            amount=300.00,
            date=datetime.date(2023, 3, 10),
            spending_category=Categories.objects.create(
                name='test_income',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending4',
            spending_owner=self.user,
            amount=600.00,
            date=datetime.date(2023, 2, 20),
            spending_category=Categories.objects.create(
                name='test_income',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions='')
        ]
        sorted_list = sorted(spending_list, key=lambda x: x.amount)

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spendings.html')

        self.assertNotEqual(spending_list, sorted_list)
        self.assertEqual(sorted_list, sorted(spending_list, key=lambda x: x.amount))

    def test_spending_report_sorts_by_spending_category(self):
        spending_list = [
            Spending.objects.create(
            title='test_spending2',
            spending_owner=self.user,
            amount=500.00,
            date=datetime.date(2023, 3, 19),
            spending_category=Categories.objects.create(
                name='test_expenditure',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending1',
            spending_owner=self.user,
            amount=200.00,
            date=datetime.date(2023, 3, 31),
            spending_category=Categories.objects.create(
                name='test_expenditure',
                owner=self.user,
                categories_type='Expenditure',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending4',
            spending_owner=self.user,
            amount=300.00,
            date=datetime.date(2023, 3, 10),
            spending_category=Categories.objects.create(
                name='test_income',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions=''),

            Spending.objects.create(
            title='test_spending3',
            spending_owner=self.user,
            amount=600.00,
            date=datetime.date(2023, 2, 20),
            spending_category=Categories.objects.create(
                name='test_income',
                owner=self.user,
                categories_type='Income',
                default_category=False
            ),
            descriptions='')
        ]
        sorted_list = sorted(spending_list, key=lambda x: x.title)

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spendings.html')

        self.assertNotEqual(spending_list, sorted_list)
        self.assertEqual(sorted_list, sorted(spending_list, key=lambda x: x.title))

    def test_paginator(self):
        spending = [Spending.objects.create(
        title=f'Test Spending {i}',
        amount=100,
        descriptions='This is a test spending',
        date=date.today(),
        spending_owner=self.user,
        spending_category=Categories.objects.create(
            name='Food',
            owner=self.user
        )
        ) for i in range(15)]

        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['spending'].count(), 15)
        self.assertEqual(response.context['page_obj'].number, 1)

        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.count, 15)
        self.assertEqual(paginator.num_pages, 2)
        self.assertEqual(list(paginator.page_range), [1, 2])

        page_obj = response.context['page_obj']
        self.assertEqual(list(page_obj), spending[:10])

        response = self.client.get(self.url + '?page=2')
        page_obj = response.context['page_obj']
        self.assertEqual(list(page_obj), spending[10:])
        
    def test_view_spendings_ajax_request(self):
        self.client.login(username=self.user.email, password='Password123')
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        response = self.client.get(f"{self.url}?start_date={start_date}&end_date={end_date}", HTTP_X_REQUESTED_WITH='XMLHttpRequest')


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spending_table.html')
