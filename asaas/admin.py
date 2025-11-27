from django.contrib import admin
from .models import AsaasConfig

class AsaasConfigInline(admin.StackedInline):
    model = AsaasConfig
    extra = 0
    readonly_fields = ["atualizado_em"]

    def get_fields(self, request, obj=None):
        base = ["atualizado_em"]

        instance = getattr(obj, "asaas_config", None)

        if instance and instance.token_api:
            return base

        return ["token_api"] + base