import os
import json
import shutil

import numpy as np
import random
from matplotlib import pyplot as plt

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import loader
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from app_tripblog.models import User, UserArticles, UserAlbums
from app_tripblog.function_chatbot_ch import ChatbotObject
from app_tripblog.fn_image_classifier import Image_Classifier
from app_tripblog.cyclegan import CycleGAN ###load cyclegan
from PIL import Image 
# from app_tripblog.fn_openpose import OpenposeObject

chatbot_object = ChatbotObject()
img_classifier = Image_Classifier()
gan = CycleGAN()
gan.load_model_and_weights(gan.G_B2A)
print('load gan sucess ===============================================')

# openpose_object = OpenposeObject()
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
    random_no = random.randint(1, 1001)
    no = ['1','2','3','4','5']
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
            message = request.POST['user_account'] + "帳號已存在，請嘗試其他帳號！"
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
    temp_user = request.session['login_user']
    del request.session['login_user']
    del request.session['is_login']
    # print(request.META.get('HTTP_REFERER'))
    return redirect(f'/tripblog/{temp_user}/')
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
    status = ''
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')
    
    if request.method == 'GET':
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
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
        dir_path1 = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id),'original')
        dir_path2 = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id),'transfer')
        dir_path3 = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id),'trainA')
        dir_path4 = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id),'trainB')
        try:
            os.makedirs(dir_path1)
            os.makedirs(dir_path2)
            os.makedirs(dir_path3)
            os.makedirs(dir_path4)
        except FileExistsError:
            print(f"Directory {dir_path} already exists")
        img_src = os.path.join(settings.MEDIA_ROOT, 'fortrain.jpg')
        img_dst = os.path.join(settings.MEDIA_ROOT, user_account, 'articles', str(user_article.id),'transfer')
        shutil.copy(img_src, img_dst)

        response = {}
        response['redirect'] = f'/tripblog/{ user_account }/'
        return JsonResponse(response)
        
def edit_article(request, user_account=None, article_id=None):
    title = 'article_edit'
    status = ''
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')

    user_article = UserArticles.objects.get(id=article_id)
    # print(user_article.article_content)
    response = {}
    response['user_article'] = user_article
    response['article_content'] = user_article.article_content
    if request.method == 'GET':
        if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
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

