from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator, MinLengthValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
  email = models.EmailField(unique=True, blank=False)
 
  def __str__(self):
    return self.email


class Categories(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #django.core.exceptions.makemigration时没被安装不知道为什么
    # ImproperlyConfigured: AUTH_USER_MODEL refers to model 'pst.User' that has not been installed
    