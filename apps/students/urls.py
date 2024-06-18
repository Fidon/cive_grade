from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.students_list, name='students_list'),
    path('new-student/', v.student_actions, name='student_actions'),
    path('<int:student>/', v.student_details, name='student_details'),
]
