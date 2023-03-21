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
    total_task_points = models.IntegerField(default=0)
    consecutive_login_days = models.IntegerField(default=1)
    logged_in_once_daily = models.BooleanField(default = False)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def increase_total_task_points(self, value):
        self.total_task_points += value
        self.save()

    def decrease_total_task_points(self, value):
        self.total_task_points -= value
        self.save()

    def get_total_task_points(self):
        return "task credits: " + str(self.total_task_points)

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def toggle_follow(self, followee):
        """Toggles whether self follows the given followee."""

        if followee==self:
            return
        if self.is_following(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def is_following(self, user):
        return user in self.followees.all()
    
    def get_is_follow_text(self, user):
        return "Unfollow" if self.is_following(user) else "Follow"

    def follower_count(self):
        return self.followers.count()

    def followee_count(self):
        return self.followees.count()

    def username(self):
        return self.first_name + ' ' + self.last_name


    @property

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

    # def mark_received(self, day):
    #     status = DailyTaskStatus.objects.get(task=self, day=day)
    #     status.received = True
    #     status.save()
    #
    # def set_task_points(self, day, points):
    #     status = DailyTaskStatus.objects.get(task=self, day=day)
    #     status.points = points
    #     status.save()
    #
    # def get_task_status(self, day):
    #     status = DailyTaskStatus.objects.get(task=self, day=day)
    #     return status.received
    #
    # def get_task_points(self, day):
    #     status = DailyTaskStatus.objects.get(task=self, day=day)
    #     return status.points

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
        user = self.task.user  # Assuming that there is a 'user' foreign key field in the 'DailyTask' model
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

    # this field store the likes from other user
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

    # this field store the likes from other user
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


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    phone_number = models.IntegerField(blank=True)

# class TotalBudget(models.Model):
#     name = models.CharField(max_length=100, default='')
#     limit = models.PositiveIntegerField()
#     start_date = models.DateField(default=timezone.now)
#     end_date = models.DateField(default=timezone.now)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     budget_owner = models.ForeignKey(  # user which this budget belongs to
#         User, on_delete=models.CASCADE
#     )

class TotalBudget(models.Model):
    # name = models.CharField(max_length=100, default='')
    limit = models.PositiveIntegerField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)  # make end_date optional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    budget_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='total_budgets'  # add related name
    )