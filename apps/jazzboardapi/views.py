from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, TextsSerializer, CommentSerializer, ChatSerializer, TextCommentSerializer
from .permissions import IsOwnerOrReadOnly
from .models import text, BearerAuthentication, comment, chat
from .sortComm import sortedComment
from .tasks import send_email
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Q

# Create your views here.
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TextSearch(APIView):
    authentication_classes = [BearerAuthentication]

    def get(self, request, format=None):
        user = request.user
        try:
            searchValue = request.query_params['searchValue']
            searchCond = request.query_params['searchCond']
            if searchCond == 'title':
                texts = text.objects.filter((Q(hidden=False) | Q(owner__username=user.username)) & Q(title=searchValue))
            elif searchCond == 'owner':
                texts = text.objects.filter((Q(hidden=False) | Q(owner__username=user.username)) & Q(owner__username=searchValue))
            else:
                texts = text.objects.filter(Q(hidden=False) | Q(owner__username=user.username))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TextsSerializer(texts, many=True)
        serializer_data = serializer.data
        for i in range(len(serializer_data)):
            if (serializer_data[i]['anonymous'] == True) and (serializer_data[i]['owner'] != request.user.username):
                serializer_data[i]['owner'] = '익명'
        return Response(serializer_data)

class TextList(generics.ListCreateAPIView):
    queryset = text.objects.all()
    serializer_class = TextsSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        user = request.user
        try:
            texts = text.objects.filter(Q(hidden=False) | Q(owner__username=user.username))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
            return Response(status=status.HTTP_404_NOT_FOUND)
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
            return Response(status=status.HTTP_404_NOT_FOUND)
        token.delete()
        return Response({ "logout success" })

class signup(APIView):

    def post(self, request, format=None):
        try:
            if request.data['name'] == '':
                raise Exception()
            if request.data['password'] == '' or not (len(request.data['password']) >= 5):
                raise Exception()
            validate_email(request.data['email'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_user(request.data['name'], request.data['email'], request.data['password'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.save()
        send_email.delay(
            title="회원 가입이 완료되었습니다", 
            content=f"{request.data['name']}님 회원가입을 축하드립니다",
            email=request.data['email']
        )
        return Response({" singUp success "})

class accountDelete(APIView):

    def delete(self, request, format=None):
        try:
            username = Token.objects.get(key=request.data['key'])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(username=username.user)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        name = user.username
        email = user.email
        user.delete()
        send_email.delay(
            "회원 탈퇴가 완료되었습니다", 
            f"{name}님 회원탈퇴가 완료되었습니다.",
            email
        )
        return Response({ "delete account success" })
    
class CommentList(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, format=None):
        try:
            serializer = CommentSerializer(data=request.data)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            try:
                textN = request.data['textN']
                texts = text.objects.get(id=textN)
                if 'toComment' in request.data:
                    tocomment = request.data['toComment']
                    arr = comment.objects.filter(Q(text__id = textN) & Q(id = tocomment))
                    if len(arr) == 0:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    comments = comment.objects.get(id = tocomment)
                    serializer.save(owner=request.user, text=texts, toComment=comments)
                else:
                    serializer.save(owner=request.user, text=texts)
            except:
                Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(status=status.HTTP_404_NOT_FOUND)
        serialzier = ChatSerializer(Chat, many=True)
        return Response(serialzier.data)

class ChatPost(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, format=None):
        try:
            serializer = ChatSerializer(data = request.data)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            try:
                toowner = User.objects.get(username=request.data['toOwner'])
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer.save(owner=request.user, toOwner=toowner)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)