from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from webook.users.forms import (
    UserChangeForm,
    UserCreationForm,
)

User = get_user_model()


# @admin.register(User)
# class UserAdmin(auth_admin.UserAdmin):

#     form = UserChangeForm
#     add_form = UserCreationForm
#     fieldsets = (
#         ("User", {"fields": ("name",)}),
#     ) + auth_admin.UserAdmin.fieldsets
#     list_display = ["username", "name", "is_superuser"]
#     search_fields = ["name"]

@admin.register(User)
class CustomUserAdmin(auth_admin.UserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
