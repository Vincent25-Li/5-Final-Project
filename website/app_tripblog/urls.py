from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    # templates
    path('base/', views.base, name='base'), # show base template
    path('<user>/', views.index, name='blog_index'),
    path('<user>/article/', views.article, name='article'),
    path('<user>/edit_article/', views.edit_article, name='edit_article'),

    # function
    path('<user>/headshot_upload/', views.headshot_upload),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('<user>/<albums>/<album>/', views.show_photos),
    path('<user>/<albums>/<album>/<category>/', views.ajax_show_photos),
]