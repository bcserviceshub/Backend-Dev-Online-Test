from rest_framework import serializers
from ..common.models import (Category, Product)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'vendor']
