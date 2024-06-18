from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.exams_list, name='exams_list'),
    path('new-exam/', v.exams_actions, name='exam_actions'),
    path('<int:exam>/', v.exam_details, name='exam_details'),
    path('mark-exam/', v.mark_exam, name='mark_exam'),
    path('results/<int:exam>/', v.results_list, name='exam_results'),
]
