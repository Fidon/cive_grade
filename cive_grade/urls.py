from django.contrib import admin
from django.urls import include, path
from . import views as v
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', v.home_page, name='home_url'),
    path('upload-majibu/', v.upload_majibu, name='upload_majibu'),

    path('', include('apps.users.urls')),
    path('civegrade/', include('apps.users.urls')),
    path('answers/', include('apps.answer_sheets.urls')),
    # path('classes/', include('apps.classes.urls')),
    # path('exams/', include('apps.exams.urls')),
    # path('students/', include('apps.students.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
