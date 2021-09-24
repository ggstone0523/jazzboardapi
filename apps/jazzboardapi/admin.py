from django.contrib import admin
from .models import text, comment, chat

# Register your models here.
admin.site.register(text)
admin.site.register(comment)
admin.site.register(chat)