from django.db import models
from rest_framework import authentication

# Create your models here.
class BearerAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'

class text(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='text', on_delete=models.CASCADE)