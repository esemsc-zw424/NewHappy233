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

class LikePostDetailTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.post = Post.objects.get(content='This is example post 1')
        self.url = reverse('like_post_details', kwargs={'post_id': self.post.id})

    def test_like_post_details_url(self):
        # Test that the URL for like post details is correct
        self.assertEqual(self.url, f'/like_post_details/{self.post.id}/')

    def test_like_post_detail(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the view returns a 200 status code
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test the number of likes is correct
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 1)
        self.assertEqual(self.post.likes.first().user, self.user)

    def test_unlike_post_detail(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that unliking a post works
        like = Like.objects.create(
            user=self.user, 
            content_object=self.post
        )

        # Test that the view returns a 200 status code
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test the number of likes is correct
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 0)

        # CHeck that the like is no more exist
        self.assertFalse(Like.objects.filter(pk=like.pk).exists())
