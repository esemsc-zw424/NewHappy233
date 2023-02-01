from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

# Create your models here.
class Spending_type(models.TextChoices):
    Expenditure = 'Expenditure'
    Income = 'Income'



class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.username

class Categories(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Spending(models.Model):
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
        default=Spending_type.Expenditure,
        blank = False,
    )

    spending_category = models.ForeignKey(Categories, on_delete=models.CASCADE, default=None) #this refers to the category of the spending
