from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime
from utils.read_answer_sheet import TableExtractor as te, TableLinesRemover as tlr, OcrToTableTool as ott
import os
import imghdr
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

        # try:
        # except Exception as e:
        #     return JsonResponse({'success': False, 'sms': f'Error processing image: {e}'})
        
        table_extractor = te(img_path)
        perspective_corrected_image = table_extractor.execute()
        cv2.imshow("perspective_corrected_image", perspective_corrected_image)

        lines_remover = tlr(perspective_corrected_image)
        image_without_lines = lines_remover.execute()
        cv2.imshow("image_without_lines", image_without_lines)

        ocr_tool = ott(image_without_lines, perspective_corrected_image)
        table_data = ocr_tool.execute()
        # print(table_data[3])

        return render(request, 'result.html', {'table_data': table_data})
    return render(request, 'home.html')


