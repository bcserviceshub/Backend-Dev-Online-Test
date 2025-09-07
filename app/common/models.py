from django.db import models

from django.db import models
from uuid import uuid4

# Create your models here.
class Category(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'

class Product(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    vendor = models.UUIDField(default=uuid4)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'products'
