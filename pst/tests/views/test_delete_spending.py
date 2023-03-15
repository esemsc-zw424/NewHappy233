from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pst.models import Spending

class DeleteSpendingTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']
    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.spending = Spending.objects.create(name='Test Spending', amount=100, user=self.user)
        self.user2 = User.objects.get(email='johndoe@example.org')
    def test_delete_spending_unauthenticated(self):
        response = self.client.get(reverse('delete_spending', args=[self.spending.id]))
        self.assertRedirects(response, '/accounts/login/?next=/delete-spending/{}/'.format(self.spending.id))

    def test_delete_spending_no_permission(self):

        self.client.force_login(self.user2)
        response = self.client.get(reverse('delete_spending', args=[self.spending.id]))
        self.assertEqual(response.status_code, 403)

    def test_delete_spending_success(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_spending', args=[self.spending.id]))
        self.assertRedirects(response, reverse('view_spendings'))
        self.assertFalse(Spending.objects.filter(pk=self.spending.pk).exists())

    def test_delete_spending_invalid_id(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_spending', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_spending_success_message(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_spending', args=[self.spending.id]))
        self.assertContains(response, "spending has been deleted")
