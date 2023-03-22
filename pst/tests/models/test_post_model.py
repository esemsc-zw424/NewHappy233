from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Post, User

class PostModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.post = Post.objects.get(content = "This is example post 1")
        self.post_author = User.objects.get(email = "johndoe@example.org")

    def _assert_post_is_valid(self):
        try:
            self.post.full_clean()
        except(ValidationError):
            self.fail('Test post should be valid')

    def _assert_post_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_valid_post(self):
        self._assert_post_is_valid()

    def test_title_can_be_blank(self):
        self.post.title = ''
        self._assert_post_is_valid()

    def test_title_can_have_up_to_150_characters(self):
        self.post.title = 'x' * 150
        self._assert_post_is_valid()

    def test_title_cannot_exceed_150_characters(self):
        self.post.title = 'x' * 151
        self._assert_post_is_invalid()

    def test_post_owner_cannot_be_blank(self):
        self.post.user = None
        self._assert_post_is_invalid()

    def test_content_cannot_be_blank(self):
        self.post.content = ''
        self._assert_post_is_invalid()

    def test_content_can_have_more_than_4000_characters(self):
        self.post.content = 'x' * 4001
        self._assert_post_is_valid()

    def test_post_date_cannot_be_blank(self):
        self.post.post_date = None
        self._assert_post_is_valid()

    def test_content_of_the_post(self):
        expected_str = 'This is example post 1'
        self.assertEqual(str(self.post), expected_str)