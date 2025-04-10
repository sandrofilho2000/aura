from django.contrib import admin
from .models import SubAccount

class SubAccountAdmin(admin.ModelAdmin):
    list_display = ['name']
