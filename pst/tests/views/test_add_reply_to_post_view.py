from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class AddReplyToPostTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.post = Post.objects.get(content='This is example post 1')
        self.url = reverse('add_reply_to_post', kwargs={'post_id': self.post.id})

    def test_add_reply_to_post_url(self):
        # Test that the URL for add reply to post is correct
        self.assertEqual(self.url, f'/add_reply_to_post/{self.post.id}/')

    def test_add_reply_to_post_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the add post page is accessible when logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_reply_to_post.html')

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

        # Check that the message correctly display
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Reply has been successfully added!')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

