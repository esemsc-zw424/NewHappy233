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
        self.url = reverse('post_detail', kwargs={'post_id': self.post.id})

    def test_post_detail_url(self):
        # Test that the URL for post detail is correct
        self.assertEqual(self.url, f'/post_detail/{self.post.id}/')

    def test_post_detail_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the post detail page is accessible
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_detail.html')

        # Test that the post and its replies are correctly displayed
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(len(response.context['replies']), Reply.objects.filter(parent_post=self.post).count())

        # Test that the page contains the correct number of replies
        replies = response.context['page_obj']
        self.assertEqual(replies.paginator.count, Reply.objects.filter(parent_post=self.post).count())

    def test_correctly_return_HttpResponseNotFound_when_post_not_exist(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Set the post ID to a value that doesn't exist in the database
        nonexistent_post_id = Post.objects.last().id + 1
        url = reverse('post_detail', args=[nonexistent_post_id])

        # Make a GET request with the non-existent post ID
        response = self.client.get(url)

        # Check that the response is a 404 Not Found
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_post_detail_page_replies_paginator(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Create 13 test replies for the post
        replies = [Reply.objects.create(
            user=User.objects.first(),
            content=f'Test Reply {i}',
            parent_post=self.post
        ) for i in range(13)]

        # Get the first page of the post detail with replies
        response = self.client.get(self.url)

        # Check that the response is OK and the first page has 4 replies
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 4)
        self.assertEqual(response.context['page_obj'].number, 1)

        # Check that the paginator has the correct properties
        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.count, 13)
        self.assertEqual(paginator.num_pages, 4)
        self.assertEqual(list(paginator.page_range), [1, 2, 3, 4])

        # Get the second and third pages and check their properties
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(len(response.context['page_obj'].object_list), 4)
        self.assertEqual(response.context['page_obj'].number, 2)

        response = self.client.get(self.url + '?page=3')
        self.assertEqual(len(response.context['page_obj'].object_list), 4)
        self.assertEqual(response.context['page_obj'].number, 3)

        # Get a non-existent page and check that the response is 200 since it will return the content in the last existing page
        response = self.client.get(self.url + '?page=5')
        self.assertEqual(response.status_code, 200)