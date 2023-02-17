from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Spending, SpendingFile
from django.core.files.uploadedfile import SimpleUploadedFile

class SpendingFileModelTestCase(TestCase):

    fixtures = ['pst/tests/fixtures/spending.json'], ['pst/tests/fixtures/users.json']


    def setUp(self):
        self.spending = Spending.objects.get(descriptions = "This is test spending 1")    
        self.spending_file = SpendingFile.objects.create(
            spending = self.spending, 
        )
    
    def _assert_spending_file_is_valid(self):
        try:
            self.spending_file.full_clean()
        except(ValidationError):
            self.fail('Test spending file should be valid')

    def _assert_spending_file_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.spending_file.full_clean()
    
    def test_file_can_be_empty(self):
        self.spending_file.file = None
        self._assert_spending_file_is_valid()
    
    def test_file_can_be_image(self):
        file = SimpleUploadedFile("image.jpg", content=b"file_content", content_type="image/jpeg")
        self.spending_file.file = file
        self._assert_spending_file_is_valid()

    def test_file_can_be_txt(self):
        file = SimpleUploadedFile("file.txt", content=b"file_content", content_type="text/plain")
        self.spending_file.file = file
        self._assert_spending_file_is_valid()
    
    def test_file_can_be_pdf(self):
        file = SimpleUploadedFile("file.pdf", content=b"file_content", content_type="application/pdf")
        self.spending_file.file = file
        self._assert_spending_file_is_valid()
    
    def test_file_can_be_png(self):
        file = SimpleUploadedFile("file.png", content=b"file_content", content_type="image/png")
        self.spending_file.file = file
        self._assert_spending_file_is_valid()

