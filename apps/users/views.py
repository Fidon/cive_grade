from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from apps.users.forms import CustomUserForm, CustomAuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@never_cache
def register_page(request):
    redirect_url = reverse('home_url')
    if request.user.is_authenticated:
        response = redirect(redirect_url)
        response.set_cookie('user_id', request.user.username)
        return response
    if request.method == 'POST':
        try:
            form = CustomUserForm(request.POST)
            if form.is_valid():
                form.save()
                fdback = {'success': True, 'sms': 'Registration completed!'}
            else:
                errorMsg = ""
                if 'username' in form.errors:
                    errorMsg = form.errors['username'][0]
                if 'phone' in form.errors:
                    errorMsg = form.errors['phone'][0]
                fdback = {'success': False, 'sms': errorMsg}
                print(f"Error sms: {errorMsg}")
        except Exception as e:
            print(f"Error: {e}")
            fdback = {'success': False, 'sms': 'Unknown error!'}
        return JsonResponse(fdback)
    return render(request, 'register.html')


@never_cache
def login_page(request):
    redirect_url = reverse('home_url')
    if request.user.is_authenticated:
        response = redirect(redirect_url)
        response.set_cookie('user_id', request.user.username)
        return response
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and not user.blocked and not user.deleted:
                login(request, user)
                response = JsonResponse({'success': True, 'url': redirect_url})
                response.set_cookie('user_id', user.username)
        else:
            response = JsonResponse({'success': False, 'sms': form.errors['__all__'][0], 'error':form.errors})
        return response
    return render(request, 'auth.html')


@login_required
def logout_view(request):
  if request.user.is_authenticated:
    logout(request)
  return redirect(reverse('auth_url'))
