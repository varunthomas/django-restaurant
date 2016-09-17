from django.contrib import admin
from .models import Register, Restaurant, FoodItems, Category
# Register your models here.

admin.site.register(Register)
admin.site.register(Restaurant)
admin.site.register(FoodItems)
admin.site.register(Category)
