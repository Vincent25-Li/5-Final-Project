import os
import json
import shutil

import numpy as np
from matplotlib import pyplot as plt

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import loader
from django.http import JsonResponse
from django.http import HttpResponseRedirect

from app_tripblog.models import User, UserArticles, UserAlbums
from app_tripblog.function_chatbot_ch import ChatbotObject
from app_tripblog.fn_image_classifier import Image_Classifier


chatbot_object = ChatbotObject()
img_classifier = Image_Classifier()
''' templates '''


# base template
def base(request):
    title = 'base template'
    user = 'Jessie'
    if request.is_ajax():
        print('success')
    return render(request, 'tripblog/base.html', locals())

def index(request, user_account=None):
    title = 'homepage'
    status = ''
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')

    user_articles = reversed(UserArticles.objects.filter(user_account__user_account=user_account))
    if request.method == 'GET':
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
        return render(request, 'tripblog/index.html', locals())

def signup(request):
    if request.method == 'GET':
        return render(request, 'tripblog/signup.html', locals())
    if request.method == 'POST':
        user_name = request.POST['user_name']
        user_account = request.POST['user_account']
        user_password = request.POST['user_password']
        try:
            user = User.objects.get(user_account=user_account)
        except:
            user = None
        if user!=None:
            message = user.username + "帳號已存在，請嘗試其他帳號！"
            return render(request, 'tripblog/signup.html', locals())
        else:
            user_folder = os.path.join(settings.MEDIA_ROOT, user_account)
            albums_folder = os.path.join(user_folder, 'albums')
            os.makedirs(user_folder)
            os.makedirs(albums_folder)
            user = User.objects.create(user_name=user_name, user_account=user_account, password=user_password)
            user.save()
            return redirect(f'/tripblog/{user_account}')


def login(request):
    # request.session['is_login'] = False
    title='Login'
    if request.method == 'GET':
        request.session['referer'] = request.META.get('HTTP_REFERER')
        return render(request, "tripblog/login.html", locals())

    elif request.method == 'POST':
        user_account = request.POST['user_account']
        user_password = request.POST['user_password']
    
        try: 
            user = User.objects.get(user_account=user_account)
            if user.password == user_password:
                user_name = user.user_name
                user_articles = reversed(UserArticles.objects.filter(user_account__user_account=user_account))
                request.session['login_user'] = user_account
                request.session['is_login'] = True
                return redirect(request.session['referer'])
            else:
                message = '帳號或密碼錯誤，請重新輸入！'
        except: 
            message = '帳號或密碼錯誤，請重新輸入！'
        
        return render(request, "tripblog/login.html", locals())

def logout(request, user_account=None):
    del request.session['login_user']
    del request.session['is_login']
    # print(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def article(request, user_account=None, article_id=None):
    status = ''
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')

    user_article = UserArticles.objects.get(id=article_id)
    title = user_article.article_title

    if request.method == 'GET':
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
        return render(request, 'tripblog/article.html', locals())

def new_article(request, user_account=None):
    title = 'new_article'
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')
    
    if request.method == 'GET':
        return render(request, 'tripblog/new_article.html', locals())
    elif request.method == 'POST' and request.is_ajax():
        article_title = request.POST['article_title']
        article_content = request.POST['article_content']
        article_content = json.loads(article_content)

        # save new data in MySQL
        user_id = User.objects.only('id').get(user_account=user_account)
        user_article = UserArticles.objects.create(user_account=user_id, article_title=article_title, article_content=article_content)
        user_article.save()

        # create new article directory
        dir_path = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id))
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            print(f"Directory {dir_path} already exists")

        response = {}
        response['redirect'] = f'/tripblog/{ user_account }/'
        return JsonResponse(response)
        
def edit_article(request, user_account=None, article_id=None):
    title = 'article_edit'
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')

    user_article = UserArticles.objects.get(id=article_id)

    if request.method == 'GET':
        return render(request, 'tripblog/edit_article.html', locals())
    elif request.method == 'POST' and request.is_ajax():
        article_title = request.POST['article_title']
        article_content = request.POST['article_content']
        article_content = json.loads(article_content)
        
        # update data in MySQL
        user_article.article_title = article_title
        user_article.article_content = article_content
        user_article.save()

        response = {}
        response['redirect'] = f'/tripblog/{ user_account }/article/{ article_id }/'
        return JsonResponse(response)

def albums(request, user_account=None):
    title = "albums"
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')
    
    user_albums = reversed(UserAlbums.objects.filter(user_account__user_account=user_account))
    if request.method == 'GET':
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
        return render(request, 'tripblog/albums.html', locals())
    

''' functions '''

def headshot_upload(request, user_account=None):
    if request.method == 'POST' and request.is_ajax():
        headshot = request.FILES['headshot'] # retrieve post image

        # define stored media path
        headshot_path = os.path.join(settings.MEDIA_ROOT, user_account, 'headshot.jpg')

        # store image at local side
        with open(headshot_path, 'wb+') as destination:
            for chunk in headshot.chunks():
                destination.write(chunk)

        return JsonResponse({'headshot_src': f'/media/{user_account}/headshot.jpg'})
    else:
        raise Http404

