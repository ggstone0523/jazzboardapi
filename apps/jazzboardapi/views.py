from .models import text, BearerAuthentication, comment
from .serializers import TextSerializer, CommentsSerializer
from rest_framework import generics, permissions, status
from .permissions import IsOwnerOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

# Create your views here.
class TextList(generics.ListCreateAPIView):
    queryset = text.objects.all()
    serializer_class = TextSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TextDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = text.objects.all()
    serializer_class = TextSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

class logOut(APIView):

    def delete(self, request, format=None):
        try:
            token = Token.objects.get(key=request.data['key'])
        except Token.DoesNotExist:
            return Response({ "To log out, you need to log in" }, status=status.HTTP_404_NOT_FOUND)
        token.delete()
        return Response({ "logout success" }, status=status.HTTP_204_NO_CONTENT)

class signup(APIView):

    def post(self, request, format=None):
        try:
            user = User.objects.create_user(request.data['name'], request.data['email'], request.data['password'])
        except:
            return Response({ "signup must include name, email, password" }, status=status.HTTP_404_NOT_FOUND)
        user.save()
        return Response({ "signup success" }, status=status.HTTP_204_NO_CONTENT)

class accountDelete(APIView):

    def delete(self, request, format=None):
        try:
            username = Token.objects.get(key=request.data['key'])
        except:
            return Response({ "To accountDelete, you need to sign in" }, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(username=username.user)
        except:
            return Response({ "no users" }, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({ "delete account success" }, status=status.HTTP_204_NO_CONTENT)

class CommentsList(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, page, format=None):
        try:
            Comment = comment.objects.filter(text__id=page)
        except comment.DoesNotExist:
            return Response({ "comments not exist" }, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentsSerializer(Comment, many=True)
        return Response(serializer.data)

    def post(self, request, page, format=None):
        serializer = CommentsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                texts = text.objects.get(id=page)
            except text.DoesNotExist:
                return Response({ "There's no page" }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(owner=request.user, text=texts)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = comment.objects.all()
    serializer_class = CommentsSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]