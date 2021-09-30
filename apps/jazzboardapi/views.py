from .models import text, BearerAuthentication, comment, chat
from .serializers import UserSerializer, TextsSerializer, CommentSerializer, ChatSerializer, TextCommentSerializer
from rest_framework import generics, permissions, status
from .permissions import IsOwnerOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q
from .sortComm import sortedComment

# Create your views here.
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TextList(generics.ListCreateAPIView):
    queryset = text.objects.all()
    serializer_class = TextsSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        user = request.user
        try:
            if not isinstance(user, AnonymousUser):
                texts = text.objects.filter(
                    Q(hidden=False)
                    |
                    Q(owner=user)
                )
            else:
                texts = text.objects.filter(hidden=False)
        except:
            return Response({'dosent have text'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TextsSerializer(texts, many=True)
        serializer_data = serializer.data
        for i in range(len(serializer_data)):
            if (serializer_data[i]['anonymous'] == True) and (serializer_data[i]['owner'] != request.user.username):
                serializer_data[i]['owner'] = '익명'
        return Response(serializer_data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TextDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = text.objects.all()
    serializer_class = TextCommentSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, pk, format=None):
        try:
            texts = text.objects.get(pk=pk)
        except:
            return Response({'dosent have text'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TextCommentSerializer(texts)
        serializer_data = serializer.data
        serializer_data['comment'] = sortedComment(serializer_data['comment'], request.user.username)
        if (serializer_data['anonymous'] == True) and (serializer_data['owner'] != request.user.username):
            serializer_data['owner'] = '익명'
        return Response(serializer_data)

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
            return Response({ "signup must include name, email, password" }, status=status.HTTP_400_BAD_REQUEST)
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

class CommentList(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, format=None):
        try:
            serializer = CommentSerializer(data=request.data)
        except:
            return Response({"you must post data"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            try:
                textN = request.data['textN']
                texts = text.objects.get(id=textN)
            except text.DoesNotExist:
                return Response({ "There's no text" }, status=status.HTTP_404_NOT_FOUND)
            try:
                tocomment = request.data['toComment']
                try:
                    arr = comment.objects.filter(
                        Q(text__id = textN)
                        & 
                        Q(id = tocomment)
                    )
                    if len(arr) == 0:
                        raise Exception()
                except:
                    return Response({"didnt match text and comment"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            try:
                comments = comment.objects.get(id = tocomment)
                serializer.save(owner=request.user, text=texts, toComment=comments)
            except:
                serializer.save(owner=request.user, text=texts)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

class ChatGet(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, format=None):
        try:
            Chat = chat.objects.filter(
                Q(owner=request.user, toOwner__username=request.data['otherOwner'])
                |
                Q(owner__username=request.data['otherOwner'], toOwner=request.user)
            )
        except chat.DoesNotExist:
            return Response({ "this user don't send chat to you" }, status=status.HTTP_404_NOT_FOUND)
        serialzier = ChatSerializer(Chat, many=True)
        return Response(serialzier.data)

class ChatPost(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, format=None):
        try:
            serializer = ChatSerializer(data = request.data)
        except:
            return Response({" you must send data "}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            try:
                toowner = User.objects.get(username=request.data['toOwner'])
            except User.DoesNotExist:
                return Response({" send user does not exist "}, status=status.HTTP_404_NOT_FOUND)
            serializer.save(owner=request.user, toOwner=toowner)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)