from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class AddReplyToReplyTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.parent_reply = Reply.objects.get(content='This is example reply 1')
        self.reply = Reply.objects.get(content='This is example reply 2')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('add_reply_to_reply', kwargs={'post_id': self.post.id, 'parent_reply_id': self.parent_reply.id})

    def test_add_reply_to_post_url(self):
        # Test that the URL for add reply to reply is correct
        self.assertEqual(self.url, f'/add_reply_to_reply/{self.post.id}/{self.parent_reply.id}/')

    def test_add_reply_to_reply_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the add post page is accessible when logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_reply_to_reply.html')

    def test_add_reply_to_post_with_valid_data(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Prepare the reply form data
        reply_data = {
            'content': 'This is a test reply',
        }

        # Count the number of replies before adding a new one
        replies_count_before = Reply.objects.count()

        # Make a POST request with the form data
        response = self.client.post(self.url, reply_data, follow=True)

        # Count the number of replies after adding a new one
        replies_count_after = Reply.objects.count()
        self.assertEqual(replies_count_before + 1, replies_count_after)

        # Check that the response redirects to the post detail page
        self.assertRedirects(response, reverse('post_detail', kwargs={'post_id': self.post.id}))

        # Check that the new reply was created with the correct attributes
        new_reply = Reply.objects.get(content='This is a test reply')
        self.assertIsNotNone(new_reply)
        self.assertEqual(new_reply.user, self.user)
        self.assertEqual(new_reply.content, 'This is a test reply')
        self.assertEqual(new_reply.parent_post, self.post)
        self.assertEqual(new_reply.parent_reply, self.parent_reply)

        # Check that the message correctly display
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Reply has been successfully added!')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)