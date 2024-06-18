from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q, Sum
from utils.util_functions import EA_TIMEZONE, parse_datetime
from datetime import datetime
from .models import CustomSheet, Questions, Marking_scheme
import os
import json
import pytz


# tanzania/east africa timezone
tz_tzone = EA_TIMEZONE()
format_datetime = "%Y-%m-%d %H:%M:%S.%f"

@never_cache
@login_required
def answer_sheets_page(request, step=None, sheet=None):
    sheet_param, sheet_exists = sheet, None
    if step is not None and step > 0:
        step1_names, questions_list = "", []
        step1_heading = """UNIVERSITY OF DODOMA\nCOLLEGE OF INFORMATICS & VIRTUAL EDUCATION\nDepartment of computer science & engineering\n2023/2024 academic year\nCP324 Test 1\n\nReg#:..........................................................................\n\nProgram:...................................................................."""
        
        if CustomSheet.objects.filter(id=sheet, teacher=request.user).exists():
            c_sheet = CustomSheet.objects.get(id=sheet)
            sheet_exists = True
            step1_names = c_sheet.names
            step1_heading = c_sheet.heading
            sheet = c_sheet.id

        if sheet_param is not None and Questions.objects.filter(sheet_id=sheet_param, sheet__teacher=request.user).exists():
            sheet_questions = Questions.objects.filter(sheet_id=sheet_param, sheet__teacher=request.user).order_by('id')
            for qns in sheet_questions:
                questions_list.append({
                    'id': qns.id,
                    'type': qns.qn_type,
                    'range': range(int(qns.qn_number)),
                    'qns': qns.questions,
                    'marks': qns.qn_marks,
                })
        
        if not CustomSheet.objects.filter(id=sheet_param, teacher=request.user).exists():
            step = 1
    
        tmp_data = {
            'custom_form': True,
            'step': step,
            'sheet': sheet,
            'sheet_name': CustomSheet.objects.get(id=sheet) if sheet_exists is not None else "",
            'questions': range(1, 21),
            'v_labels': range(1, 11),
            'answer_len': range(3, 19),
            'names': step1_names,
            'heading': step1_heading,
            'questions_list': questions_list,
        }
        return render(request, 'answer_sheets/select_sheets.html', context=tmp_data)
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
            sheet_heading = request.POST.get('heading').strip()
            sheet = int(request.POST.get('sheet')) if request.POST.get('sheet').isdigit() else None

            if len(names) < 3:
                return JsonResponse({'success': False, 'sms': 'Names is too short, should be atleast 3.'})
            if len(names) > 200:
                return JsonResponse({'success': False, 'sms': 'Names is too long, should be atmost 64.'})
            if sheet is None and CustomSheet.objects.filter(names=names, teacher=user).exists():
                return JsonResponse({'success': False, 'sms': 'You already have custom sheet with this name.'})
            if sheet is not None and CustomSheet.objects.filter(names=names, teacher=user).exclude(id=sheet).exists():
                return JsonResponse({'success': False, 'sms': 'You already have custom sheet with this name.'})
            try:
                if sheet is not None and CustomSheet.objects.filter(id=sheet, teacher=request.user).exists():
                    customsheet = CustomSheet.objects.get(id=sheet, teacher=request.user)
                    customsheet.names = names
                    customsheet.heading = sheet_heading
                    customsheet.save()
                    next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet':sheet})
                else:
                    cust_sheet = CustomSheet.objects.create(
                        names=names,
                        heading=sheet_heading,
                        teacher=request.user
                    )
                    next_url = reverse('create_custom_sheet', kwargs={'step': next_step, 'sheet':cust_sheet.id})

                fdback = {'success': True, 'url': next_url}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 3:
            sheet = int(request.POST.get('sheet'))
            custom_sheet = CustomSheet.objects.get(id=sheet)
            try:
                data = request.POST.get('questions')
                data = json.loads(data)
                
                Questions.objects.create(
                    qn_type=request.POST.get('qns_type'),
                    qn_number=request.POST.get('qn_number'),
                    qn_marks=request.POST.get('qn_marks'),
                    questions=data,
                    sheet=custom_sheet
                )

                if not custom_sheet.published:
                    custom_sheet.published = True
                    custom_sheet.save()

                fdback = {'success': True}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 4:
            try:
                sheet_id = int(request.POST.get('sheet'))
                custom_sheet = CustomSheet.objects.get(id=sheet_id)
                questions_list = json.loads(request.POST.get('questions'))

                if Marking_scheme.objects.filter(sheet_id=sheet_id).exists():
                    Marking_scheme.objects.filter(sheet_id=sheet_id).delete()

                for question in questions_list:
                    Marking_scheme.objects.create(
                        qn_number = int(question.get('qn_number')),
                        qn_options = question.get('qn_options'),
                        qn_indices = question.get('qn_indices'),
                        qn_type = question.get('qn_type'),
                        question=Questions.objects.get(id=question.get('qn_question')),
                        sheet = custom_sheet
                    )
                    
                custom_sheet.regdate = datetime.now().replace(tzinfo=pytz.UTC)
                custom_sheet.circles_count = int(request.POST.get('circles_count'))
                custom_sheet.squares_count = int(request.POST.get('squares_count'))
                custom_sheet.save()
                fdback = {'success': True, 'url': reverse('scheme_details', kwargs={'mark_scheme': sheet_id})}
            except Exception as e:
                fdback = {'success': False, 'sms': 'Unknown error..!'}
        elif next_step == 5:
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
    delete_sheet = request.POST.get('delete_sheet')
    if request.method == 'POST' and delete_sheet is None:
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = CustomSheet.objects.filter(teacher=request.user, published=True)

        # Date range filtering
        start_date = parse_datetime(request.POST.get('startdate'), format_datetime, to_utc=True)
        end_date = parse_datetime(request.POST.get('enddate'), format_datetime, to_utc=True)
        date_range_filters = Q()

        if start_date and end_date:
            date_range_filters |= Q(regdate__range=(start_date, end_date))
        else:
            if start_date:
                date_range_filters |= Q(regdate__gte=start_date)
            elif end_date:
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
                'status': "Published",
                'edit': reverse('create_custom_sheet', kwargs={'step': 2, 'sheet': sheet.id}),
                'scheme': reverse('scheme_details', kwargs={'mark_scheme': sheet.id}),
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
                'mark_scheme': item.get('scheme'),
                'edit_sheet': item.get('edit'),
                'action': ''
            })

        ajax_response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': records_filtered,
            'data': final_data,
        }
        return JsonResponse(ajax_response)
    if request.method == 'POST' and delete_sheet is not None:
        fdback = {'success': False, 'sms': 'Unknown error: Failed to delete custom sheet.'}
        try:
            Questions.objects.filter(sheet_id=delete_sheet).delete()
            Marking_scheme.objects.filter(sheet_id=delete_sheet).delete()
            CustomSheet.objects.get(id=delete_sheet).delete()
            fdback = {'success': True}
        except Exception as e:
            fdback = {'success': False, 'sms': 'Unknown error: Failed to delete custom sheet.'}
        return JsonResponse(fdback)
    return render(request, 'answer_sheets/custom_sheets.html')



