from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import CustomSheet, HeaderBoxes, StudentKeys, Questions
import os
import json

@never_cache
@login_required
def answer_sheets_page(request, step=None, sheet=None):
    if step is not None and step > 0:
        if sheet is None or not CustomSheet.objects.filter(id=sheet, teacher=request.user, published=False).exists():
            step = 1
        context = {
            'custom_form': True,
            'step': step,
            'sheet': sheet,
            'questions': range(1, 51),
            'v_labels': range(1, 11),
            'answer_len': range(3, 16),
            # 'rows': range(1, 51),
            # 'cols': range(1, 26)
        }
        return render(request, 'answer_sheets/select_sheets.html', context=context)
    return render(request, 'answer_sheets/select_sheets.html')


@never_cache
@login_required
def save_custom_sheets(request):
    if request.method == 'POST' and request.POST.get('step'):
        next_step = int(request.POST.get('step'))
        user = request.user
        fdback = {'success': False, 'sms': 'Unknown error..!'}
        if next_step == 2:
            names = request.POST.get('names').strip()
            if len(names) < 3:
                return JsonResponse({'success': False, 'sms': 'Names is too short, should be atleast 3.'})
            if len(names) > 64:
                return JsonResponse({'success': False, 'sms': 'Names is too long, should be atmost 64.'})
            if not names.isalpha():
                return JsonResponse({'success': False, 'sms': 'Names should have only alphabets.'})
            if CustomSheet.objects.filter(names=names, teacher=user).exists():
                return JsonResponse({'success': False, 'sms': 'You already have custom sheet with this name.'})
            
            try:
                cust_sheet = CustomSheet.objects.create(
                    names=names,
                    teacher=request.user
                )

                next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet':cust_sheet.id})
                fdback = {'success': True, 'url': next_url}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 3:
            sheet = int(request.POST.get('sheet'))
            next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet': sheet})
            try:
                data = request.POST.get('data')
                data = json.loads(data)
                
                HeaderBoxes.objects.create(
                    contents=data,
                    sheet=CustomSheet.objects.get(id=sheet)
                )
                fdback = {'success': True, 'url': next_url}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 4:
            sheet = int(request.POST.get('sheet'))
            next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet': sheet})
            try:
                data = request.POST.get('data')
                data = json.loads(data)
                
                StudentKeys.objects.create(
                    contents=data,
                    sheet=CustomSheet.objects.get(id=sheet)
                )
                fdback = {'success': True, 'url': next_url}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 5:
            sheet = int(request.POST.get('sheet'))
            try:
                data = request.POST.get('questions')
                data = json.loads(data)
                show_labels = int(request.POST.get('show_labels')) if request.POST.get('show_labels') else None
                if show_labels:
                    show_labels = True if show_labels == 1 else False
                
                Questions.objects.create(
                    qn_type=request.POST.get('qns_type'),
                    qn_number=request.POST.get('qn_number'),
                    questions=data,
                    show_labels=show_labels,
                    sheet=CustomSheet.objects.get(id=sheet)
                )
                fdback = {'success': True}
            except Exception as e:
                print(f'Error: {e}')
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 6:
            try:
                next_url = reverse('custom_list')
                sheet_id = int(request.POST.get('sheet'))
                custom_sheet = CustomSheet.objects.get(id=sheet_id)
                custom_sheet.published = True
                custom_sheet.save()
                fdback = {'success': True, 'url': next_url}
            except Exception as e:
                print(f'Error: {e}')
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        return JsonResponse(fdback)
    return redirect('custom_list')


@never_cache
@login_required
def download_answersheet(request, questions):
    filename = "CiveGrade50Questions.pdf" if questions == 50 else "CiveGrade20Questions.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f"attachment; filename={filename}"
        return response
    

@never_cache
@login_required
def custom_sheets_list(request):
    return render(request, 'answer_sheets/custom_sheets.html')