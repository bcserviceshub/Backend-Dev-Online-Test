import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from app.common.models import Product, Category
from django.db import transaction

@transaction.atomic
def populate_db():
    cat_data = {
        'name': 'Fashion'
    }
    cat = Category.objects.create(**cat_data)

    prod_data = {
        'category': cat,
        'name': 'Levi Jeans',
        'price': 12.99,
        'vendor': ''
    }
    prod = Product.objects.create(**prod_data)

populate_db()
