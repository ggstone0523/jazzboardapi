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
        fields = ['id', 'content', 'hidden', 'anonymous', 'owner', 'text', 'toComment']

class TextsSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = text
        fields = ['id', 'title', 'hidden', 'anonymous', 'content', 'create_date', 'owner']

class TextCommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comment = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = text
        fields = ['id', 'title', 'hidden', 'anonymous', 'content', 'create_date', 'owner', 'comment']

class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    toOwner = serializers.ReadOnlyField(source='toOwner.username')

    class Meta:
        model = chat
        fields = ['id', 'content', 'owner', 'toOwner']