@never_cache
@login_required
def marking_schemes_list(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = CustomSheet.objects.filter(teacher=request.user, published=True)

        # Date range filtering
        start_date = parse_datetime(request.POST.get('startdate'), format_datetime, to_utc=True)
        end_date = parse_datetime(request.POST.get('enddate'), format_datetime, to_utc=True)
        date_range_filters = Q()

        if start_date and end_date:
            date_range_filters |= Q(regdate__range=(start_date, end_date))
        else:
            if start_date:
                date_range_filters |= Q(regdate__gte=start_date)
            elif end_date:
                date_range_filters |= Q(regdate__lte=end_date)

        if date_range_filters:
            queryset = queryset.filter(date_range_filters)


        # Base data from queryset
        base_data = []
        for sheet in queryset:
            status = Marking_scheme.objects.filter(sheet=sheet)
            base_data.append({
                'id': sheet.id,
                'regDate': sheet.regdate,
                'examName': "--",
                'sheetName': sheet.names,
                'questions': Questions.objects.filter(sheet=sheet).aggregate(total_num=Sum('qn_number'))['total_num'] or 0,
                'status': 'Incomplete' if not status.exists() or status.filter(qn_answer__isnull=True).exists() else 'Complete',
                'info': reverse('scheme_details', kwargs={'mark_scheme': sheet.id})
            })

        
        # Total records before filtering
        total_records = len(base_data)

        # Define a mapping from DataTables column index to the corresponding model field
        column_mapping = {
            0: 'id',
            1: 'regDate',
            2: 'examName',
            3: 'sheetName',
            4: 'questions',
            5: 'status'
        }

        # Apply sorting
        order_column_name = column_mapping.get(order_column_index, 'regDate')
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
                            item_value = float(column_value) if column_value else 0.0
                            if column_search.startswith('-') and column_search[1:].isdigit():
                                max_value = int(column_search[1:])
                                if item_value <= max_value:
                                    filtered_base_data.append(item)
                            elif column_search.endswith('-') and column_search[:-1].isdigit():
                                min_value = int(column_search[:-1])
                                if item_value >= min_value:
                                    filtered_base_data.append(item)
                            elif '-' in column_search and column_search.count('-') == 1:
                                parts = column_search.split('-')
                                if parts[0].isdigit() and parts[1].isdigit():
                                    min_value = int(parts[0])
                                    max_value = int(parts[1])
                                    if min_value <= item_value <= max_value:
                                        filtered_base_data.append(item)
                            elif column_search.isdigit():
                                target_value = float(column_search.replace(',', ''))
                                if item_value == target_value:
                                    filtered_base_data.append(item)
                        else:
                            if column_search.lower() in column_value:
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
                'regDate': item.get('regDate').strftime('%d-%b-%Y'),
                'examName': item.get('examName'),
                'sheetName': item.get('sheetName'),
                'questions': item.get('questions'),
                'status': item.get('status'),
                'info': item.get('info'),
                'action': ''
            })

        ajax_response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': records_filtered,
            'data': final_data,
        }
        return JsonResponse(ajax_response)
    return render(request, 'answer_sheets/mark_schemes.html')


