from django.urls import path
from . import views

urlpatterns = [
    path('user_task/', views.user_task, name='user_task'),
]
