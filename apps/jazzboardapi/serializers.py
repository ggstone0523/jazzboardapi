from rest_framework import serializers
from django.contrib.auth.models import User
from .models import text

class UserSerializer(serializers.ModelSerializer):
    text = serializers.PrimaryKeyRelatedField(many=True, queryset=text.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'text']

class TextSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = text
        fields = ['id', 'title', 'content', 'create_date', 'owner']