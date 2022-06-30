from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
