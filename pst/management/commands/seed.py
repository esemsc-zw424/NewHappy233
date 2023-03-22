# this is seed file
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from django.contrib.auth import models
from pst.models import User, Spending, SpendingFile, Spending_type, Categories, Budget, Reward, Post, PostImage, Reply, Like, TotalBudget, DeliveryAddress
from datetime import datetime, timedelta
import random
from django.db import IntegrityError
from decimal import Decimal
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from allauth.account.signals import user_signed_up
from pst.signals import create_default_categories

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 2

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

        self.start_date = (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        self.end_date = datetime.now()
        self.days_between = (self.end_date - self.start_date).days
        self.faker.unique.clear()
       

    def handle(self, *args, **options):

        self._create_specified_number_of_users()


        # # create spending
        # for _ in range(10):
        #     spending = Spending.objects.create(
        #         title=self.faker.word(),
        #         spending_owner=User.objects.order_by('?').first(),
        #         amount=Decimal(random.uniform(1, 1000)),
        #         descriptions=self.faker.text(max_nb_chars=500),
        #         date=self.faker.date_between('-1y', 'today'),
        #         spending_type=random.choice(Spending_type.choices),
        #         spending_category=random.choice(self.categories)
        #     )
                 
        # # create spending files
        # for _ in range(random.randint(0, 3)):
        #     file_name = f'{self.faker.word()}.txt'
        #     file_content = io.StringIO('example file content')
        #     file = ContentFile(file_content.read().encode('utf-8'), name=file_name)
        #     SpendingFile.objects.create(
        #         spending=spending,
        #         file=file
        #     )    
            
        # print(f'Successfully created 100 spendings for user {user.email}')

        #  # categories_name= [food, drink]
        # # create categories
        # if not Categories.objects.exists():
        #     self.categories = [
        #         Categories.objects.create(
        #             name=self.faker.word(),
        #             owner=User.objects.order_by('?').first(),
        #             categories_type=random.choice(['Expenditure', 'Income']),
        #             default_category=False
        #         ) for _ in range(10)
        #     ]
        # else:
        #     self.categories = Categories.objects.all()
            
        # # create posts and post images
        # for i in range(20):
        #     post = Post.objects.create(
        #         user=random.choice(users),
        #         title=self.faker.sentence() if random.choice([True, False]) else '',
        #         content=self.faker.text(max_nb_chars=500)
        #     )
        #     print(f'Created post {post.id}')
        #     for j in range(random.randint(0, 5)):
        #         image = PostImage.objects.create(
        #             post=post,
        #             image=f'img/image-{random.randint(1,10)}.jpg'
        #         )
        #         print(f'Created image {image.id} for post {post.id}')
        # # create replies
        # for i in range(10):
        #     post = Post.objects.order_by('?').first()
        #     reply = Reply.objects.create(
        #         user=random.choice(users),
        #         parent_post=post,
        #         content=self.faker.text(max_nb_chars=200)
        #     )
        #     print(f'Created reply {reply.id} for post {post.id}')
        # # create nested replies
        # for j in range(random.randint(0, 2)):
        #     parent_reply = Reply.objects.filter(parent_post=post).order_by('?').first()
        #     reply = Reply.objects.create(
        #         user=random.choice(users),
        #         parent_post=post,
        #         parent_reply=parent_reply,
        #         content=self.faker.text(max_nb_chars=200)
        #     )
        #     print(f'Created nested reply {reply.id} for reply {parent_reply.id}')    
        # # create likes for posts and replies
        # all_posts_and_replies = list(Post.objects.all()) + list(Reply.objects.all())
        # for item in all_posts_and_replies:
        #     for l in range(random.randint(0, 10)):
        #         user = random.choice(users)
        #         like, created = Like.objects.get_or_create(
        #             user=user,
        #             content_type=ContentType.objects.get_for_model(item),
        #             object_id=item.id
        #         )
        #         if created:
        #             print(f'Created like {like.id} for {item.__class__.__name__} {item.id}')
        #         else:
        #             print(f'Like for {item.__class__.__name__} {item.id} already exists for user {user.email}')
        # # create budgets
        # for user in users:
        #     categories = Categories.objects.filter(owner=user)
        #     for _ in range(5):
        #         budget = Budget.objects.create(
        #             name=self.faker.word(),
        #             limit=random.randint(500, 10000),
        #             start_date=timezone.now(),
        #             end_date=timezone.now() + timezone.timedelta(days=random.randint(30, 180)),
        #             budget_owner=user,
        #             spending_category=random.choice(self.categories)
        #         )
        #         print(f'Created budget {budget.id} for user {user.email}')
        # # create total budgets
        # for user in users:
        #     total_budget = TotalBudget.objects.create(
        #         name=self.faker.word(),
        #         limit=random.randint(1000, 50000),
        #         start_date=timezone.now(),
        #         end_date=timezone.now() + timezone.timedelta(days=random.randint(30, 365)),
        #         budget_owner=user,
        #     )
        #     print(f'Created total budget {total_budget.id} for user {user.email}')

        # create all information about Alice Doe
        self._create_alice_doe()
        self._create_spending_for_alice_doe()
        self._create_customised_category_for_alice_doe()
        self._create_post_for_alice_doe()
        self._create_like_for_alice_post()
        self._create_reply_for_alice_post()
        self._create_reply_for_a_reply()
        self._create_budget_for_alice_doe()
        self._create_delievery_address_for_alice_doe()
        print('finish seeding complete information for Alice Doe')
    
        #  ----------------------Helper Method----------------------
    
    def _create_specified_number_of_users(self):
        # create 99 users
        user_count = 0
        while user_count < Command.USER_COUNT:
            try:    
                self._create_user(user_count)
            except IntegrityError:
                continue
            user_count += 1
        
        
        # special user is the one who will have his/her own post, and who will like and reply Alice's post
        self.special_user = User.objects.exclude(email='alice.doe@example.org').order_by('?').first()

        print('finish seeding users')


    def _create_user(self, user_count):
        first_name = self.faker.unique.first_name()
        last_name = self.faker.unique.last_name()
        email = self._email(first_name, last_name)
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=f'this is the account of {first_name} {last_name}',
            gender= self.faker.random_element(elements=('Male', 'Female', 'Other', 'Prefer not to Say')),
            address=f'Street {first_name} {last_name}',
            phone_number= f'{user_count}',
            total_task_points=0,
            password=Command.PASSWORD,
            date_joined= self.start_date + timedelta(days=random.randint(0, self.days_between)),
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

        #  ----------------------Setup of Alice Doe----------------------

    def _create_alice_doe(self):

        self.alice_doe = User.objects.create_user(
            first_name="Alice",
            last_name="Doe",
            email='alice.doe@example.org',
            bio="This is Alice Doe's account",
            gender = 'Female',
            address = "Street ABC",
            phone_number= "01111111111",
            total_task_points=10,
            password=Command.PASSWORD,
            date_joined= datetime.now() - timedelta(days=7) # Calculate the date and time that is seven days before the current date and time
        )

        print("finish creating account of Alice")

        # Trigger the user_signed_up signal to create default categories for the new user
        create_default_categories(sender=None, request=None, user=self.alice_doe)

        self.common_category_list = Categories.objects.filter(owner=self.alice_doe, default_category=True)
       
    
    def _create_spending_for_alice_doe(self):
        # get the spending category alice doe has
        self.default_expenditure_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.EXPENDITURE) #default_category=True)
        self.default_income_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.INCOME) # default_category=True

        POSSIBILITY_OF_HAVING_FILE = 0.1 
        
        for i in range(1, 41):
            is_expenditure = i <= 20

            # Determine spending type and file content based on expenditure/income
            if is_expenditure:
                spending_type = Spending_type.EXPENDITURE
                file_content = f"This is the file content{i} for expenditure".encode('utf-8')
                spending_category = self.default_expenditure_category_list.order_by('?').first()
            else:
                spending_type = Spending_type.INCOME
                file_content = f"This is the file content{i} for income".encode('utf-8')
                spending_category=self.default_income_category_list.order_by('?').first()

             # Create the spending object
            spending = Spending.objects.create(
                    title=f"Spending {i}",
                    spending_owner=self.alice_doe,
                    amount=random.random() * 100,
                    descriptions=f"This is spending {i}",
                    date=self.start_date + timedelta(days=random.randint(0, self.days_between)),
                    spending_type=spending_type,
                    spending_category=spending_category
            )

            # Create the spending file object if necessary
            if random.random() < POSSIBILITY_OF_HAVING_FILE:
                file_name = f"file{i}.txt"
                file_path = f'user_files/{file_name}'

                # Save the file using Django's default storage
                default_storage.save(file_path, ContentFile(file_content))

                # Create the SpendingFile object
                spending_file = SpendingFile.objects.create(
                    spending=spending, file=file_path
                )

        print("finished creating expenditures and incomes")

    
    def _create_customised_category_for_alice_doe(self):

        Categories.objects.create(
            name="Alice's Customised Expenditure Category",
            owner=self.alice_doe,
            categories_type=Spending_type.EXPENDITURE,
        )

        Categories.objects.create(
            name="Alice's Customised Income Category",
            owner=self.alice_doe,
            categories_type=Spending_type.INCOME,
        )
        print("finish creating customised category")

    def _create_post_for_alice_doe(self):
        
        self.alice_post = Post.objects.create(
                            user=self.alice_doe,
                            title='Demonstration for forum post function',
                            content="This picture shows the home page of the application.",
                            post_date=self.start_date,
                        )

        # create image for the post
        with open('static/seed_image/home_page.png', 'rb') as f:
            image = SimpleUploadedFile('seed_demonstration_image.png', f.read(), content_type='image/png')
            f.close()

        PostImage.objects.create(
            post=self.alice_post,
            file=image
        )

        print("finish creating post for Alice Doe")

    def _create_like_for_alice_post(self):
        like = Like.objects.create(
                user=self.special_user, 
                content_object=self.alice_post
        )
        print("finish adding a like to Alice's post")
    
    def _create_reply_for_alice_post(self):

        self.special_user_reply = Reply.objects.create(
            user=self.special_user,
            parent_post=self.alice_post,
            content='This is demo for reply function.',
            reply_date=datetime.now()
        )
        like = Like.objects.create(
            user=self.alice_doe,
            content_object=self.special_user_reply
        )
        print("finish adding a reply to Alice's post and a like to that reply")
    
    def _create_reply_for_a_reply(self):
        reply_of_reply = Reply.objects.create(
                            user=self.alice_doe,
                            parent_post=self.alice_post,
                            content='Received. This is demo for replying a reply function.',
                            reply_date=datetime.now()
        )
        like = Like.objects.create(
            user=self.special_user,
            content_object=reply_of_reply
        )
        print("finish adding a reply a reply and a like to that reply")

        

    def _create_budget_for_alice_doe(self):

        # create overall budget
        self.alice_total_budget= TotalBudget.objects.create(
            limit=6000,
            start_date=datetime.today().replace(day=1),
            end_date=datetime.today().replace(day=30),
            budget_owner=self.alice_doe
        )

        # create budget for each individual budget
        for category_budget in self.default_expenditure_category_list:
            Budget.objects.create(
                limit=500,
                budget_owner=self.alice_doe,
                spending_category=category_budget
            )
        
        print("finish creating budgets")
    
    def _create_delievery_address_for_alice_doe(self):
        DeliveryAddress.objects.create(
            user=self.alice_doe,
            address=self.alice_doe.address,
            phone_number=self.alice_doe.phone_number
        )
        print("finish creating delivery address")