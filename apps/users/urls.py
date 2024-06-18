from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.login_page, name='auth_url'),
    path('auth/', v.login_page, name='auth_url'),
    path('logout/', v.logout_view, name='logout_url'),
    path('users/', v.users_list, name='users_list'),
    path('users/<int:user_id>/', v.user_details, name='user_details'),
    path('users/actions/', v.users_actions, name='user_actions'),
    path('user/profile/', v.profile_page, name='user_profile'),
]