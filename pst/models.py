from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Spending(models.Model):
    title = models.CharField(max_length=20, blank=False)
    amount = models.IntegerField(blank=False, validators=[MinValueValidator(0)])
    #category = models.ForeignKey(Category, blank=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=100, blank=True)
    file = models.FileField(null=True, blank=True) 
    image = models.ImageField(null=True, blank=True)

    
