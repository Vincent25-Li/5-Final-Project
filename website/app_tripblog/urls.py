from django.urls import path

from . import views

urlpatterns = [
    path('base', views.base, name='base'),
    path('', views.index, name='blog_index'),
    path('add_post', views.add_post, name='add_post'),
    path('edit_article', views.edit_article, name='edit_article'),
]