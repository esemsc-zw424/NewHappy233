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
    USER_COUNT = 98

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

        self.start_date = (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        self.end_date = datetime.now()
        self.days_between = (self.end_date - self.start_date).days
        self.faker.unique.clear()
       

    def handle(self, *args, **options):
        
        # create all users and related information, ALice Doe is created here because users need to information about Alice
        print('Start seeding, please wait about 20 seconds... ')
        self._create_alice_doe()
        self._create_specified_number_of_users()
        
        self._create_spendings_for_all_users()
        

        self._create_posts_for_all_users()
        self._create_total_budget_for_all_users()
        self._create_budget_for_all_users()
        
        # create all information about Alice Doe        
        self._create_spending_for_alice_doe()
        self._create_customised_category_for_alice_doe()
        self._create_a_post_made_by_special_user() # it is meant to put here in order to display in the first page in pagination
        self._create_post_for_alice_doe()
        self._create_like_for_alice_post()
        self._create_reply_for_alice_post()
        self._create_reply_for_a_reply()
        self._create_budget_for_alice_doe()
        self._create_delievery_address_for_alice_doe()

        
        print('Everything is done, enjoy the application :) ')
    
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
        self.special_user = User.objects.exclude(email='Alice.Doe@example.org').order_by('?').first()
        self.users=User.objects.exclude(email='Alice.Doe@example.org')
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


    def _create_spendings_for_all_users(self):
        
        # since all users all have same default categories, just exploit Alice Doe to get all common categories.
        self.default_expenditure_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.EXPENDITURE, default_category=True)
        self.default_income_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.INCOME, default_category=True)
        POSSIBILITY_OF_HAVING_SPENDING = 0.6
        # random.choice([Spending_type.EXPENDITURE, Spending_type.INCOME])

        for user in self.users:
            if random.random() < POSSIBILITY_OF_HAVING_SPENDING:

                # choose spending_type and spending_category
                if random.choice([Spending_type.EXPENDITURE, Spending_type.INCOME]) == Spending_type.EXPENDITURE:
                    spending_type = Spending_type.EXPENDITURE
                    spending_category = self.default_expenditure_category_list.order_by('?').first()
                else:
                    spending_type = Spending_type.INCOME
                    spending_category=self.default_income_category_list.order_by('?').first()

                # generate spending
                for i in range(random.randint(1, 10)):
                    spending = Spending.objects.create(
                    title=f"Spending {i}",
                    spending_owner=user,
                    amount=random.random() * 100,
                    descriptions=f"This is spending {i}",
                    date=self.start_date + timedelta(days=random.randint(0, self.days_between)),
                    spending_type=spending_type,
                    spending_category=spending_category
                    )
   

    # this is a post of special user, the purpose is to make sure that Alice can see others' post as well.
    def _create_a_post_made_by_special_user(self):
        self.special_user_post=Post.objects.create(
                            user=self.special_user,
                            title='Alice, Can you see my post?',
                            content="I am sure you can!",
                        )
         # create image for the post
        with open('static/seed_image/question_mark.png', 'rb') as f:
            image = SimpleUploadedFile('seed_demonstration_image_2.png', f.read(), content_type='image/png')
            f.close()

        PostImage.objects.create(
            post=self.special_user_post,
            file=image
        )
        print('finish adding post of the special user')
    

    def _create_posts_for_all_users(self):
        POSSIBILITY_OF_POST = 0.9 #0.12
        for user in self.users:
            if random.random() <= POSSIBILITY_OF_POST:
                Post.objects.create(
                user=user,
                title= f'post of {user.last_name}',
                content= f'content writteb by {user.last_name}',
                )
        print('finish creating posts for all user')
    
    def _create_total_budget_for_all_users(self):
        for user in self.users:
            TotalBudget.objects.create(
                limit=1200,
                start_date=datetime.today().replace(day=1),
                end_date=datetime.today().replace(day=30),
                budget_owner=user
        )
        print('finish createing total budget for all users')
    
    def _create_budget_for_all_users(self):
        POSSIBILITY_OF_HAVING_CATEGORY_BUDGET= 0.5

        for user in self.users:
            if random.random() <= 0.5:
                if random.choice([Spending_type.EXPENDITURE, Spending_type.INCOME]) == Spending_type.EXPENDITURE:
                    spending_category = self.default_expenditure_category_list
                else:
                    spending_category = self.default_income_category_list

                for category_budget in spending_category:
                    Budget.objects.create(
                        limit=120,
                        budget_owner=user,
                        spending_category=category_budget
                    )





    #  ----------------------helper method for the setup of Alice Doe----------------------

    def _create_alice_doe(self):

        self.alice_doe = User.objects.create_user(
            first_name="Alice",
            last_name="Doe",
            email='Alice.Doe@example.org',
            bio="This is Alice Doe's account",
            gender = 'Female',
            address = "Street ABC",
            phone_number= "01111111111",
            total_task_points=0,
            password=Command.PASSWORD,
            date_joined= datetime.now() - timedelta(days=7) # Calculate the date and time that is seven days before the current date and time
        )

        print("finish creating account of Alice")

        # Trigger the user_signed_up signal to create default categories for the new user
        create_default_categories(sender=None, request=None, user=self.alice_doe)

        self.common_category_list = Categories.objects.filter(owner=self.alice_doe, default_category=True)
       
    
    def _create_spending_for_alice_doe(self):
        # get the spending category alice doe has
        self.alice_expenditure_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.EXPENDITURE) #default_category=True)
        self.alice_income_category_list = Categories.objects.filter(owner=self.alice_doe, categories_type=Spending_type.INCOME) # default_category=True

        POSSIBILITY_OF_HAVING_FILE = 0.1 
        
        for i in range(1, 41):
            is_expenditure = i <= 20

            # Determine spending type and file content based on expenditure/income
            if is_expenditure:
                spending_type = Spending_type.EXPENDITURE
                file_content = f"This is the file content{i} for expenditure".encode('utf-8')
                spending_category = self.alice_expenditure_category_list.order_by('?').first()
            else:
                spending_type = Spending_type.INCOME
                file_content = f"This is the file content{i} for income".encode('utf-8')
                spending_category=self.alice_income_category_list.order_by('?').first()

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
    
        # create Alice's post
        self.alice_post = Post.objects.create(
                            user=self.alice_doe,
                            title='Demonstration for forum post function',
                            content="This picture shows the home page of the application.",
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
        )
        like = Like.objects.create(
            user=self.special_user,
            content_object=reply_of_reply
        )
        print("finish adding a reply a reply and a like to that reply")

        

    def _create_budget_for_alice_doe(self):

        # create overall budget
        self.alice_total_budget= TotalBudget.objects.create(
            limit=360,
            start_date=datetime.today().replace(day=1),
            end_date=datetime.today().replace(day=30),
            budget_owner=self.alice_doe
        )

        # create budget for each individual budget
        for category_budget in self.alice_expenditure_category_list:
            Budget.objects.create(
                limit=30,
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