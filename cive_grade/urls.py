from django.contrib import admin
from django.urls import include, path
from . import views as v
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', v.home_page, name='home_url'),

    path('', include('apps.users.urls')),
    path('civegrade/', include('apps.users.urls')),
    path('answers/', include('apps.answer_sheets.urls')),
    path('exams/', include('apps.exams.urls')),
    path('programs/', include('apps.classes.urls')),
    path('students/', include('apps.students.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
