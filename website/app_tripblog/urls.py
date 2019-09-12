from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='blog_index'),
    path('addpost', views.add_post, name='add_post'),
]