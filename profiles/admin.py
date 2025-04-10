from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import Group
from admin.models import BaseAdmin

admin.site.unregister(Group)

@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    filter_horizontal = ('permissions',)