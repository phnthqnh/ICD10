# ICD10/forms.py
import os
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ICD10.models.user import User
from  utils.utils import Utils
from django.conf import settings
from unfold.forms import AdminPasswordChangeForm as UnfoldPasswordChangeForm
from django.contrib.auth import password_validation

# UNFOLD_INPUT_CLASS = (
#     "border border-base-200 rounded-default bg-white font-medium min-w-20 placeholder-base-400"
#     "shadow-xs text-font-default-light text-sm"
#     "focus:outline-2 focus:-outline-offset-2 focus:outline-primary-600" 
#     "group-[.errors]:border-red-600 focus:group-[.errors]:outline-red-600"
#     "dark:bg-base-900 dark:border-base-700 dark:text-font-default-dark" 
#     "dark:group-[.errors]:border-red-500 dark:focus:group-[.errors]:outline-red-500" 
#     "dark:scheme-dark group-[.primary]:border-transparent disabled:!bg-base-50" 
#     "dark:disabled:!bg-base-800 px-3 py-2 w-full max-w-2xl"
# )
class UserCreationForm(forms.ModelForm):
    """Form dùng để tạo user trong admin"""
    # password1 = forms.CharField(
    #     label="Password",
    #     widget=forms.PasswordInput(attrs={'class': UNFOLD_INPUT_CLASS})
    # )
    # password2 = forms.CharField(
    #     label="Confirm password",
    #     widget=forms.PasswordInput(attrs={'class': UNFOLD_INPUT_CLASS})
    # )
    def make_random_password(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    class Meta:
        model = User
        fields = ("username", "email", "role", "status")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        # raw_password = self.cleaned_data["password1"]
        # user.set_password(self.cleaned_data["password1"])
        raw_password = self.make_random_password()
        user.set_password(raw_password)
        self.raw_password = raw_password
        if commit:
            user.save()
            # Tạo token
            token = Utils.generate_verification_token(user)
            activation_url = settings.ACTIVATION_URL
            activation_link = f"{activation_url}?token={token}"
            # Gửi email
            Utils.admin_send_activation_email(
                user=user,
                activation_link=activation_link,
                password=raw_password  # gửi kèm password
            )
        return user


class UserChangeForm(forms.ModelForm):
    """Form dùng để sửa user trong admin"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "status",
            "is_staff",
            "is_superuser",
            "role",
            "is_verified_doctor",
        )


class CustomPasswordChangeForm(UnfoldPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom labels
        self.fields['old_password'].label = "Mật khẩu cũ"
        self.fields['new_password1'].label = "Mật khẩu mới"
        self.fields['new_password2'].label = "Xác nhận mật khẩu mới"
        
        # Custom help texts
        self.fields['new_password1'].help_text = '<br>'.join([
            "Mật khẩu của bạn phải:",
            "• Có ít nhất 8 ký tự",
            "• Phải chứa cả chữ và số"
        ])