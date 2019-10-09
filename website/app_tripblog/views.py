import os
import json

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import loader
from django.http import JsonResponse

from app_tripblog.function_chatbot import ChatbotObject
from app_tripblog.fn_image_classifier import Image_Classifier
from matplotlib import pyplot as plt


chatbot_object = ChatbotObject()

''' templates '''

# base template
def base(request):
    title = 'base template'
    user = 'Jessie'
    if request.is_ajax():
        print('success')
    return render(request, 'tripblog/base.html', locals())

def index(request, user=None):
    title = 'homepage'
    user = user
    if request.method == 'GET':
        return render(request, 'tripblog/index.html', locals())

def article(request, user=None):
    title = 'test_article'
    user = user
    return render(request, 'tripblog/article.html', locals())
        
def edit_article(request, user=None):
    title = 'article_edit'
    user = user
    return render(request, 'tripblog/edit_article.html', locals())
    

''' functions '''

def headshot_upload(request, user=None):
    if request.method == 'POST' and request.is_ajax():
        headshot = request.FILES['headshot'] # retrieve post image

        # define stored media path
        headshot_path = os.path.join(settings.MEDIA_ROOT, user, 'headshot.jpg')

        # store image at local side
        with open(headshot_path, 'wb+') as destination:
            for chunk in headshot.chunks():
                destination.write(chunk)

        return JsonResponse({'headshot_src': f'/media/{user}/headshot.jpg'})
    else:
        raise Http404

def chatbot(request, user=None):
    if request.method =='POST' and request.is_ajax():
        user_msg = request.POST.get('user_msg')
        reply = chatbot_object.reply(user_msg)
        data = json.dumps({'reply': reply})
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404

def show_photos(request, user=None, albums='albums', album=None):
    title = 'Gallery'
    user = user
    album_path = os.path.join(settings.MEDIA_ROOT, user, albums, album)
    relative_path2cat = os.path.join('/media', user, albums, album)
    if request.method == 'GET':
        return render(request, 'tripblog/upload_photos.html', locals())
    elif request.method == 'POST':
        model_file = os.path.join(settings.MEDIA_ROOT, 
                                'models_weights', 'image_classifier', 'output_graph.pb')
        label_file = os.path.join(settings.MEDIA_ROOT, 
                                'models_weights', 'image_classifier', 'output_labels.txt')
        img_classifier = Image_Classifier(model_file, label_file, user, album)

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
        return render(request, 'tripblog/gallery.html', locals())

def ajax_show_photos(request, user=None, albums='albums', album=None, category=None):
    if request.method =='POST' and request.is_ajax():
        display_imgs = []

        if category != 'all':
            des = os.path.join(settings.MEDIA_ROOT, user, albums, album, category)
            images = os.listdir(des)
            for image in images:
                if image == '.DS_Store':
                    continue
                image_path = os.path.join('/media', user, albums, album, category, image)
                if settings.MEDIA_ROOT.startswith('C:'): # for windows
                        image_path = image_path.replace('\\', '/')
                display_imgs.append(image_path)
        else:
            album_path = os.path.join(settings.MEDIA_ROOT, user, albums, album)
            categories = os.listdir(album_path)
            for cat in categories:
                if cat == '.DS_Store':
                    continue
                des = os.path.join(settings.MEDIA_ROOT, user, albums, album, cat)
                images = os.listdir(des)
                for image in images:
                    if image == '.DS_Store':
                        continue
                    image_path = os.path.join('/media', user, albums, album, cat, image)
                    if settings.MEDIA_ROOT.startswith('C:'): # for windows
                        image_path = image_path.replace('\\', '/')
                    display_imgs.append(image_path)

    return JsonResponse(display_imgs, safe=False)

def cyclegan(request):
    pass