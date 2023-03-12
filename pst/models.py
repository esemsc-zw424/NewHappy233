from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import os

class Spending_type(models.TextChoices):
    EXPENDITURE = "Expenditure"
    INCOME = "Income"


class UserManager(BaseUserManager):


    def create_user(self, first_name, last_name, email, password, **extra_fields):

        email = self.normalize_email(email)
        user = self.model(first_name=first_name,
                          last_name=last_name, email=email)
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        user = self.create_user(first_name, last_name, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user




class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(blank=False, unique=False, max_length=50)
    last_name = models.CharField(blank=False, unique=False, max_length=50)
    bio = models.TextField(max_length=500, blank=True)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Perfer not to say')
    ]
    gender = models.CharField(
        max_length=20, choices=GENDER_CHOICES, blank=True)
    phone_regex = RegexValidator(regex=r'^\d{10,15}$', message="Phone number must be entered in the format: '9999999999' and maximum 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    address = models.CharField(max_length=100, blank=True)

    reward_points = models.IntegerField(default=0)
    consecutive_login_days = models.IntegerField(default=1)
    logged_in_once_daily = models.BooleanField(default = False)
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def __str__(self):
        return self.email

class Categories(models.Model):


    name = models.CharField( # name of the category
        max_length=100
    )

    owner = models.ForeignKey(  # user which this category belongs to
        User, on_delete=models.CASCADE
    )

    categories_type = models.CharField(  # the type of this category belongs to, for example expenditure or income
        max_length=30,
        choices=Spending_type.choices,
        default=Spending_type.EXPENDITURE,
        blank=False,
    )

    default_category = models.BooleanField(
        default=False,
        help_text=(
            'Designates this category is a default category or not'
            'default category are not expected to be modified'
        )
    )

    def __str__(self):
        return self.name



class Spending(models.Model):

    title = models.CharField(  # title for the spending
        max_length=30,
        blank=False
    )

    spending_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spendingOwner') #this refers to the user when create this spending

    amount = models.IntegerField(  # this refers to the amount this user spent or gained
        blank=False,
        validators=[
            MaxValueValidator(10000000),
            MinValueValidator(0),
        ]
    )

    descriptions = models.CharField(  # comments for the spending
        blank=True,
        max_length=500,
    )

    date = models.DateField( # date of the spending
        blank = False,
    )

    spending_type = models.CharField(  # this refers to the spending type
        max_length=30,
        choices=Spending_type.choices,
        default=Spending_type.EXPENDITURE,
        blank=False,
    )


    spending_category = models.ForeignKey(Categories, on_delete=models.CASCADE, default='', related_name='category',
                                          blank=False)  # this refers to the category of the spending



class SpendingFile(models.Model):
    spending = models.ForeignKey(
        Spending, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        null=True,
        blank=True,
        upload_to='user_files/'
    )


class Budget(models.Model):
    name = models.CharField(max_length=100)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    # start_date = models.DateField()
    # end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    budget_owner = models.ForeignKey(  # user which this budget belongs to
        User, on_delete=models.CASCADE
    )


class Reward(models.Model):
    name = models.CharField(max_length=50)
    points_required = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

# this model is for posts in the forum
class Post(models.Model):

    # this field store the user when sent this post
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post', blank = False)

    # this field store the title of the post
    # the title are not expected to be very long and can be empty if user don't want to have a title
    title = models.CharField(
        blank = True,
        max_length= 150,
    )

    # this field store the content of the post
    content = models.TextField( # for stroing the content of the post
        blank = False,
    )

    # this field store the number of likes other user gave
    # likes = models.IntegerField( # this store the number of likes other user gave
    #     default=0,
    #     blank = False,
    #     validators=[
    #         MinValueValidator(0),
    #     ]
    # )
    likes = GenericRelation('Like')

    # this field store the date and time when this post sent
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


def validate_file_extension(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if not ext.lower() in valid_extensions:
            raise ValidationError('File format not supported.')

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='post_images/',
        validators=[validate_file_extension],
    )

# this model is for replies under a post
class Reply(models.Model):

    # this field store the user when sent this reply
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reply', blank = False)

    # this field store the post where this reply belongs to
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reply', blank = False)

    # if this reply is the reply for another reply under the same post, then this field will be use to mark the parent reply
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    # this field store the content of the post
    # and the reason why the content for reply is charfield is becasue reply are expect to have a shorter length
    content = models.TextField(
        blank = False,
    )

    # this field store the number of likes other user gave
    # likes = models.IntegerField(
    #     default=0,
    #     blank = False,
    #     validators=[
    #         MinValueValidator(0),
    #     ]
    # )
    likes = GenericRelation('Like')

    # this field store the date and time when this reply sent
    reply_date = models.DateTimeField(auto_now_add=True, blank = False)

    def __str__(self):
        return self.content

class Like(models.Model):
    # used GenericForeignKey so like can be applied on both reply and post model

    # user who gaves this like
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # this refers to what type of model this object this is
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    # this refers to a specific object under this model
    object_id = models.PositiveIntegerField()

    # shortcut property that combines content_type and object_id to return the actual object being liked
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = [['user', 'content_type', 'object_id']]
