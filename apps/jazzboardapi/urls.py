from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('texts/', views.TextList.as_view()),
    path('texts/<int:pk>/', views.TextDetail.as_view()),
    path('logout/', views.logOut.as_view()),
    path('signup/', views.signup.as_view()),
    path('accountdelete/', views.accountDelete.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)