from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os


class PersonalForumTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('personal_forum')

    def test_personal_forum_url(self):
        # Test that the URL for personal forum is correct
        self.assertEqual(self.url, '/personal_forum/')
    
    def test_personal_forum_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the personal forum page is accessible when logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal_forum.html')

        # Test that the page contains the correct number of posts
        posts = response.context['page_obj']
        self.assertEqual(posts.paginator.count, Post.objects.count())

    def test_personal_forum_page_post_request(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Test that the post is correctly display in the personal forum
        select_post = Post.objects.get(content='This is example post 1')
        self.assertIsNotNone(select_post)
        self.assertEqual(select_post.user, self.user)
        self.assertEqual(select_post.title, '')
        self.assertEqual(select_post.content, 'This is example post 1')

    def test_personal_forum_page_post_request_with_new_post_create(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Count the number of posts before create one
        posts_count_before = Post.objects.count()

        new_post = Post.objects.create(
            user=self.user,
            content='This is new example post',
            created_date='2023-3-30'
        )

        # Count the number of posts after create one
        posts_count_after = Post.objects.count()
        self.assertEqual(posts_count_before + 1, posts_count_after)

        # Test that the post is correctly display in the personal forum
        select_post = Post.objects.get(content='This is new example post')
        self.assertIsNotNone(select_post)
        self.assertEqual(select_post.user, self.user)
        self.assertEqual(select_post.title, '')
        self.assertEqual(select_post.content, 'This is new example post')

    def test_personal_forum_page_post_request_with_image(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Use a test image from the fixtures directory
        with open('pst/tests/views/test_image/test_image_HOWAREYOU.png', 'rb') as f:
            image = SimpleUploadedFile('test_image_HOWAREYOU.png', f.read(), content_type='image/png')
            post_image = PostImage.objects.create(post=self.post, file=image)

        # Test that the new post was created with the correct attributes
        new_post = Post.objects.get(content='This is example post 1')
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.user, self.user)
        self.assertEqual(new_post.title, '')
        self.assertEqual(new_post.content, 'This is example post 1')
        self.assertEqual(new_post.images.count(), 1)

        # Test that the image was saved correctly
        saved_image = new_post.images.first()
        self.assertIsNotNone(saved_image.file)
        self.assertEqual(saved_image.file.name, 'post_images/test_image_HOWAREYOU.png')

        # Get the absolute path to the static directory and delete it
        image_dir = os.path.abspath(os.path.join(__file__, '../../../../static'))
        image_path = os.path.join(image_dir, 'post_images', 'test_image_HOWAREYOU.png')
        os.remove(image_path)

    def test_personal_forum_post_paginator(self):
        # Create 13 test posts
        posts = [Post.objects.create(
                user=self.user,
                content=f'Test Post {i}',
                created_date='2024-3-30'
            ) for i in range(13)]

        # Log in as the test user and get the first page of the personal forum
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)

        # Check that the response is OK and the first page has 5 posts
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 5)
        self.assertEqual(response.context['page_obj'].number, 1)

        # Check that the paginator has the correct properties
        paginator = response.context['page_obj'].paginator
        self.assertEqual(paginator.count, 15)
        self.assertEqual(paginator.num_pages, 3)
        self.assertEqual(list(paginator.page_range), [1, 2, 3])

        # Get the second and third pages and check their properties
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(len(response.context['page_obj'].object_list), 5)
        self.assertEqual(response.context['page_obj'].number, 2)

        response = self.client.get(self.url + '?page=3')
        self.assertEqual(len(response.context['page_obj'].object_list), 5)
        self.assertEqual(response.context['page_obj'].number, 3)

        # Get a non-existent page and check that the response is 200 since it will return the content in the last existing page
        response = self.client.get(self.url + '?page=4')
        self.assertEqual(response.status_code, 200)