from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Student_class
from utils.util_functions import parse_datetime
from datetime import datetime
import pytz


# tanzania/east africa timezone
format_datetime = "%Y-%m-%d %H:%M:%S.%f"


@never_cache
@login_required
def classes_list(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 0))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # Base queryset
        queryset = Student_class.objects.filter(deleted=False)

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
        for st_class in queryset:
            base_data.append({
                'id': st_class.id,
                'regDate': st_class.regdate,
                'names': st_class.names,
                'abbrev': st_class.abbrev,
                'students': 0,
                'info': reverse('class_details', kwargs={'class_id': st_class.id})
            })

        
        # Total records before filtering
        total_records = len(base_data)

        # Define a mapping from DataTables column index to the corresponding model field
        column_mapping = {
            0: 'id',
            1: 'regDate',
            2: 'names',
            3: 'abbrev',
            4: 'students',
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
                        if column_field == 'students':
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
                'abbrev': item.get('abbrev'),
                'students': item.get('students'),
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
    return render(request, 'st_classes/classes.html')


@never_cache
@login_required
def class_actions(request):
    if request.method == 'POST':
        try:
            edit_class = request.POST.get('edit_class')
            delete_class = request.POST.get('delete_class')
            if delete_class:
                program = Student_class.objects.get(id=delete_class)
                program.deleted = True
                program.save()
                fdback = {'success': True, 'url':reverse('classes_list')}
            elif edit_class:
                class_names = request.POST.get('names').strip()
                class_abbrev = request.POST.get('abbrev').strip()
                class_comment = request.POST.get('description').strip()
                class_duration = request.POST.get('duration')
                if len(class_comment) == 0:
                    class_comment = None

                if len(class_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Class names is too short'})
                
                if len(class_abbrev) < 2:
                    return JsonResponse({'success': False, 'sms': 'Class abbrev is too short'})
                
                program = Student_class.objects.get(id=edit_class)
                program.names = class_names
                program.abbrev = class_abbrev
                program.describe = class_comment
                program.duration = class_duration
                program.lastEdited = datetime.now().replace(tzinfo=pytz.UTC)
                program.save()
                fdback = {'success': True, 'update_success':True, 'sms': 'Class/program info updated!'}
            else:
                class_names = request.POST.get('names').strip()
                class_abbrev = request.POST.get('abbrev').strip()
                class_comment = request.POST.get('description').strip()
                class_duration = request.POST.get('duration')
                if len(class_comment) == 0:
                    class_comment = None

                if len(class_names) < 3:
                    return JsonResponse({'success': False, 'sms': 'Class names is too short'})
                
                if len(class_abbrev) < 2:
                    return JsonResponse({'success': False, 'sms': 'Class abbrev is too short'})
                
                Student_class.objects.create(
                    names = class_names,
                    abbrev = class_abbrev,
                    duration = class_duration,
                    describe = class_comment,
                    teacher = request.user,
                )
                fdback = {'success': True, 'sms': 'New class created successfully!'}
        except Exception as e:
            print(e)
            fdback = {'success': False, 'sms': 'Unknown error occured'}
        return JsonResponse(fdback)
    return JsonResponse({'success': False, 'sms': 'Invalid data'})


@never_cache
@login_required
def class_details(request, class_id):
    if request.method == 'GET' and Student_class.objects.filter(id=class_id, deleted=False).exists():
        st_class = Student_class.objects.get(id=class_id)
        class_data = {
            'id': class_id,
            'regdate': st_class.regdate.strftime('%d-%b-%Y %H:%M:%S'),
            'names': st_class.names,
            'abbrev': st_class.abbrev,
            'describe': st_class.describe if st_class.describe else 'N/A',
            'students': 0,
            'duration': st_class.duration if st_class.duration else '',
            'info': st_class.describe if st_class.describe else '',
            'lastEdit': st_class.lastEdited.strftime('%d-%b-%Y %H:%M:%S') if st_class.lastEdited else "N/A",
        }
        context = {
            'class_info': class_id,
            'class': class_data,
        }
        return render(request, 'st_classes/classes.html', context)
    return JsonResponse({'status': False, 'message': 'Invalid request'})