from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Post, User, PostImage
from django.core.files.uploadedfile import SimpleUploadedFile

class PostImageModelTestCase(TestCase):

    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
         
        self.post = Post.objects.get(content = "This is example post 1")
    
        self.post_image = PostImage.objects.create(
            post = self.post, 
        )
    
    def _assert_post_image_is_valid(self):
        try:
            self.post_image.full_clean()
        except(ValidationError):
            self.fail('Test post image should be valid')

    def _assert_post_image_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.post_image.full_clean()
    
    def test_file_can_be_empty(self):
        self.post_image.image = None
        self._assert_post_image_is_valid()
    
    def test_jpg_file_is_valid_format(self):
        image = SimpleUploadedFile("image.jpg", content=b"file_content", content_type="image/jpg")
        self.post_image.image = image
        self._assert_post_image_is_valid()
    
    def test_jpeg_file_is_valid_format(self):
        image = SimpleUploadedFile("image.jpeg", content=b"file_content", content_type="image/jpeg")
        self.post_image.image = image
        self._assert_post_image_is_valid()

    def test_png_file_is_valid_format(self):
        image = SimpleUploadedFile("image.png", content=b"file_content", content_type="image/png")
        self.post_image.image = image
        self._assert_post_image_is_valid()

    def test_invalid_file_format(self):
        file = SimpleUploadedFile("invalid_file.xyz", content=b"file_content", content_type="application/octet-stream")
        self.post_image.image = file
        self._assert_post_image_is_invalid()
    
