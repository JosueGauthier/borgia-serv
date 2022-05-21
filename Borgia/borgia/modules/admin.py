from django.contrib import admin

# Register your models here.

from .models import Category,CategoryProduct

admin.site.register(Category),
admin.site.register(CategoryProduct),

