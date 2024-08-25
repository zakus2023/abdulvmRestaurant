from django.db import models
from vendors.models import Vendor

# Create your models here.

class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
    
    def clean(self):
        self.category_name = self.category_name.capitalize()
    



class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    food_title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foodimages', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_title


