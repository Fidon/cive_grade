from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from apps.classes.models import Student_class
from .models import Students
from utils.util_functions import parse_datetime


# tanzania/east africa timezone
format_datetime = "%Y-%m-%d %H:%M:%S.%f"


@never_cache
@login_required
def students_list(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = Students.objects.filter(deleted=False)

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
        for student in queryset:
            base_data.append({
                'id': student.id,
                'regDate': student.regdate,
                'names': student.names,
                'regnumber': student.regnumber,
                'program': student.program.abbrev,
                'year': student.year,
                'info': reverse('student_details', kwargs={'student': int(student.id)})
            })

        
        # Total records before filtering
        total_records = len(base_data)

        # Define a mapping from DataTables column index to the corresponding model field
        column_mapping = {
            0: 'id',
            1: 'regDate',
            2: 'names',
            3: 'regnumber',
            4: 'program',
            5: 'year'
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
                        if column_field == 'year':
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
                'names': item.get('names'),
                'regnumber': item.get('regnumber'),
                'program': item.get('program'),
                'year': item.get('year'),
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
    programs = Student_class.objects.filter(deleted=False)
    return render(request, 'students/students.html', {'programs': programs})


@never_cache
@login_required
def student_actions(request):
    if request.method == 'POST':
        try:
            edit_student = request.POST.get('edit_student')
            delete_student = request.POST.get('delete_student')
            if delete_student:
                student = Students.objects.get(id=delete_student)
                student.deleted = True
                student.save()
                fdback = {'success': True, 'url':reverse('students_list')}
            elif edit_student:
                student_names = request.POST.get('names').strip().upper()
                student_regno = request.POST.get('regnumber').strip().upper()
                student_program = int(request.POST.get('program'), 0)
                student_year = int(request.POST.get('year'), 0)
                program = Student_class.objects.get(id=student_program)

                if len(student_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Student name is too short'})
                
                if len(student_regno) < 12:
                    return JsonResponse({'success': False, 'sms': 'Reg# is too short'})
                
                if Students.objects.filter(regnumber=student_regno).exclude(id=edit_student).exists():
                    return JsonResponse({'success': False, 'sms': 'Registration number is already registered'})
                
                if student_year < 1 or student_year > program.duration:
                    return JsonResponse({'success': False, 'sms': 'Year of study exceeds program duration'})
                
                student_instance = Students.objects.get(id=edit_student)
                student_instance.names = student_names
                student_instance.regnumber = student_regno
                student_instance.year = student_year
                student_instance.program = program
                student_instance.save()
                fdback = {'success': True, 'update_success':True, 'sms': 'Student info updated!'}
            else:
                student_names = request.POST.get('names').strip().upper()
                student_regno = request.POST.get('regnumber').strip().upper()
                student_program = int(request.POST.get('program'), 0)
                student_year = int(request.POST.get('year'), 0)
                program = Student_class.objects.get(id=student_program)

                if len(student_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Student name is too short'})
                
                if len(student_regno) < 12:
                    return JsonResponse({'success': False, 'sms': 'Reg# is too short'})
                
                if Students.objects.filter(regnumber=student_regno).exists():
                    return JsonResponse({'success': False, 'sms': 'Registration number is already registered'})
                
                if student_year < 1 or student_year > program.duration:
                    return JsonResponse({'success': False, 'sms': 'Year of study exceeds program duration'})
                
                Students.objects.create(
                    names = student_names,
                    regnumber = student_regno,
                    year = student_year,
                    program = program,
                )
                fdback = {'success': True, 'sms': 'New student registered successfully!'}
        except Exception as e:
            fdback = {'success': False, 'sms': 'Unknown error occured'}
        return JsonResponse(fdback)
    return JsonResponse({'success': False, 'sms': 'Invalid data'})


@never_cache
@login_required
def student_details(request, student):
    if request.method == 'GET' and Students.objects.filter(id=student, deleted=False).exists():
        student = Students.objects.get(id=student)
        student_data = {
            'id': student.id,
            'regdate': student.regdate.strftime('%d-%b-%Y %H:%M:%S'),
            'names': student.names,
            'regno': student.regnumber,
            'program': f"{student.program.names} ({student.program.abbrev})",
            'program_id': student.program_id,
            'year': student.year
        }
        context = {
            'student_info': student,
            'student': student_data,
            'programs': Student_class.objects.filter(deleted=False)
        }
        return render(request, 'students/students.html', context)
    return JsonResponse({'status': False, 'message': 'Invalid request'})