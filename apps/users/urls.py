from django.contrib import admin
from django.urls import include, path
from . import views as v

urlpatterns = [
    path('register/', v.register_page, name='register_url'),
    path('', v.login_page, name='auth_url'),
    path('auth/', v.login_page, name='auth_url'),
    path('logout/', v.logout_view, name='logout_url'),
]