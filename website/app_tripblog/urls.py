from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    # templates
    path('base/', views.base, name='base'), # show base template
    path('', views.index, name='blog_index'),
    path('article/', views.article, name='article'),
    path('edit_article/', views.edit_article, name='edit_article'),

    # function
    path('chatbot/', views.chatbot, name='chatbot'),
    re_path(r'jessie/albums/album1/$', views.show_photos),
    re_path(r'jessie/albums/album1/(\w+)$', views.ajax_show_photos),
]