@never_cache
@login_required
def marking_scheme_details(request, mark_scheme):
    if request.method == 'GET' and CustomSheet.objects.filter(id=mark_scheme, teacher=request.user, published=True).exists():
        sheet = CustomSheet.objects.get(id=mark_scheme)
        questions_list = []
        for quest in Marking_scheme.objects.filter(sheet=sheet):
            questions_list.append({
                'id': quest.id,
                'number': quest.qn_number,
                'options': quest.qn_options if quest.qn_type == 'circle' else f"{quest.qn_options} Characters",
                'length': 1 if quest.qn_type == 'circle' else int(quest.qn_options),
                'answer': "" if quest.qn_answer is None else quest.qn_answer,
                'marks': quest.question.qn_marks,
            })
        if len(questions_list) > 1:
            questions_list = sorted(questions_list, key=lambda x: x['number'], reverse=False)

        context_data = {
            'marking_scheme_info': True,
            'sheet_id': mark_scheme,
            'sheet_name': sheet.names,
            'questions': questions_list
        }
        return render(request, 'answer_sheets/mark_schemes.html', context=context_data)
    if request.method == 'POST':
        try:
            if CustomSheet.objects.filter(id=mark_scheme, teacher=request.user).exists():
                answers_list = json.loads(request.POST.get('answers'))
                for answer in answers_list:
                    quest_answer = answer.get('quest_answer')
                    quest_id = int(answer.get('quest_id'))
                    question = Marking_scheme.objects.get(id=quest_id)
                    question.qn_answer = quest_answer
                    question.save()
                fdback = {'success': True, 'sms': 'Answers saved successfully!'}
            else:
                fdback = {'success': False, 'sms': 'Failed to save marking scheme'}
        except Exception as e:
            print(e)
            fdback = {'success': False, 'sms': 'Unknown error occured.'}
        return JsonResponse(fdback)
    return redirect('marking_schemes_list')