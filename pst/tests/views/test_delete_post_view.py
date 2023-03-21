from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class DeletePostTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json',]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.post = Post.objects.get(content='This is example post 1')
        self.url = reverse('delete_post', kwargs={'post_id': self.post.id})

    def test_delete_post_url(self):
        # Test that the URL for delele pst is correct
        self.assertEqual(self.url, f'/delete_post/{self.post.id}/')

    def test_delete_post(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Count the number of posts before delete one
        posts_count_before = Post.objects.count()

        # Delete the post
        response = self.client.post(self.url, follow=True)

        # Count the number of posts after delete one
        posts_count_after = Post.objects.count()
        self.assertEqual(posts_count_before, posts_count_after + 1)

        # Test that the response redirects to the personal forum page
        self.assertRedirects(response, reverse('personal_forum'))

        # Test that the post was deleted
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

        # Test that the success message was displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'post has been deleted')
        self.assertEqual(messages_list[0].level, messages.WARNING)