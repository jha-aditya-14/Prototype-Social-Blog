from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
# Create your models here.

class User(AbstractUser):
    # first_name= models.CharField(max_length=100, default='NA')
    img=models.ImageField(upload_to='pics', null=True)
    # contact = models.BigIntegerField(null=True)
    username = None
    email= models.EmailField(unique=True, max_length=200)
    # password= models.CharField(max_length=100, default='NA')
    # createdAt=models.DateTimeField(null=False)
    updatedAt = models.DateTimeField(null=True)
    # lastLogin = models.DateTimeField(null=True)
    # last_name=models.CharField(max_length=100)
    objects= UserManager()
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

class Blogs(models.Model):
    blogName = models.CharField(max_length=300)
    Description = models.CharField(max_length=1500)
    img=models.ImageField(upload_to='blogPics' , null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt=models.DateTimeField(null=False)
    updatedAt = models.DateTimeField(null=True)
    
class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(null=True, default='NA')
    city = models.CharField(null=True, default='NA')
    country = models.CharField(null=True, default='NA')
    postalCode = models.IntegerField(null=True)
    aboutMe=models.CharField(null=True, default='NA')
    userName =models.CharField(null=True, default='NA')



