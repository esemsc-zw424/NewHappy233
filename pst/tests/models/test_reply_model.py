from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Post, Reply, User

class ReplyModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.reply = Reply.objects.get(content = "This is example reply 2")
        self.user = User.objects.get(email = "johndoe@example.org")
        self.post = Post.objects.get(content="This is example post 1")
        self.parent_reply = Reply.objects.create(
            user=self.user,
            parent_post=self.post,
            content="This is an example reply",
        )

    def _assert_reply_is_valid(self):
        try:
            self.reply.full_clean()
        except ValidationError:
            self.fail("Test reply should be valid")

    def _assert_reply_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.reply.full_clean()

    def test_valid_reply(self):
        self._assert_reply_is_valid()

    def test_user_cannot_be_blank(self):
        self.reply.user = None
        self._assert_reply_is_invalid()

    def test_parent_post_cannot_be_blank(self):
        self.reply.parent_post = None
        self._assert_reply_is_invalid()

    def test_parent_reply_can_be_blank(self):
        self.reply.parent_reply = None
        self._assert_reply_is_valid()

    def test_parent_reply_can_point_to_another_reply(self):
        self.reply.parent_reply = self.parent_reply
        self._assert_reply_is_valid()

    def test_content_cannot_be_blank(self):
        self.reply.content = ""
        self._assert_reply_is_invalid()

    def test_reply_date_can_be_blank(self):
        self.reply.created_date = None
        self._assert_reply_is_valid()
