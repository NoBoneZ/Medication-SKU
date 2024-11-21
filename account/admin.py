from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserAccountActivationOTP
# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_account_verified")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": (
        "email", "full_name", "address", "is_account_verified")}),
    )

class UserAccountActivationOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "expires")


admin.site.register(UserAccountActivationOTP, UserAccountActivationOTPAdmin)
admin.site.register(User, CustomUserAdmin)