from rest_framework import serializers
from django.contrib.auth.models import User
from .models import comment, text, chat

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    text = serializers.ReadOnlyField(source='text.id')
    toComment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = comment
        fields = ['id', 'content', 'owner', 'text', 'toComment']

class TextSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comment = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = text
        fields = ['id', 'title', 'content', 'create_date', 'owner', 'comment']

class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    toOwner = serializers.ReadOnlyField(source='toOwner.username')

    class Meta:
        model = chat
        fields = ['id', 'content', 'owner', 'toOwner']