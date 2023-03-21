from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseNotFound
from datetime import datetime
import os

class ViewPostUserTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.parent_reply = Reply.objects.get(content='This is example reply 1')
        self.reply = Reply.objects.get(content='This is example reply 2')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('view_post_user', kwargs={'user_id': self.user.id, 'post_id': self.post.id})

    def test_view_post_user_url(self):
        # Test that the URL for view post user is correct
        self.assertEqual(self.url, f'/view_post_user/{self.user.id}/{self.post.id}/')

    def test_view_post_user_view_from_post(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the view returns a 200 status code
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Test that the correct template is used
        self.assertTemplateUsed(response, 'view_post_user.html')

        # Test that the context contains the correct user and post objects
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['post'], self.post)

    def test_view_post_user_view_from_reply(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Update the url
        url = reverse('view_post_user', kwargs={'user_id': self.user.id, 'post_id': self.reply.parent_post.id})

        # Test that the view returns a 200 status code
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test that the correct template is used
        self.assertTemplateUsed(response, 'view_post_user.html')

        # Test that the context contains the correct user and post objects
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['post'], self.reply.parent_post)
