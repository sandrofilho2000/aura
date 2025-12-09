from django.contrib import admin
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.shortcuts import redirect

from .models import AsaasConfig


# INLINE usado dentro do admin de Integration
class AsaasConfigInline(admin.StackedInline):
    model = AsaasConfig
    extra = 0
    can_delete = False

    readonly_fields = ["status_badge", "atualizado_em", "delete_link"]

    # Link de exclusão
    def delete_link(self, instance):
        if not instance or not instance.pk:
            return ""
        url = reverse("admin:asaas_asaasconfig_delete", args=[instance.pk])
        return mark_safe(
            f'<a href="{url}" '
            f'style="display: block; background: var(--delete-button-bg); '
            f'border-radius: 4px; padding: 0.625rem 0.9375rem; '
            f'line-height: 0.9375rem; color: var(--button-fg);">'
            f'Excluir integração Asaas</a>'
        )

    delete_link.short_description = "Excluir"

    # Badge de status
    def status_badge(self, instance):
        if not instance or not instance.status:
            return "-"

        css_class = (
            "badge badge-" +
            instance.status.replace("_", "-")
            .replace("ã", "a")
            .replace("í", "i")
        )

        return format_html(
            '<span class="{}">{}</span>',
            css_class,
            instance.get_status_display()
        )

    status_badge.short_description = "Status"

    # Campos exibidos
    def get_fields(self, request, obj=None):
        if not obj:
            return ["token_api"]

        instance = getattr(obj, "asaas_config", None)

        base = ["status_badge", "atualizado_em", "delete_link"]

        if instance:
            if instance.status == "conectado":
                return base
            else:
                return ["token_api"] + base

        return ["token_api"]


# ADMIN que realmente controla o modelo AsaasConfig
class AsaasConfigAdmin(admin.ModelAdmin):
    readonly_fields = ["status_badge"]
    # Redireciona a list view (ex: /admin/asaas/asaasconfig/)
    
    def changelist_view(self, request, extra_context=None):
        return redirect("/admin/integrations/integration/1/change/")

    # Redireciona qualquer outra view do admin do AsaasConfig, exceto delete
    def change_view(self, request, object_id, form_url="", extra_context=None):
        return redirect("/admin/integrations/integration/1/change/")

    def add_view(self, request, form_url="", extra_context=None):
        return redirect("/admin/integrations/integration/1/change/")

    def has_view_permission(self, request, obj=None):
        # Permite delete funcionar
        current_url = resolve(request.path_info).url_name or ""

        if current_url.endswith("_delete"):
            return super().has_view_permission(request, obj)

        return True

    def status_badge(self, instance):
        if not instance or not instance.status:
            return "-"

        css_class = (
            "badge badge-" +
            instance.status.replace("_", "-")
            .replace("ã", "a")
            .replace("í", "i")
        )

        return format_html(
            '<span class="{}">{}</span>',
            css_class,
            instance.get_status_display()
        )

    status_badge.short_description = "Status"

    # Campos exibidos
    def get_fields(self, request, obj=None):
        if not obj:
            return ["externalId"]

        instance = getattr(obj, "asaas_config", None)

        base = ["status_badge"]

        if instance:
            if instance.status == "conectado":
                return base
            else:
                return ["externalId"] + base

        return ["externalId"]

admin.site.register(AsaasConfig, AsaasConfigAdmin)