def openpose(request, user_account=None):
    title = 'OpenPose'
    status = ''
    if 'is_login' in request.session:
            login_user = request.session['login_user']
            status = 'login'
    
    user_name = check_useraccount_exist(user_account)
    if not bool(user_name):
        return HttpResponse(f'Page not found: user account "{user_account}" not exist')
    return render(request, 'tripblog/openpose.html', locals())

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

        response = {}
        if chatbot_object.category_id[reply_index-1][0] == 1 and 'NER' not in request.session:
            reply = chatbot_object.chat_reply(reply_index)

        elif chatbot_object.category_id[reply_index-1][0] == 2 or 'NER' in request.session:
            
            if 'NER' not in request.session:
                request.session['NER'] = True
                request.session['S-loc'] = False
                request.session['D-loc'] = False
                request.session['B-obj'] = False
                request.session['first_date'] = False
                request.session['last_date'] = False
                request.session['loc_a'] = False
                request.session['B-obj_a'] = False
                request.session['first_date_a'] = False
                request.session['last_date_a'] = False

            X_msg, y_tag = chatbot_object.ner(user_msg)
            n_tag = list(set(y_tag))

            if request.session['first_date_a'] == True:
                request.session['first_date'] = user_msg
                request.session['first_date_a'] = False
            elif request.session['last_date_a'] == True:
                request.session['last_date'] = user_msg
                request.session['last_date_a'] = False
            elif len(n_tag) > 1:
                n_tag.remove('O')
                if request.session['B-obj_a'] == True:
                    try:
                        tag_idx = y_tag.index('B-obj')
                        request.session['B-obj'] = X_msg[tag_idx]
                        request.session['B-obj_a'] = False
                    except ValueError:
                        reply = f"不好意思請您再說一次您要搭什麼前往{request.session['D-loc']}<br>Ex:搭高鐵"
                elif request.session['loc_a']:
                    if 'B-obj' in n_tag:
                        n_tag.remove('B-obj')
                    for tag in n_tag:
                        tag_idx = y_tag.index(tag)
                        request.session[tag] = X_msg[tag_idx]
                    request.session['loc_a'] = False
            
            mission_list = ['S-loc', 'D-loc', 'B-obj', 'first_date', 'last_date']
            mission_completed = 0
            for item in mission_list:
                mission_completed += bool(request.session[item])

            user_name = User.objects.get(user_account=user_account).user_name
            confirmation = ['y', 'yes', '確認']
            cancellation = ['n', 'no', '取消', '我要取消']
            
            if user_msg.lower() in confirmation and mission_completed==5:
                user_id = User.objects.only('id').get(user_account=user_account)
                article_title = f"{request.session['first_date']}~{request.session['last_date']}: {request.session['S-loc']}至{request.session['D-loc']}旅遊記"
                article_content = {
                    'first_date': request.session['first_date'],
                    'last_date': request.session['last_date'],
                    'transportation': request.session['B-obj']
                    }
                user_article = UserArticles.objects.create(user_account=user_id, article_title=article_title, article_content=article_content)
                user_article.save()

                response['title'] = article_title
                response['id'] = user_article.id
                reply = '已安排您的行程於遊記裡'
                del request.session['NER']
            elif user_msg.lower() in cancellation and mission_completed==5:
                reply = f'{user_name}您的旅程已取消'
                del request.session['NER']
            elif mission_completed == 5:
                reply = f"請確定您的以下行程：<br>{request.session['S-loc']}＞{request.session['D-loc']}<br>搭乘：{request.session['B-obj']}<br>時間：{request.session['first_date']}＞{request.session['last_date']}<br>[Y/N]"
            elif not bool(request.session['S-loc']) and not bool(request.session['D-loc']):
                reply = f'{user_name}請問您想如何規劃行程'
                request.session['loc_a'] = True
            elif not bool(request.session['S-loc']) and bool(request.session['D-loc']):
                reply = f'請問您從哪出發'
                request.session['loc_a'] = True
            elif bool(request.session['S-loc']) and not bool(request.session['D-loc']):
                reply = f'請問您要前往何處'
                request.session['loc_a'] = True
            elif not bool(request.session['first_date']):
                reply = f"您預計何時從{request.session['S-loc']}出發"
                request.session['first_date_a'] = True
            elif not bool(request.session['last_date']):
                reply = f"您預計何時從{request.session['D-loc']}返回"
                request.session['last_date_a'] = True
            elif not bool(request.session['B-obj']):
                reply = f"請問您要如何從{request.session['S-loc']}前往{request.session['D-loc']}"
                request.session['B-obj_a'] = True
            
        response['response'] = reply
        return JsonResponse(response)
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

@csrf_exempt
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

def new_album(request, user_account=None):
    categories = ['architecture', 'food', 'nature', 'other', 'people']
    if request.method == 'POST' and request.is_ajax():
        album_title = request.POST.get('album_title')
        user = User.objects.get(user_account=user_account)

        try: 
            user_albums = UserAlbums.objects.get(user_account_id=user.id, album_title=album_title)

        except UserAlbums.DoesNotExist:
            user_album = UserAlbums.objects.create(user_account_id=user.id, album_title=album_title)
            user_album.save()
            
            dir_path = os.path.join(settings.MEDIA_ROOT, user_account, 'albums', str(user_album.id))
            os.mkdir(dir_path)
        
        # create subfolders for each category
        for cat in categories:
            os.mkdir(os.path.join(dir_path, cat))

        # retrieve albums 
        user_albums = UserAlbums.objects.filter(user_account_id=user.id)
        data = serializers.serialize('json', user_albums)

        response = {}
        # response['redirect'] = f'/tripblog/{ user_account }/albums/'
        response['response'] = f'相簿"{album_title}"新增成功'
        # response['albums'] = data

        return JsonResponse(response, safe=False)

