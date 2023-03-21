from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class LikeReplyTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.parent_reply = Reply.objects.get(content='This is example reply 1')
        self.reply = Reply.objects.get(content='This is example reply 2')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('like_reply', kwargs={'reply_id': self.reply.id, 'post_id': self.post.id})

    def test_like_reply_url(self):
        # Test that the URL for like reply is correct
        self.assertEqual(self.url, f'/like_reply/{self.reply.id}/{self.post.id}/')

    def test_like_reply(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the view returns a 200 status code
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test the number of likes is correct
        self.post.refresh_from_db()
        self.assertEqual(self.reply.likes.count(), 1)
        self.assertEqual(self.reply.likes.first().user, self.user)

    def test_unlike_reply(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that unliking a post works
        like = Like.objects.create(
            user=self.user, 
            content_object=self.reply
        )

        # Test that the view returns a 200 status code
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test the number of likes is correct
        self.post.refresh_from_db()
        self.assertEqual(self.reply.likes.count(), 0)

        # CHeck that the like is no more exist
        self.assertFalse(Like.objects.filter(pk=like.pk).exists())


    