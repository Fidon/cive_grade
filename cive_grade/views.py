from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required


@never_cache
@login_required
def home_page(request):
    return render(request, 'home.html')



