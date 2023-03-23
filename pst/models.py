from datetime import date, timedelta
from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os



class Spending_type(models.TextChoices):
    EXPENDITURE = "Expenditure"
    INCOME = "Income"


class UserManager(BaseUserManager):


    def create_user(self, first_name, last_name, email, password, **extra_fields):

        email = self.normalize_email(email)
        user = self.model(first_name=first_name,
                          last_name=last_name, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user



    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        user = self.create_user(first_name, last_name, email, password, **extra_fields)
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
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=100, blank=True)
    total_task_points = models.IntegerField(default=0)
    consecutive_login_days = models.IntegerField(default=1)
    logged_in_once_daily = models.BooleanField(default = False)
    cur_login_day = models.DateTimeField(auto_now_add=True)


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def increase_total_task_points(self, value):
        self.total_task_points += value
        self.save()

    def decrease_total_task_points(self, value):
        self.total_task_points -= value
        self.save()

    def get_number_days_from_register(self):
        date_joined = self.date_joined
        num_days = (timezone.now().day - date_joined.day) + 1
        if  num_days == 0:
            num_days = 1

        return num_days
    
    def check_already_logged_in_once_daily(self):
        # if over a day since last login
        if timezone.now().day - self.cur_login_day.day >= 1:
            self.logged_in_once_daily = False
            self.save()
        else:
            self.logged_in_once_daily = True
            self.save()


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


class Day(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Day {self.number}"


class DailyTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    days = models.ManyToManyField(Day, through='DailyTaskStatus')

    def get_day(self):
        return self.days.all()

    def get_user(self):
        return self.user


    def __str__(self):
        return f"{self.user.email}'s daily tasks"


class TaskType(Enum):
    LOGIN = 'Login'
    POST = 'Post'

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class DailyTaskStatus(models.Model):
    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    task_points = models.IntegerField(default=0)
    task_type = models.CharField(choices=TaskType.choices(), default=TaskType.LOGIN.name, max_length=10)

    def save(self, *args, **kwargs):
        user = self.task.user  
        user.total_task_points += self.task_points
        user.save()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('task', 'day', 'task_type')


class Spending(models.Model):
    title = models.CharField(max_length=30, blank=False)
    spending_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spendingOwner') 
    amount = models.DecimalField(  
        blank=False,
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ]
    )
    descriptions = models.CharField(blank=True, max_length=500)
    date = models.DateField(blank=False)
    spending_type = models.CharField(
        max_length=30,
        choices=Spending_type.choices,
        default=Spending_type.EXPENDITURE,
        blank=False,
    )
    spending_category = models.ForeignKey(Categories, on_delete=models.CASCADE, default='', related_name='category', blank=False)  
    

class SpendingFile(models.Model):
    spending = models.ForeignKey(
        Spending, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        null=True,
        blank=True,
        upload_to='user_files/'
    )




class Budget(models.Model):
    # name = models.CharField(max_length=100, default='')
    limit = models.PositiveIntegerField()
    # start_date = models.DateField(default=timezone.now)
    # end_date = models.DateField(default=timezone.now)
    budget_owner = models.ForeignKey(  # user which this budget belongs to
        User, on_delete=models.CASCADE
    )
    spending_category = models.ForeignKey(Categories, on_delete=models.CASCADE, default='', related_name='budget_spending_category', blank=True)





class Reward(models.Model):
    name = models.CharField(max_length=50)
    points_required = models.IntegerField(default=0)
    image = models.FileField(
        null=True,
        blank=True,
        upload_to='rewards/'
    )
    default_image = models.FileField(upload_to='rewards/', default='rewards/default_reward_image.jpg')

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

# Abstract base model for both reply and post
class BasePostReplyModel(models.Model):

    # Some common fields
    # User that this reply or post belongs to
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s')

    # Content of the Reply or Post
    content = models.TextField(blank=False)

    # Likes other user gave
    likes = GenericRelation('Like')

    # Date when this reply or post create 
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True



# this model is for posts in the forum
class Post(BasePostReplyModel):

    # this field store the title of the post
    # the title are not expected to be very long and can be empty if user don't want to have a title
    title = models.CharField(
        blank = True,
        max_length= 150,
    )

    def __str__(self):
        return self.content


def validate_file_extension(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if not ext.lower() in valid_extensions:
            raise ValidationError('File format not supported.')

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    file = models.ImageField(
        null=True,
        blank=True,
        upload_to='post_images/',
        validators=[validate_file_extension],
    )

@receiver(pre_delete, sender=SpendingFile)
@receiver(pre_delete, sender=PostImage)
def delete_file(sender, instance, **kwargs):
    # delete the file when the related object is deleted
    if instance.file:
        path = instance.file.path
        if os.path.exists(path):
            os.remove(path)

# this model is for replies under a post
class Reply(BasePostReplyModel):

    # this field store the post where this reply belongs to
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reply', blank = False)

    # if this reply is the reply for another reply under the same post, then this field will be use to mark the parent reply
    parent_reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

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

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=False)
    phone_number = models.CharField(max_length=15, blank=True)



class TotalBudget(models.Model):
    limit = models.PositiveIntegerField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)  # make end_date optional
    budget_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='total_budgets'  # add related name
    )