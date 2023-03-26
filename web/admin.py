from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OAuth2Token


# Register your models here.
class UserAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class OAuth2Admin(admin.ModelAdmin):
    list_display = ('name', 'access_token', 'user')
    search_fields = ('name', 'access_token', 'user')
    readonly_fields = ('name', 'access_token', 'user')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CustomUser, UserAdmin)
admin.site.register(OAuth2Token, OAuth2Admin)
