from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


User = get_user_model()

# Teacher registration form
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['fullname', 'username', 'phone', 'password']

    def clean_fullname(self):
        getName = self.cleaned_data['fullname'].strip()
        fullname = ' '.join(word.capitalize() for word in getName.split())
        return fullname

    def clean_username(self):
        username = self.cleaned_data['username'].strip().capitalize()
        if len(username) < 3:
            raise forms.ValidationError("Username is too short.")
        if not username.isalpha():
            raise forms.ValidationError("Username should contain only alphabets A-Z.")
        if self.instance and self.instance.pk:
            if User.objects.filter(username=username, deleted=False).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already used by another teacher.")
        else:
            if User.objects.filter(username=username, deleted=False).exists():
                raise forms.ValidationError("This username is already used by another teacher.")
        return username
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Please use a 10-digit phone number.")
        if phone and len(phone) != 10:
            raise forms.ValidationError("Please use a 10-digit phone number.")
        if self.instance and self.instance.pk:
            if User.objects.filter(phone=phone, deleted=False).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This phone is already used by another teacher.")
        else:
            if User.objects.filter(phone=phone, deleted=False).exists():
                raise forms.ValidationError("This phone is already used by another teacher.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        user.set_password(password)
        if commit:
            user.save()
        return user
    
    


# Teacher login form
class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Incorrect username or password.")
            if user.blocked:
                raise forms.ValidationError("Account blocked, contact your admin.")
            if user.deleted:
                raise forms.ValidationError("Invalid account, contact your admin.")

        return self.cleaned_data
