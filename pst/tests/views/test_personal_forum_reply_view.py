from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class PersonalForumReplyTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.parent_reply = Reply.objects.get(content='This is example reply 1')
        self.reply = Reply.objects.get(content='This is example reply 2')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('personal_forum_reply')

    def test_personal_forum_reply_url(self):
        # Test that the URL for personal forum reply is correct
        self.assertEqual(self.url, '/personal_forum_reply/')

    def test_personal_forum_reply_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the personal forum reply page is accessible when logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal_forum_reply.html')

        # Test that the page contains the correct number of replies
        replies = response.context['reply_page_obj']
        self.assertEqual(replies.paginator.count, Reply.objects.count())

    def test_personal_forum_reply_page_replies_request(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test that the post is correctly display in the personal forum reply
        select_reply = Reply.objects.get(content='This is example reply 2')
        self.assertIsNotNone(select_reply)
        self.assertEqual(select_reply.user, self.user)
        self.assertEqual(select_reply.parent_post, self.post)
        self.assertEqual(select_reply.parent_reply, self.parent_reply)
        self.assertEqual(select_reply.content, 'This is example reply 2')

    def test_personal_forum_reply_page_post_request_with_new_reply_create(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Count the number of posts before create one
        replies_count_before = Reply.objects.count()

        new_reply = Reply.objects.create(
            user=self.user,
            content='This is new example reply',
            parent_post=self.post,
            parent_reply=self.parent_reply,
            reply_date='2023-3-30'
        )

        # Count the number of posts after create one
        replies_count_after = Reply.objects.count()
        self.assertEqual(replies_count_before + 1, replies_count_after)

        # Test that the post is correctly display in the personal forum
        select_reply = Reply.objects.get(content='This is new example reply')
        self.assertIsNotNone(select_reply)
        self.assertEqual(select_reply.user, self.user)
        self.assertEqual(select_reply.parent_post, self.post)
        self.assertEqual(select_reply.parent_reply, self.parent_reply)
        self.assertEqual(select_reply.content, 'This is new example reply')

    def test_personal_forum_reply_paginator(self):
        # Create 13 test replies
        replies = [Reply.objects.create(
                user=self.user,
                parent_post=self.post,
                content=f'Test Reply {i}',
                reply_date='2024-3-30'
            ) for i in range(13)]

        # Log in as the test user and get the first page of the personal forum reply
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        # Check that the response is OK and the first page has 5 replies
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reply_page_obj'].object_list), 5)
        self.assertEqual(response.context['reply_page_obj'].number, 1)

        # Check that the paginator has the correct properties
        paginator = response.context['reply_page_obj'].paginator
        self.assertEqual(paginator.count, 15)
        self.assertEqual(paginator.num_pages, 3)
        self.assertEqual(list(paginator.page_range), [1, 2, 3])

        # Get the second and third pages and check their properties
        response = self.client.get(self.url + '?reply_page=2')
        self.assertEqual(len(response.context['reply_page_obj'].object_list), 5)
        self.assertEqual(response.context['reply_page_obj'].number, 2)

        response = self.client.get(self.url + '?reply_page=3')
        self.assertEqual(len(response.context['reply_page_obj'].object_list), 5)
        self.assertEqual(response.context['reply_page_obj'].number, 3)

        # Get a non-existent page and check that the response is 200 since it will return the content in the last existing page
        response = self.client.get(self.url + '?reply_page=4')
        self.assertEqual(response.status_code, 200)