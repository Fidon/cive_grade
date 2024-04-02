from django.urls import path
from . import views as v

urlpatterns = [
    path('select-answer-sheet/', v.answer_sheets_page, name='ans_sheets'),
    path('create-custom-sheet/<int:step>/<int:sheet>/', v.answer_sheets_page, name='create_custom_sheet'),
    path('create-custom-sheet/<int:step>/', v.answer_sheets_page, name='create_custom_sheet'),
    path('download/<int:questions>/', v.download_answersheet, name='download_sheet'),
    path('custom-answer-sheets/list/', v.custom_sheets_list, name='custom_list'),
    path('save/custom-sheet/', v.save_custom_sheets, name='save_sheet'),
]
