# this is seed file

from django.core.management.base import BaseCommand, CommandError

from pst.models import User
from pst .models import Post


from pytz import all_timezones
import pytz
from faker import Faker
from random import randint, random

from django.contrib.auth import models
from pst.models import User, Spending, SpendingFile, Spending_type, Categories, Budget, Reward, Post, PostImage, Reply, Like, TotalBudget   #,RewardPoint
import datetime
import random
from django.db import IntegrityError
from decimal import Decimal
from django.core.files import File
import io
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Command(BaseCommand):
    USER_COUNT = 100
    POST_COUNT = 2000
    FOLLOW_PROBABILITY = 0.1
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_posts()
        self.create_followers()

    def create_users(self):
        self.create_johndoe()
        user_count = 1
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user()
            except:
                continue
            user_count += 1
        print("User seeding complete.      ")

    def create_johndoe(self):
        User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Jane',
            last_name='Doe',
            bio="Hi, I'm Jane Doe and want to remain anonymous here.  "
                "This is a sample account for development purposes."
        )

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._create_email(first_name, last_name)
        username = self._create_username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        User.objects.create_user(
            username=username,
            email=email,
            password=Command.DEFAULT_PASSWORD,
            first_name=first_name,
            last_name=last_name,
            bio=bio
        )

    def _create_email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _create_username(self, first_name, last_name):
        username = f'@{first_name}.{last_name}'
        return username

    def create_posts(self):
        for i in range(self.POST_COUNT):
            print(f"Seeding post {i}/{self.POST_COUNT}", end='\r')
            self.create_post()
        print("Post seeding complete.      ")

    def create_post(self):
        post = Post()
        post.author = self.get_random_user()
        post.text = self.faker.text(max_nb_chars=280)
        post.save()
        datetime = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        Post.objects.filter(id=post.id).update(created_at = datetime)

    def get_random_user(self):
        index = randint(0,self.users.count()-1)
        return self.users[index]

    def create_followers(self):
        count = 1
        for user in self.users:
            print(f"Seed followers for user {count}/{self.USER_COUNT}", end='\r')
            self.create_followers_for_user(user)
            count += 1
        print("Follower seeding complete.     ")

    def create_followers_for_user(self, user):
        for follower in self.users:
            if random() < self.FOLLOW_PROBABILITY:
                user.toggle_follow(follower)
        users = []

       
        
        for i in range(10):
            # create fake user
            user = User.objects.create(
                email=self.faker.email(),
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                bio=self.faker.text(max_nb_chars=500),
                gender=self.faker.random_element(
                    elements=['Male', 'Female', 'Other', 'Prefer not to say']),
                phone_number=self.faker.phone_number(),
                address=self.faker.address()
            )
            print(f'Created user {user.email}')
            users.append(user)

           
        # create spending
        for _ in range(10):
            spending = Spending.objects.create(
                title=self.faker.word(),
                spending_owner=User.objects.order_by('?').first(),
                amount=Decimal(random.uniform(1, 1000)),
                descriptions=self.faker.text(max_nb_chars=500),
                date=self.faker.date_between('-1y', 'today'),
                spending_type=random.choice(Spending_type.choices),
                spending_category=random.choice(self.categories)
            )
                 
        # create spending files
        for _ in range(random.randint(0, 3)):
            file_name = f'{self.faker.word()}.txt'
            file_content = io.StringIO('example file content')
            file = ContentFile(file_content.read().encode('utf-8'), name=file_name)
            SpendingFile.objects.create(
                spending=spending,
                file=file
            )    
            print(f'Created spending {spending.title} for user {user.email}')
        print(f'Successfully created 100 spendings for user {user.email}')

         # categories_name= [food, drink]
        # create categories
        if not Categories.objects.exists():
            self.categories = [
                Categories.objects.create(
                    name=self.faker.word(),
                    owner=User.objects.order_by('?').first(),
                    categories_type=random.choice(['Expenditure', 'Income']),
                    default_category=False
                ) for _ in range(10)
            ]
        else:
            self.categories = Categories.objects.all()
            
        # create posts and post images
        for i in range(20):
            post = Post.objects.create(
                user=random.choice(users),
                title=self.faker.sentence() if random.choice([True, False]) else '',
                content=self.faker.text(max_nb_chars=500)
            )
            print(f'Created post {post.id}')
            for j in range(random.randint(0, 5)):
                image = PostImage.objects.create(
                    post=post,
                    image=f'img/image-{random.randint(1,10)}.jpg'
                )
                print(f'Created image {image.id} for post {post.id}')
        # create replies
        for i in range(10):
            post = Post.objects.order_by('?').first()
            reply = Reply.objects.create(
                user=random.choice(users),
                parent_post=post,
                content=self.faker.text(max_nb_chars=200)
            )
            print(f'Created reply {reply.id} for post {post.id}')
        # create nested replies
        for j in range(random.randint(0, 2)):
            parent_reply = Reply.objects.filter(parent_post=post).order_by('?').first()
            reply = Reply.objects.create(
                user=random.choice(users),
                parent_post=post,
                parent_reply=parent_reply,
                content=self.faker.text(max_nb_chars=200)
            )
            print(f'Created nested reply {reply.id} for reply {parent_reply.id}')    
        # create likes for posts and replies
        all_posts_and_replies = list(Post.objects.all()) + list(Reply.objects.all())
        for item in all_posts_and_replies:
            for l in range(random.randint(0, 10)):
                user = random.choice(users)
                like, created = Like.objects.get_or_create(
                    user=user,
                    content_type=ContentType.objects.get_for_model(item),
                    object_id=item.id
                )
                if created:
                    print(f'Created like {like.id} for {item.__class__.__name__} {item.id}')
                else:
                    print(f'Like for {item.__class__.__name__} {item.id} already exists for user {user.email}')
        # create budgets
        for user in users:
            categories = Categories.objects.filter(owner=user)
            for _ in range(5):
                budget = Budget.objects.create(
                    name=self.faker.word(),
                    limit=random.randint(500, 10000),
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=random.randint(30, 180)),
                    budget_owner=user,
                    spending_category=random.choice(self.categories)
                )
                print(f'Created budget {budget.id} for user {user.email}')
        # create total budgets
        for user in users:
            total_budget = TotalBudget.objects.create(
                name=self.faker.word(),
                limit=random.randint(1000, 50000),
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=random.randint(30, 365)),
                budget_owner=user,
            )
            print(f'Created total budget {total_budget.id} for user {user.email}')
