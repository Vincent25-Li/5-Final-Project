from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    # templates
    path('base/', views.base, name='base'), # show base template
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('<user_account>/logout/', views.logout, name='logout'),
    path('<user_account>/', views.index, name='blog_index'),
    path('<user_account>/article/<article_id>/', views.article, name='article'),
    path('<user_account>/new_article/', views.new_article, name='new_article'),
    path('<user_account>/edit_article/<article_id>/', views.edit_article, name='edit_article'),
    path('<user_account>/albums/', views.albums, name='albums'),
    path('<user_account>/albums/<user_album_id>/delete/', views.delete_album, name='delete_album'),
    path('<user_account>/new_album/', views.new_album, name='new_album'),
    path('<user_account>/openpose/', views.openpose, name='openpose'),

    # function
    path('<user_account>/model_pose/', views.get_model_image, name='get_model_image'),
    path('<user_account>/pose_analysis/', views.pose_analysis, name='pose_analysis'),
    path('<user_account>/delete_article/', views.delete_article, name='delete_article'),
    path('<user_account>/headshot_upload/', views.headshot_upload),
    path('<user_account>/blog_image_upload/<article_id>/', views.blog_image_upload), #in order to indicate to fxn by url
    path('<user_account>/chatbot/', views.chatbot, name='chatbot'),
    path('<user_account>/<albums>/<album>/', views.show_photos, name='show_photos'),
    path('<user_account>/<albums>/<album>/<category>/', views.ajax_show_photos),
]