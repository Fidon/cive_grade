from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime
from img2table.ocr import TesseractOCR
from img2table.document import Image
import os
import imghdr

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


        ocr = TesseractOCR(n_threads=1, lang="eng")
        doc = Image(img_path)
        extracted_tables = doc.extract_tables(ocr=ocr, implicit_rows=False, borderless_tables=False, min_confidence=50)
        table_data = []
        if extracted_tables:
            table = extracted_tables[0]
            for row_idx, row in enumerate(table.content.values()):
                row_data = []
                for cell in row:
                    row_data.append(cell.value)
                table_data.append({'row_idx': (row_idx+1), 'row_data': row_data})
                
        return render(request, 'home.html', {'tabledata': table_data})
    return render(request, 'home.html')


