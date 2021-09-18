from rest_framework import serializers
from django.contrib.auth.models import User
from .models import comment, text

class UserSerializer(serializers.ModelSerializer):
    text = serializers.PrimaryKeyRelatedField(many=True, queryset=text.objects.all())
    comments = serializers.PrimaryKeyRelatedField(many=True, queryset=comment.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'text', 'comments']

class TextSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comments = serializers.PrimaryKeyRelatedField(many=True, queryset=comment.objects.all())

    class Meta:
        model = text
        fields = ['id', 'title', 'content', 'create_date', 'owner', 'comments']

class CommentsSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    text = serializers.ReadOnlyField(source='text.id')

    class Meta:
        model = comment
        fields = ['id', 'content', 'owner', 'text']