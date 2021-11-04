from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, TextsSerializer, CommentSerializer, TextCommentSerializer
from .permissions import IsOwnerOrReadOnly
from .models import text, BearerAuthentication, comment
from .sortComm import sortedComment
from .tasks import send_email
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Q

# 사용자 목록을 제공하기 위한 API View
# (GET METHOD 사용)
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# 글 검색을 제공하기 위한 API View
# (GET METHOD 사용)
class TextSearch(APIView):
    authentication_classes = [BearerAuthentication]

    def get(self, request, format=None):
        user = request.user

        # 쿼리 스트링 파라미터를 사용하여 db에서 검색하는 로직 
        # hidden이 True인 글은 글 작성자가 로그인 하지 않았을 경우 보내지 않음
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

        # anonymous가 True인 글은 글 작성자가 로그인 하지 않았을 경우 owner를 '익명'으로 바꿔서 보냄
        for i in range(len(serializer_data)):
            if (serializer_data[i]['anonymous'] == True) and (serializer_data[i]['owner'] != request.user.username):
                serializer_data[i]['owner'] = '익명'
        return Response(serializer_data)

# 전체 글 목록 및 글 생성 기능을 제공하기 위한 API View
# (전체 글 목록 : GET METHOD, 글 생성 기능 : CREATE METHOD 사용)
class TextList(generics.ListCreateAPIView):
    queryset = text.objects.all()
    serializer_class = TextsSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        user = request.user

        # 글 전체를 db에서 가져오는 로직
        # hidden이 True인 글은 글 작성자가 로그인 하지 않았을 경우 보내지 않음
        try:
            texts = text.objects.filter(Q(hidden=False) | Q(owner__username=user.username))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TextsSerializer(texts, many=True)
        serializer_data = serializer.data

        # anonymous가 True인 글은 글 작성자가 로그인 하지 않았을 경우 owner를 '익명'으로 바꿔서 보냄
        for i in range(len(serializer_data)):
            if (serializer_data[i]['anonymous'] == True) and (serializer_data[i]['owner'] != request.user.username):
                serializer_data[i]['owner'] = '익명'
        return Response(serializer_data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# 특정 글 하나를 보여주는 기능을 제공하기위한 API View
# (특정 글 보기 : GET METHOD 사용, 특정 글 업데이트 : UPDATE METHOD 사용, 특정 글 삭제 : DELETE METHOD 사용)
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

        # 글에 달린 댓글들을 댓글과 대댓글 등의 순서에 맞게 정렬
        serializer_data['comment'] = sortedComment(serializer_data['comment'], request.user.username)

        # anonymous가 True인 글은 글 작성자가 로그인 하지 않았을 경우 owner를 '익명'으로 바꿔서 보냄
        if (serializer_data['anonymous'] == True) and (serializer_data['owner'] != request.user.username):
            serializer_data['owner'] = '익명'
        return Response(serializer_data)

# 사용자의 로그아웃 기능을 제공하기 위한 API View
# (DELETE METHOD 사용)
class logOut(APIView):

    def delete(self, request, format=None):
        try:
            token = Token.objects.get(key=request.data['key'])
        except Token.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        token.delete()
        return Response({ "logout success" })

# 가입기능을 제공하기 위한 API View
# (POST METHOD 사용)
class signup(APIView):

    def post(self, request, format=None):
        # 계정가입을 위한 정보를 제대로 입력했는지 확인하고 정보가 제대로 입력되지 않았을경우 400에러 사용자에게 반환
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

        # 가입 축하 이메일을 보내는 로직은 비동기적으로 처리
        send_email.delay(
            title="회원 가입이 완료되었습니다", 
            content=f"{request.data['name']}님 회원가입을 축하드립니다",
            email=request.data['email']
        )
        return Response({" singUp success "})

# 계정삭제기능을 제공하는 API View
# (DELETE METHOD 사용)
class accountDelete(APIView):

    def delete(self, request, format=None):
        # 사용자가 Body를 통해 보낸 Bearer Token을 통해 사용자 이름을 파악하고 사용자 이름을 통해 사용자를 DB에서 가져옴 
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

        # 탈퇴 완료 이메일을 보내는 로직을 비동기적으로 처리 
        send_email.delay(
            "회원 탈퇴가 완료되었습니다", 
            f"{name}님 회원탈퇴가 완료되었습니다.",
            email
        )
        return Response({ "delete account success" })
    
# 댓글을 작성하는 기능을 제공하는 API View
# (POST METHOD 사용)
class CommentList(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, format=None):
        try:
            serializer = CommentSerializer(data=request.data)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():

            # HTTP request Body에 toComment key가 있는지 확인하고
            # 있으면, toComment가 가리키는 댓글이 현재 댓글을 작성하려는 글에 적힌 댓글인지 파악하여 적힌 댓글이 아닐 경우 400에러 반환
            # 없거나 toComment가 가리키는 댓글이 현재 글에 적힌 댓글일 경우, 데이터베이스에 사용자가 보낸 댓글 저장
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

# 댓글을 업데이트 하거나 삭제하기 위한 기능을 제공하는 API View
# (댓글 업데이트 : UPDATE METHOD 사용, 댓글 삭제 : DELETE METHOD 사용)
class CommentDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [IsOwnerOrReadOnly]