def delete_album(self, user_account=None, user_album_id=None):
    categories = ['architecture', 'food', 'nature', 'other', 'people']
    user = User.objects.get(user_account=user_account)
    UserAlbums.objects.filter(user_account_id=user.id, id=user_album_id).delete()
    dir_path = os.path.join(settings.MEDIA_ROOT, user_account, 'albums', user_album_id)
    shutil.rmtree(dir_path, ignore_errors=True)

    return redirect(f'/tripblog/{user_account}/albums/')

def get_model_image(request, user_account=None):
    if request.method == 'POST' and request.is_ajax():
        image = request.POST.get('image')
        width = int(request.POST.get('w'))
        height = int(request.POST.get('h'))
        image = list(json.loads(image).values())
        image = np.array(image).reshape(height, width, -1)[:, :, :3]
        image = image.astype('uint8')
        openpose_object.model_wh(width, height)
        openpose_object.load_model_img(image, user_account)
        response = {}
        response['response'] = 'OK'
        return JsonResponse(response)

def pose_analysis(request, user_account=None):
    if request.method == 'POST' and request.is_ajax():
        image = request.POST.get('image')
        width = int(request.POST.get('w'))
        height = int(request.POST.get('h'))
        image = list(json.loads(image).values())
        image = np.array(image).reshape(height, width, -1)[:, :, :3]
        image = image.astype('uint8')
        
        try:
            result = openpose_object.openpose_matching(image, user_account)
        except IndexError:
            result = False

        response = {}
        response['result'] = result
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
        
def article_cover_upload(request, user_account=None, article_id=None):
    if request.method == 'POST' and request.is_ajax():
        article_cover = request.FILES['article_cover'] # retrieve post image
        print('~~~~~~~~~~~~~~article_cover :', article_cover ,'~~~~~~~~~~~~~~')
        user = User.objects.get(user_account=user_account)
        # print('user is :', user,'====================================') 
        user_article = UserArticles.objects.get(id=article_id)
        print('~~~~~~~~~~~~~~user_article :', user_article ,'~~~~~~~~~~~~~~') 
        print('~~~~~~~~~~~~~~user_article.article_title :', user_article.article_title ,'~~~~~~~~~~~~~~') 
        # print('user_article.id is :', user_article.id ,'====###======') 
        user_article_id = str(user_article.id)

        article_cover_path = os.path.join(settings.MEDIA_ROOT, user_account,'articles', user_article_id ,'original','cover.jpg')   # define stored media path
        print('~~~~~~~~~~~~~~article_cover_path :', article_cover_path ,'~~~~~~~~~~~~~~')

        with open(article_cover_path, 'wb+') as destination:# store image at local side
            for chunk in article_cover.chunks():
                destination.write(chunk)

        print('~~~~~~~~~~~~~~OK~~~~~~~~~~~~~~')
        im = Image.open(article_cover_path)
        width = 256
        height = 256
        nim = im.resize( (width, height), Image.BILINEAR )
        nim.save(article_cover_path)  

        # GAN = CycleGAN(user_account = user_account, user_article_id = user_article_id )
        # # print('user_account :', user_account, '&&&&&&&&&&&&&&&&&')
        # # print('user_article_id :', user_article_id, '&&&&&&&&&&&') 
        # GAN.load_model_and_weights(GAN.G_B2A)
        # GAN.load_model_and_generate_synthetic_images()   
    
        return JsonResponse({'article_cover_src': f'/media/{user_account}/articles/{user_article.id}/original/cover.jpg'})

    else:
        raise Http404

def article_cover_style_change(request, user_account=None, article_id=None):
    user = User.objects.get(user_account=user_account)
    user_article = UserArticles.objects.get(id=article_id)
    user_article_id = str(user_article.id)

    GAN = CycleGAN(user_account = user_account, user_article_id = user_article_id )
    # print('user_account :', user_account, '&&&&&&&&&&&&&&&&&')
    # print('user_article_id :', user_article_id, '&&&&&&&&&&&') 
    GAN.load_model_and_weights(GAN.G_B2A)
    GAN.load_model_and_generate_synthetic_images()  

    return JsonResponse({'article_style_src': f'/media/{user_account}/articles/{user_article.id}/transfer/cover.j_synthetic.png'}) 