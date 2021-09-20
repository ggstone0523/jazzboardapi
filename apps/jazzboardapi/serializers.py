from rest_framework import serializers
from django.contrib.auth.models import User
from .models import comment, text, chat, comComment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TextSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = text
        fields = ['id', 'title', 'content', 'create_date', 'owner']

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    text = serializers.ReadOnlyField(source='text.id')

    class Meta:
        model = comment
        fields = ['id', 'content', 'owner', 'text']

class ComCommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comment = serializers.ReadOnlyField(source='comment.id')

    class Meta:
        model = comComment
        fields = ['id', 'content', 'owner', 'comment']

class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    toOwner = serializers.ReadOnlyField(source='toOwner.username')

    class Meta:
        model = chat
        fields = ['id', 'content', 'owner', 'toOwner']