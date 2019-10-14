from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    # templates
    path('base/', views.base, name='base'), # show base template
    path('<user_account>/', views.index, name='blog_index'),
    path('<user_account>/article/<article_id>/', views.article, name='article'),
    path('<user_account>/new_article/', views.new_article, name='new_article'),
    path('<user_account>/edit_article/<article_id>/', views.edit_article, name='edit_article'),

    # function
    path('<user_account>/delete_article/', views.delete_article, name='delete_article'),
    path('<user_account>/headshot_upload/', views.headshot_upload),
    path('<user_account>/chatbot/', views.chatbot, name='chatbot'),
    path('<user_account>/<albums>/<album>/', views.show_photos),
    path('<user_account>/<albums>/<album>/<category>/', views.ajax_show_photos),
]