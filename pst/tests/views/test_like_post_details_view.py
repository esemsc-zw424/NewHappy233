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

class PostDetailTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.post = Post.objects.get(content='This is example post 1')
        self.url = reverse('like_post_details', kwargs={'like_post_details': self.post.id})

    def test_like_post_details_url(self):
        # Test that the URL for like post details is correct
        self.assertEqual(self.url, f'/like_post_details/{self.post.id}/')
