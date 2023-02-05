from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, email, password):
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email)
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
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']



    def __str__(self):
        return self.email


# Create your models here.

class Spending(models.Model):

    class Spending_type(models.TextChoices):
        EXPENDITURE = "Expenditure"
        INCOME = "Income"

    title = models.CharField( # title for the spending
        max_length=30,
        blank=False
    ) 

    spending_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spendingOwner', blank = False) #this refers to the user when create this spending

    amount = models.IntegerField( # this refers to the amount this user spent or gained
        blank=False,
        validators=[
            MaxValueValidator(10000000),
            MinValueValidator(0),
        ]
    )

    descriptions = models.CharField( # comments for the spending
        blank = True,
        max_length=500,
    )

    date = models.DateField( # data of the spending
        blank = False,
    )

    spending_type = models.CharField( # this refers to the spending type 
        max_length=30,
        choices=Spending_type.choices,
        default=Spending_type.EXPENDITURE,
        blank = False,
    )

    # spending_category = models.ForeignKey(Categories, on_delete=models.CASCADE) #this refers to the category of the spending

    file = models.FileField( # optional file/images could be provided to the spending
        null=True, 
        blank=True,
    ) 

    
    
    
 
