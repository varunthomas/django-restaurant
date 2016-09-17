from __future__ import unicode_literals
from django_countries.fields import CountryField
from django.db import models
from django_countries import countries
# Create your models here.

class Register(models.Model):
    TYPE_OF_USER = ((0, 'Customer'), (1, 'Owner'))
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=30)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    mobilenumber = models.CharField(max_length=30)
    typeofuser = models.BooleanField('I am a/an:')
    first_time_logged_in = models.IntegerField(default=0)

class Restaurant(models.Model):
    #ip = models.CharField(max_length=45)
    owner_id=models.IntegerField()
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = CountryField(choices=list(countries))
    contact = models.CharField(max_length=15)
    def __str__(self):
        return self.name

    #zipcode = models.CharField(max_length=6)


class Sale(models.Model):
    user_id = models.IntegerField()
    rest_id = models.IntegerField()
    food_id = models.IntegerField()
    quantity = models.IntegerField()
    rating = models.IntegerField()

class Menu(models.Model):
    rest_id = models.IntegerField()
    food_id = models.IntegerField()


class Category(models.Model):
    category = models.CharField(max_length = 50)
    content = models.CharField(max_length= 50, null = True,blank=True)
    preparation = models.CharField(max_length= 50, null=True, blank=True)
    time = models.CharField(max_length=50,null=True, blank=True)


class FoodItems(models.Model):
    rest_id = models.IntegerField()
    name = models.CharField(max_length=200)
    time = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    content = models.CharField(max_length=50)
    preparation = models.CharField(max_length=50)
    comment = models.CharField(max_length=300)
    price = models.IntegerField()
    image = models.FileField(upload_to='images')

class Order(models.Model):
    food_item = models.CharField(max_length=200)
    rest_id = models.IntegerField()
    done = models.IntegerField()
    user_id = models.IntegerField()
    rating = models.IntegerField()
    table_num = models.IntegerField()

