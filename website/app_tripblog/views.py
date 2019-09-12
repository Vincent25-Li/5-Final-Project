import os

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse


# Create your views here.

def index(request):
    if request.method == 'GET':
        return render(request, 'tripblog/index.html')

    elif request.method == 'POST':
        headshot = request.FILES['headshot'] # retrieve post image

        # define stored media path
        headshot_path = os.path.join(settings.MEDIA_ROOT, 'jessie', 'headshot.jpg')

        # store image at local side
        with open(headshot_path, 'wb+') as destination:
            for chunk in headshot.chunks():
                destination.write(chunk)
        return redirect('/tripblog/')