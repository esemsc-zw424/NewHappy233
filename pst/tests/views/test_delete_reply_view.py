from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class DeleteReplyTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.parent_reply = Reply.objects.get(content='This is example reply 1')
        self.reply = Reply.objects.get(content='This is example reply 2')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('delete_reply', kwargs={'reply_id': self.reply.id})

    def test_delete_reply_url(self):
        # Test that the URL for post detail is correct
        self.assertEqual(self.url, f'/delete_reply/{self.reply.id}/')

    def test_delete_reply(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Count the number of replies before delete one
        replies_count_before = Reply.objects.count()

        # Delete the reply
        response = self.client.post(self.url, follow=True)

        # Count the number of replies after delete one
        replies_count_after = Reply.objects.count()
        self.assertEqual(replies_count_before, replies_count_after + 1)

        # Test that the response redirects to the personal forum page
        self.assertRedirects(response, reverse('personal_forum_reply'))

        # Test that the reply was deleted
        self.assertFalse(Reply.objects.filter(id=self.post.id).exists())

        # Test that the success message was displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'reply has been deleted')
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_delete_parent_reply(self):
        # when parent reply is deleted, all the reply that has this reply as their parent reply will have their parent reply set to null

        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # update the url
        url = reverse('delete_reply', kwargs={'reply_id': self.parent_reply.id})

        # Count the number of replies before delete one
        replies_count_before = Reply.objects.count()

        # Delete the reply
        response = self.client.post(self.url, follow=True)

        # Count the number of replies after delete one
        replies_count_after = Reply.objects.count()
        self.assertEqual(replies_count_before, replies_count_after + 1)

        # Test that the response redirects to the personal forum page
        self.assertRedirects(response, reverse('personal_forum_reply'))

        # Test that the reply was deleted
        self.assertFalse(Reply.objects.filter(id=self.post.id).exists())

        # Check that the parent_reply field of all replies with the deleted reply as their parent reply is null
        for reply in Reply.objects.filter(parent_reply=self.parent_reply):
            self.assertIsNone(reply.parent_reply)

        # Test that the success message was displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'reply has been deleted')
        self.assertEqual(messages_list[0].level, messages.WARNING)