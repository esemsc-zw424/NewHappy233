from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Post, Reply, Like, PostImage, User
from pst.forms import PostForm, ReplyForm
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
import os

class AddPostTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/post.json']

    def setUp(self):
        self.post = Post.objects.get(content='This is example post 1')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('add_post')

    def test_add_post_url(self):
        # Test that the URL for adding a post is correct
        self.assertEqual(self.url, '/add_post/')

    def test_add_post_page_accessible(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the add post page is accessible when logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_post.html')

    def test_add_post_with_valid_data(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Use a test image from the fixtures directory
        with open('pst/tests/views/test_image/test_image_HOWAREYOU.png', 'rb') as f:
            image = SimpleUploadedFile('test_image_HOWAREYOU.png', f.read(), content_type='image/png')

            # Prepare the post form data
            post_data = {
                'title': 'Test Post',
                'content': 'This is a test post',
                'image' : image
            }

            # Count the number of posts before adding a new one
            posts_count_before = Post.objects.count()

            # Make a POST request with the form data
            response = self.client.post(self.url, post_data, follow=True)

            # Count the number of posts after adding a new one
            posts_count_after = Post.objects.count()
            self.assertEqual(posts_count_before + 1, posts_count_after)

            # Check that the response redirects to the forum page
            self.assertRedirects(response, reverse('forum'))

            # Check that the new post was created with the correct attributes
            new_post = Post.objects.get(content='This is a test post')
            self.assertIsNotNone(new_post)
            self.assertEqual(new_post.user, self.user)
            self.assertEqual(new_post.title, 'Test Post')
            self.assertEqual(new_post.content, 'This is a test post')
            self.assertEqual(new_post.images.count(), 1)

            messages_list = list(response.context['messages'])
            self.assertEqual(len(messages_list), 1)
            self.assertEqual(str(messages_list[0]), 'post has been successfully added!')
            self.assertEqual(messages_list[0].level, messages.SUCCESS)

            # Test that the image was saved correctly
            saved_image = new_post.images.first()
            self.assertIsNotNone(saved_image.file)
            self.assertEqual(saved_image.file.name, 'post_images/test_image_HOWAREYOU.png')

            # Get the absolute path to the static directory and delete it
            image_dir = os.path.abspath(os.path.join(__file__, '../../../../static'))
            image_path = os.path.join(image_dir, 'post_images', 'test_image_HOWAREYOU.png')
            os.remove(image_path)