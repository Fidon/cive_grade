from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from utils.image_processing import mark_circle_questions, mark_square_questions
from django.http import JsonResponse
from django.db.models import Q, Sum
from utils.util_functions import parse_datetime
from datetime import datetime
from apps.answer_sheets.models import CustomSheet, Questions, Marking_scheme
from apps.students.models import Students
from .models import Exams, Results
import os
from django.conf import settings
import imghdr
import pytz


# tanzania/east africa timezone
format_datetime = "%Y-%m-%d %H:%M:%S.%f"


@never_cache
@login_required
def exams_actions(request):
    if request.method == 'POST':
        try:
            edit_exam = request.POST.get('edit_exam')
            delete_exam = request.POST.get('delete_exam')
            if delete_exam:
                exam_instance = Exams.objects.get(id=delete_exam)
                exam_instance.deleted = True
                exam_instance.save()
                return JsonResponse({'success': True, 'url': reverse('exams_list')})
            elif edit_exam:
                exam_names = request.POST.get('exam_name').strip()
                exam_sheet = request.POST.get('sheet')
                exam_comment = request.POST.get('description').strip()
                if len(exam_comment) == 0:
                    exam_comment = None

                if len(exam_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Exam name is too short'})
                
                exam_instance = Exams.objects.get(id=edit_exam)
                exam_instance.names = exam_names
                exam_instance.answersheet = CustomSheet.objects.get(id=exam_sheet)
                exam_instance.describe = exam_comment
                exam_instance.lastEdited = datetime.now().replace(tzinfo=pytz.UTC)
                exam_instance.save()
                fdback = {'success': True, 'update_success': True, 'sms': 'Exam info updated successfully!'}
            else:
                exam_names = request.POST.get('exam_name').strip()
                exam_sheet = request.POST.get('answersheet')
                exam_comment = request.POST.get('description').strip()
                if len(exam_comment) == 0:
                    exam_comment = None

                if len(exam_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Exam name is too short'})
                
                Exams.objects.create(
                    names = exam_names,
                    describe = exam_comment,
                    answersheet = CustomSheet.objects.get(id=exam_sheet),
                    teacher = request.user,
                )
                fdback = {'success': True, 'sms': 'New exam created successfully!'}
        except Exception as e:
            fdback = {'success': False, 'sms': 'Unknown error occured'}
        return JsonResponse(fdback)
    return JsonResponse({'success': False, 'sms': 'Invalid data'})

@never_cache
@login_required
def exam_details(request, exam):
    if request.method == 'GET' and Exams.objects.filter(id=exam, teacher=request.user, deleted=False).exists():
        answer_sheets_list = []
        for sheet in CustomSheet.objects.filter(teacher=request.user, published=True):
            check_sheet = Marking_scheme.objects.filter(sheet=sheet)
            if check_sheet.exists() and not check_sheet.filter(qn_answer__isnull=True).exists():
                answer_sheets_list.append({'id': sheet.id, 'name': sheet.names})

        exam_obj = Exams.objects.get(id=exam)
        exam_data = {
            'exam_info': True,
            'answer_sheets': answer_sheets_list,
            'exam': {
                'sheet': exam_obj.answersheet_id,
                'circles_count': exam_obj.answersheet.circles_count,
                'squares_count': exam_obj.answersheet.squares_count,
                'id': exam_obj.id,
                'name': exam_obj.names,
                'dates': exam_obj.regdate.strftime('%d-%b-%Y %H:%M:%S'),
                'lastupdate': exam_obj.lastEdited.strftime('%d-%b-%Y %H:%M:%S') if exam_obj.lastEdited else "N/A",
                'answer_sheet': exam_obj.answersheet.names,
                'sheet_url': reverse('create_custom_sheet', kwargs={'step':2, 'sheet': exam_obj.answersheet_id}),
                'describe': exam_obj.describe if exam_obj.describe else "N/A",
                'info': exam_obj.describe if exam_obj.describe else ""
            }
        }
        return render(request, 'exams/exams.html', context=exam_data)
    if request.method == 'POST' and Exams.objects.filter(id=exam, deleted=False):
        pass
    return redirect('exams_list')

@never_cache
@login_required
def exams_list(request):
    answer_sheets_list = []
    for sheet in CustomSheet.objects.filter(teacher=request.user, published=True):
        check_sheet = Marking_scheme.objects.filter(sheet=sheet)
        if check_sheet.exists() and not check_sheet.filter(qn_answer__isnull=True).exists():
            answer_sheets_list.append({'id': sheet.id, 'name': sheet.names})
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = Exams.objects.filter(teacher=request.user, deleted=False)

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
        for exam in queryset:
            base_data.append({
                'id': exam.id,
                'regDate': exam.regdate,
                'examName': exam.names,
                'sheetName': exam.answersheet.names,
                'questions': Questions.objects.filter(sheet=exam.answersheet).aggregate(total_num=Sum('qn_number'))['total_num'] or 0,
                'info': reverse('exam_details', kwargs={'exam': exam.id})
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
    return render(request, 'exams/exams.html', context={'answer_sheets': answer_sheets_list})

@never_cache
@login_required
def mark_exam(request):
    if request.method == 'POST':
        # try:
            
        # except Exception as e:
        #     print(e)
        #     fdback ={'success': False, 'sms': 'Failed to complete marking process.'}
        image = request.FILES['exam_attachment']
        sheet_id = int(request.POST.get('sheet'), 0)
        exam_id = int(request.POST.get('exam'), 0)
        exam_circles = int(request.POST.get('circles'), 0)
        exam_squares = int(request.POST.get('squares'), 0)
        image_type = imghdr.what(image)
        if image_type not in ['jpeg', 'png', 'jpg']:
            fdback = {'success': False, 'sms': 'Only jpg, jpeg and png are allowed formats!'}
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            _, ext = os.path.splitext(image.name)
            new_filename = timestamp + ext
            img_path = os.path.join(settings.MEDIA_ROOT, new_filename)

            with open(img_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            def map_answer_to_index(option, options, start_range):
                if option in options:
                    index = options.index(option) + start_range
                    return index
                return None

            
            circles_ranges_array, circles_answers, circles_qn_number, circles_qn_marks = [], [], [], []
            squares_ranges_array, squares_answers, squares_qn_number, squares_qn_marks = [], [], [], []
            get_mark_scheme = Marking_scheme.objects.filter(sheet_id=sheet_id)
            total_exam_marks = 0.0
            for item in get_mark_scheme.filter(qn_type='circle').order_by('qn_number'):
                circles_ranges_array.append(str(item.qn_indices))
                start, end = map(int, item.qn_indices.split('-'))
                answer_idx = map_answer_to_index(item.qn_answer, item.qn_options, start)
                circles_answers.append(answer_idx)
                circles_qn_number.append(item.qn_number)
                circles_qn_marks.append(item.question.qn_marks)
                total_exam_marks += item.question.qn_marks

            for item in get_mark_scheme.filter(qn_type='square').order_by('qn_number'):
                squares_ranges_array.append(str(item.qn_indices))
                squares_answers.append(item.qn_answer)
                squares_qn_number.append(item.qn_number)
                squares_qn_marks.append(item.question.qn_marks)
                total_exam_marks += item.question.qn_marks

            def parse_indice_ranges(index_range):
                ranges = []
                for item in index_range:
                    start, end = map(int, item.split('-'))
                    ranges.append((start, end))
                return ranges

            def find_group_index(number, ranges):
                for index, (start, end) in enumerate(ranges):
                    if start <= number <= end:
                        return int(index)
                return None
            
            def read_regnumber(param):
                base_array = [0, 9, 18, 27, 36, 45, 54, 63, 72, 81]
                output_array = []

                # Create the output array of arrays
                for i in range(10):
                    output_array.append([x + i for x in base_array])

                group_results = {}
                for num in param:
                    found = False
                    for i, sub_array in enumerate(output_array):
                        if num in sub_array:
                            group_results.setdefault(i, []).append(sub_array.index(num))
                            found = True
                            break
                    if not found:
                        group_results.setdefault(None, []).append(None)

                # Sort results within each group
                for group, indices in group_results.items():
                    if group is not None:
                        group_results[group].sort()

                # Combine results back into a single list with group order preserved
                result = []
                for i in range(10):
                    result.extend(group_results.get(i, []))
                result.extend(group_results.get(None, []))

                formatted_result = [str(index) if index is not None else "" for index in result]
                formatted_string = f"{''.join(formatted_result[:2])}-{''.join(formatted_result[2:4])}-{''.join(formatted_result[4:])}"

                return formatted_string

            # Parse the ranges
            ranges_circle = parse_indice_ranges(circles_ranges_array)

            total_squares_count, answers_identified = mark_square_questions(img_path, squares_ranges_array, exam_squares)
            total_circles_count, shaded_circles_list = mark_circle_questions(img_path)

            if total_squares_count == exam_squares and total_circles_count == exam_circles:
                # read registration number
                regnumber_circles = [idx for idx in shaded_circles_list if idx <= 89]
                student_regnumber = f"T{read_regnumber(regnumber_circles)}"

                # square answers
                qn_correct, qn_wrong, total_marks, idx = [], [], 0.0, 0
                for item in squares_ranges_array:
                    extracted_answer = answers_identified[idx]
                    question_number = squares_qn_number[idx]
                    correct_answer = squares_answers[idx]
                    question_marks = squares_qn_marks[idx]
                    if extracted_answer == correct_answer:
                        qn_correct.append(question_number)
                        total_marks += question_marks
                    elif not question_number in qn_wrong:
                        qn_wrong.append(f"{question_number}({extracted_answer})")
                    idx += 1

                # shaded-circles answers
                for number in shaded_circles_list:
                    index = find_group_index(number, ranges_circle)
                    if index is not None:
                        question_number = circles_qn_number[index]
                        correct_answer = circles_answers[index]
                        question_marks = circles_qn_marks[index]
                        if number == correct_answer:
                            if question_number in qn_correct:
                                qn_correct.remove(question_number)
                                total_marks -= question_marks
                                if not question_number in qn_wrong:
                                    qn_wrong.append(question_number)
                            else:
                                qn_correct.append(question_number)
                                total_marks += question_marks
                        elif not question_number in qn_wrong:
                            qn_wrong.append(question_number)
                
                # Record marking results
                student_instance = None
                if len(student_regnumber) > 5 and Students.objects.filter(regnumber=student_regnumber).exists():
                    student_instance = Students.objects.filter(regnumber=student_regnumber).first()
                Results.objects.create(
                    exam = Exams.objects.get(id=exam_id),
                    student = student_instance,
                    regnumber = student_regnumber,
                    marks = total_marks,
                    total = total_exam_marks
                )

                fdback = {
                    'success': True,
                    'sms': 'Marking process completed',
                    'regnumber': student_regnumber,
                    'correct': ', '.join(map(str, qn_correct)),
                    'wrong': ', '.join(map(str, qn_wrong)),
                    'marks': f'{total_marks}/{total_exam_marks}'
                }
            else:
                fdback = {'success': False, 'sms': 'Failed to capture all exam questions'}
            
            if os.path.exists(img_path):
                os.remove(img_path)
        return JsonResponse(fdback)
    return JsonResponse({'success': False, 'sms': 'Invalid data!'})

@never_cache
@login_required
def results_list(request, exam):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = Results.objects.filter(exam_id=exam).order_by('-id')

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
        for result in queryset:
            base_data.append({
                'id': result.id,
                'regDate': result.regdate,
                'regnumber': result.regnumber if result.regnumber else 'N/A',
                'names': result.student.names if result.student else 'N/A',
                'program': result.student.program.abbrev if result.student else 'N/A',
                'marks': result.marks
            })

        
        # Total records before filtering
        total_records = len(base_data)

        # Define a mapping from DataTables column index to the corresponding model field
        column_mapping = {
            0: 'id',
            1: 'regDate',
            2: 'regnumber',
            3: 'names',
            4: 'program',
            5: 'marks',
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
                        if column_field == 'marks':
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
                'regDate': item.get('regDate').strftime('%d-%b-%Y'),
                'regnumber': item.get('regnumber'),
                'names': item.get('names'),
                'program': item.get('program'),
                'marks': item.get('marks')
            })

        ajax_response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': records_filtered,
            'data': final_data,
        }
        return JsonResponse(ajax_response)
