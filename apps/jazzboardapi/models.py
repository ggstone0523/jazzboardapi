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
    hidden = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)

class comment(models.Model):
    content = models.TextField()
    owner = models.ForeignKey('auth.User', related_name='comment', on_delete=models.CASCADE)
    text = models.ForeignKey(text, related_name='comment', on_delete=models.CASCADE)
    toComment = models.ForeignKey('self', related_name='comment', on_delete=models.CASCADE, null=True, blank=True)
    hidden = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return '%d' % (self.id)