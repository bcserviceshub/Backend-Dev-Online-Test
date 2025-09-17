from django.contrib import admin
from .common.models import Product, Category

admin.site.register(Product)
admin.site.register(Category)