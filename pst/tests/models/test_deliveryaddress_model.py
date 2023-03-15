from django.test import TestCase
from pst.models import User
from pst.models import DeliveryAddress

class DeliveryAddressModelTest(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email = 'lll@example.org')
        self.delivery_address = DeliveryAddress.objects.create(
            user=self.user, address='123 Main St', phone_number=1234567890
        )

    def test_delivery_address_obj(self):
        self.assertEqual(str(self.delivery_address), 'DeliveryAddress object (1)')

    def test_delivery_address_user(self):
        self.assertEqual(self.delivery_address.user, self.user)

    def test_delivery_address_address(self):
        self.assertEqual(self.delivery_address.address, '123 Main St')

    def test_delivery_address_phone_number(self):
        self.assertEqual(self.delivery_address.phone_number, 1234567890)