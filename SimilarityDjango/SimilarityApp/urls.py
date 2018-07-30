from django.urls import path, include
from . import views

app_name = 'SimilarityApp'   # app名字

urlpatterns = [
    path('', views.start, name='起始页'),
    path('login/', views.login, name='登录'),
    path('home/<role>/<user_id>/<username>/', views.home, name='主页'),
]