def chatbot(request, user_account=None):
    if request.method =='POST' and request.is_ajax():
        user_msg = request.POST.get('user_msg')
        reply_index = chatbot_object.get_index(user_msg)

        if chatbot_object.category_id[reply_index][0] == 1 and 'NER' not in request.session:
            reply = chatbot_object.chat_reply(reply_index)

        elif chatbot_object.category_id[reply_index][0] == 2 or 'NER' in request.session:
            if 'NER' not in request.session:
                request.session['NER'] = {'S-loc': False, 'D-loc': False, 'B-obj': False, 'first_date': False, 'last-date': False}

            chatbot_object.ner(user_msg)

            user_name = User.objects.get(user_account=user_account).user_name
            if not bool(request.session['NER']['S-loc']):
                reply = f'{user_name}請問您要如何規劃行程'
            else:
                reply = 'Test'
            
            print(request.session['NER'])
        response = json.dumps({'reply': reply})
        return HttpResponse(response, content_type='application/json')
    else:
        raise Http404

def show_photos(request, user_account=None, albums='albums', album=None):
    status = ''
    title = 'Gallery'
    user = User.objects.get(user_account=user_account)
    user_name = user.user_name
    album_path = os.path.join(settings.MEDIA_ROOT, user_account, albums, album)
    relative_path2cat = os.path.join('/media', user_account, albums, album)
    if request.method == 'GET':
        display_imgs = []
        for category in os.listdir(album_path):
            if category == '.DS_Store':
                continue
            for image in os.listdir(os.path.join(album_path, category)):
                if image == '.DS_Store':
                    continue
                image_path = os.path.join(relative_path2cat, category, image)

                if settings.MEDIA_ROOT.startswith('C:'): # for windows
                    image_path = image_path.replace('\\', '/')
                display_imgs.append(image_path)

        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'

        return render(request, 'tripblog/gallery.html', locals())
    elif request.method == 'POST':
        # model_file = os.path.join(settings.MEDIA_ROOT, 
        #                         'models_weights', 'image_classifier', 'output_graph.pb')
        # label_file = os.path.join(settings.MEDIA_ROOT, 
        #                         'models_weights', 'image_classifier', 'output_labels.txt')
        # img_classifier = Image_Classifier()
        duplicate_imgs = []
        display_imgs = []
        for img in request.FILES.getlist('upload_imgs'):
            img_fp = os.path.join(settings.MEDIA_ROOT, img.name) # img file path
            with open(img_fp, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)
            
            predict_result = img_classifier.predict(img_fp)
            des = os.path.join(album_path, predict_result)
            duplicate_img = img_classifier.photo2category(img_fp, des)
            if duplicate_img != None: # 判斷重複
                duplicate_imgs.append(duplicate_img)
        
        # print(f'duplicate_imgs: {duplicate_imgs}') #暫時不寫
        for category in os.listdir(album_path):
            if category == '.DS_Store':
                continue
            for image in os.listdir(os.path.join(album_path, category)):
                if image == '.DS_Store':
                    continue
                image_path = os.path.join(relative_path2cat, category, image)

                if settings.MEDIA_ROOT.startswith('C:'): # for windows
                    image_path = image_path.replace('\\', '/')
                display_imgs.append(image_path)
        
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
        return render(request, 'tripblog/gallery.html', locals())

def ajax_show_photos(request, user_account=None, albums='albums', album=None, category=None):
    if request.method =='POST' and request.is_ajax():
        display_imgs = []

        if category != 'all':
            des = os.path.join(settings.MEDIA_ROOT, user_account, albums, album, category)
            images = os.listdir(des)
            for image in images:
                if image == '.DS_Store':
                    continue
                image_path = os.path.join('/media', user_account, albums, album, category, image)
                if settings.MEDIA_ROOT.startswith('C:'): # for windows
                        image_path = image_path.replace('\\', '/')
                display_imgs.append(image_path)
        else:
            album_path = os.path.join(settings.MEDIA_ROOT, user_account, albums, album)
            categories = os.listdir(album_path)
            for cat in categories:
                if cat == '.DS_Store':
                    continue
                des = os.path.join(settings.MEDIA_ROOT, user_account, albums, album, cat)
                images = os.listdir(des)
                for image in images:
                    if image == '.DS_Store':
                        continue
                    image_path = os.path.join('/media', user_account, albums, album, cat, image)
                    if settings.MEDIA_ROOT.startswith('C:'): # for windows
                        image_path = image_path.replace('\\', '/')
                    display_imgs.append(image_path)

    return JsonResponse(display_imgs, safe=False)

def delete_article(request, user_account=None):
    
    if request.method == 'POST' and request.is_ajax():
        article_id = request.POST.get('id')
        dir_path = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', article_id)
    
        try:
            os.rmdir(dir_path)
            UserArticles.objects.get(id=article_id).delete()
        except OSError:
            shutil.rmtree(dir_path, ignore_errors=True)
            UserArticles.objects.get(id=article_id).delete()

        response = {}
        response['reply'] = 'success'
        return HttpResponse('')

def new_album(request, user_account=None):
    if request.method == 'POST' and request.is_ajax():
        album_title = request.POST.get('album_title')

        # user_id = User.objects.only('id').get(user_account=user_account)
        # user_album = UserAlbums.objects.create(user_account=user_id, album_title=album_title)
        # user_album.save()
        response = {}
        response['redirect'] = f'/tripblog/{ user_account }/albums/'
        response['response'] = f'"{album_title}"新增成功'
        return JsonResponse(response)

        


'''internal functions'''

# check user_account whether exist in database
# if yes, return user_name
# if not, return None
def check_useraccount_exist(user_account):
    user_accounts = User.objects.values_list('user_account')
    if user_account in np.array(user_accounts):
        user_name = User.objects.get(user_account=user_account).user_name
        return user_name
    else:
        return None
        
def cyclegan(request):
    pass
