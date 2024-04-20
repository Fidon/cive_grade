from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q, Sum
from utils.util_functions import EA_TIMEZONE
from datetime import datetime
from .models import CustomSheet, HeaderBoxes, StudentKeys, Questions
import os
import json
import pytz


# tanzania/east africa timezone
tz_tzone = EA_TIMEZONE()
format_datetime = "%Y-%m-%d %H:%M:%S.%f"

@never_cache
@login_required
def answer_sheets_page(request, step=None, sheet=None):
    if step is not None and step > 0:
        step = 1 if sheet is None or not CustomSheet.objects.filter(id=sheet, teacher=request.user, published=False).exists() else step
        step1_names, sizes, header_boxes, id_section, keys_section = "", None, None, None, None
        questions_list = []
        
        if step == 1 and CustomSheet.objects.filter(teacher=request.user, published=False).exists():
            c_sheet = CustomSheet.objects.filter(teacher=request.user, published=False).order_by('-id').first()
            step1_names = c_sheet.names
            sheet = c_sheet.id
        if sheet is not None and HeaderBoxes.objects.filter(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False).exists():
            hd_boxes = HeaderBoxes.objects.get(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False)
            header_boxes = hd_boxes.contents
            sizes = [{'short': 's', 'long': 'Small'}, {'short': 'm', 'long': 'Medium'}, {'short': 'l', 'long': 'Large'}]
        if sheet is not None and StudentKeys.objects.filter(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False).exists():
            studentkeys = StudentKeys.objects.get(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False)
            id_section = studentkeys.contents[0]
            keys_section = studentkeys.contents[1]
        if sheet is not None and Questions.objects.filter(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False).exists():
            sheet_questions = Questions.objects.filter(sheet_id=sheet, sheet__teacher=request.user, sheet__published=False).order_by('id')
            for qns in sheet_questions:
                questions_list.append({
                    'id': qns.id,
                    'type': qns.qn_type,
                    'range': range(int(qns.qn_number)),
                    'qns': qns.questions,
                    'show': qns.show_labels if qns.show_labels else None
                })
    
        context = {
            'custom_form': True,
            'step': step,
            'sheet': sheet,
            'sheet_name': CustomSheet.objects.get(id=sheet) if sheet is not None and step > 0 else "",
            'questions': range(1, 51),
            'v_labels': range(1, 11),
            'answer_len': range(3, 16),
            'names': step1_names,
            'header_boxes': header_boxes,
            'sizes': sizes,
            'id_section': id_section,
            'keys_section': keys_section,
            'questions_list': questions_list,
            'table_columns': range(1, 34),
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
            sheet = int(request.POST.get('sheet')) if request.POST.get('sheet').isdigit() else None
            print(f"Sheet_id: {sheet}")

            if len(names) < 3:
                return JsonResponse({'success': False, 'sms': 'Names is too short, should be atleast 3.'})
            if len(names) > 200:
                return JsonResponse({'success': False, 'sms': 'Names is too long, should be atmost 64.'})
            if sheet is None and CustomSheet.objects.filter(names=names, teacher=user).exists():
                return JsonResponse({'success': False, 'sms': 'You already have custom sheet with this name.'})
            if sheet is not None and CustomSheet.objects.filter(names=names, teacher=user).exclude(id=sheet).exists():
                return JsonResponse({'success': False, 'sms': 'You already have custom sheet with this name.'})
            try:
                if sheet is not None and CustomSheet.objects.filter(id=sheet, published=False, teacher=request.user).exists():
                    customsheet = CustomSheet.objects.get(id=sheet, published=False, teacher=request.user)
                    customsheet.names = names
                    customsheet.save()
                    next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet':sheet})
                else:
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

                if HeaderBoxes.objects.filter(sheet_id=sheet, sheet__published=False, sheet__teacher=request.user).exists():
                    hdboxes = HeaderBoxes.objects.get(sheet_id=sheet, sheet__published=False, sheet__teacher=request.user)
                    hdboxes.contents = data
                    hdboxes.save()
                else:
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

                if StudentKeys.objects.filter(sheet_id=sheet, sheet__published=False, sheet__teacher=request.user).exists():
                    st_keys = StudentKeys.objects.get(sheet_id=sheet, sheet__published=False, sheet__teacher=request.user)
                    st_keys.contents = data
                    st_keys.save()
                else:
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
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 7:
            try:
                questions = request.POST.get('questions')
                questions = json.loads(questions)
                for qn in questions:
                    quest = Questions.objects.get(id=qn['id'])
                    if (quest.qn_number - int(qn['qns'])) > 0:
                        quest.qn_number = quest.qn_number - int(qn['qns'])
                        quest.save()
                    else:
                        quest.delete()
                fdback = {'success': True}
            except Exception as e:
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
    if request.method == 'POST' and request.POST.get('delete_sheet') is None:
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = CustomSheet.objects.filter(teacher=request.user, published=True)

        # Date range filtering
        start_date = request.POST.get('startdate')
        end_date = request.POST.get('enddate')
        date_range_filters = Q()
        if start_date:
            start_date = datetime.strptime(start_date, format_datetime).replace(tzinfo=pytz.UTC)
            date_range_filters |= Q(regdate__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, format_datetime).replace(tzinfo=pytz.UTC)
            date_range_filters |= Q(regdate__lte=end_date)

        if date_range_filters:
            queryset = queryset.filter(date_range_filters)


        # Base data from queryset
        base_data = []
        for sheet in queryset:
            base_data.append({
                'id': sheet.id,
                'regdate': sheet.regdate,
                'names': sheet.names,
                'questions': Questions.objects.filter(sheet=sheet).aggregate(total_num=Sum('qn_number'))['total_num'] or 0,
                'status': "Published"
            })

        
        # Total records before filtering
        total_records = len(base_data)

        # Define a mapping from DataTables column index to the corresponding model field
        column_mapping = {
            0: 'id',
            1: 'regdate',
            2: 'names',
            3: 'questions',
            4: 'status'
        }

        # Apply sorting
        order_column_name = column_mapping.get(order_column_index, 'names')
        if order_dir == 'asc':
            base_data = sorted(base_data, key=lambda x: x[order_column_name], reverse=False)
        else:
            base_data = sorted(base_data, key=lambda x: x[order_column_name], reverse=True)

        # Apply individual column filtering
        for i in range(len(column_mapping)):
            column_search = request.POST.get(f'columns[{i}][search][value]', '')
            if column_search:
                column_field = column_mapping.get(i)
                if column_field:
                    filtered_base_data = []
                    for item in base_data:
                        column_value = str(item.get(column_field, '')).lower()
                        if column_field == 'questions':
                            if column_search.startswith('-') and column_search[1:].isdigit():
                                max_value = int(column_search[1:])
                                item_value = float(column_value) if column_value else 0.0
                                if item_value <= max_value:
                                    filtered_base_data.append(item)
                            elif column_search.endswith('-') and column_search[:-1].isdigit():
                                min_value = int(column_search[:-1])
                                item_value = float(column_value) if column_value else 0.0
                                if item_value >= min_value:
                                    filtered_base_data.append(item)
                            elif column_search.isdigit():
                                target_value = float(column_search.replace(',', ''))
                                item_value = float(column_value) if column_value else 0.0
                                if item_value == target_value:
                                    filtered_base_data.append(item)
                        elif column_search.lower() in column_value:
                            filtered_base_data.append(item)

                    base_data = filtered_base_data

        # Apply global search
        if search_value:
            base_data = [item for item in base_data if any(str(value).lower().find(search_value.lower()) != -1 for value in item.values())]

        # Calculate the total number of records after filtering
        records_filtered = len(base_data)

        # Apply pagination
        if length < 0:
            length = len(base_data)
        base_data = base_data[start:start + length]

        # Calculate row_count based on current page and length
        page_number = start // length + 1
        row_count_start = (page_number - 1) * length + 1


        # Final data to be returned to ajax call
        final_data = []
        for i, item in enumerate(base_data):
            final_data.append({
                'count': row_count_start + i,
                'id': item.get('id'),
                'regdate': item.get('regdate').strftime('%d-%b-%Y'),
                'names': item.get('names'),
                'questions': item.get('questions'),
                'status': item.get('status'),
                'action': ''
            })

        ajax_response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': records_filtered,
            'data': final_data,
        }
        return JsonResponse(ajax_response)
    if request.method == 'POST' and request.POST.get('delete_sheet') is not None:
        fdback = {'success': False, 'sms': 'Unknown error: Failed to delete custom sheet.'}
        try:
            sheet = request.POST.get('delete_sheet')
            Questions.objects.filter(sheet_id=sheet).delete()
            StudentKeys.objects.filter(sheet_id=sheet).delete()
            HeaderBoxes.objects.filter(sheet_id=sheet).delete()
            CustomSheet.objects.get(id=sheet).delete()
            fdback = {'success': True}
        except Exception as e:
            fdback = {'success': False, 'sms': 'Unknown error: Failed to delete custom sheet.'}
        return JsonResponse(fdback)
    return render(request, 'answer_sheets/custom_sheets.html')