import os
import json
import pickle

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404


# Create your views here.
chatbot_clf = pickle.load()
# templates

# base template
def base(request):
    title = 'base template'
    if request.is_ajax():
        print('success')
    return render(request, 'tripblog/base.html', locals())

def index(request):
    title = 'homepage'
    if request.method == 'GET':
        return render(request, 'tripblog/index.html', locals())

    elif request.method == 'POST':
        headshot = request.FILES['headshot'] # retrieve post image

        # define stored media path
        headshot_path = os.path.join(settings.MEDIA_ROOT, 'jessie', 'headshot.jpg')

        # store image at local side
        with open(headshot_path, 'wb+') as destination:
            for chunk in headshot.chunks():
                destination.write(chunk)
        return redirect('/tripblog/')

def add_post(request):
    title = 'responsive timeline v3'
    return render(request, 'tripblog/add_post.html', locals())
    
def edit_article(request):
    title = 'article_edit'
    return render(request, 'tripblog/edit_article.html', locals())

# functions

def chatbot(request):
    if request.method =='POST' and request.is_ajax():
        user_msg = request.POST.get('user_msg')
        data = json.dumps({'reply': 'Hi'})
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404
