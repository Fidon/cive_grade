from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.classes_list, name='classes_list'),
    path('new-class/', v.class_actions, name='class_actions'),
    path('<int:class_id>/', v.class_details, name='class_details'),
]
