from django.contrib import admin
from .models import Integration
from asaas.admin import AsaasConfigInline

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    exclude = ("name",)     # remove o campo do formulário
    inlines = [AsaasConfigInline]

    def has_add_permission(self, request):
        return False   