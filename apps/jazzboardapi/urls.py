from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('texts/', views.TextList.as_view()),
    path('textsDetail/<int:pk>/', views.TextDetail.as_view()),
    path('logout/', views.logOut.as_view()),
    path('signup/', views.signup.as_view()),
    path('accountdelete/', views.accountDelete.as_view()),
    path('comments/', views.CommentList.as_view()),
    path('commentsDetail/<int:pk>/', views.CommentDetail.as_view()),
    path('chatget/', views.ChatGet.as_view()),
    path('chatpost/', views.ChatPost.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)