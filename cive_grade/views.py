from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime
import os
import imghdr
import pytesseract as pyt
import cv2


@never_cache
@login_required
def home_page(request):
    return render(request, 'home.html', context={'rows': range(50), 'cols': range(25)})


@never_cache
@login_required
def upload_majibu(request):
    if request.method == 'POST' and request.FILES['majibu']:
        image = request.FILES['majibu']
        image_type = imghdr.what(image)
        if image_type not in ['jpeg', 'png']:
            return JsonResponse({'success': False, 'sms': 'Only jpg, jpeg and png are allowed formats!'})
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        _, ext = os.path.splitext(image.name)
        new_filename = timestamp + ext
        img_path = os.path.join(settings.MEDIA_ROOT, new_filename)

        with open(img_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
                
        pyt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        img = cv2.imread(img_path)
        custom_config = r'--oem 3 --psm 3'

        text = pyt.image_to_string(img, config=custom_config)
        text = text.encode("ascii", "ignore")
        text = text.decode()

        os.remove(img_path)
        
        return JsonResponse({'success': True, 'sms': 'Image uploaded successfully!', 'img_text': text})
    return render(request, 'home.html')


