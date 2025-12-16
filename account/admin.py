from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib import admin, messages
from asaas.models import AfiliadoAsaas, AsaasConfig
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import requests
from django.urls import reverse, resolve


class AfiliadoAsaasInline(admin.StackedInline):
    model = AfiliadoAsaas
    extra = 0
    max_num = 1
    can_delete = False

    readonly_fields = ["status_badge", "delete_link"]
    # Link de exclusão
    def delete_link(self, instance):
        if not instance or not instance.pk:
            return ""
        url = reverse("admin:asaas_asaasconfig_delete", args=[instance.pk])
        return mark_safe(
            f'<a href="{url}" '
            f'style="display: block; background: var(--delete-button-bg); '
            f"border-radius: 4px; padding: 0.625rem 0.9375rem; "
            f'line-height: 0.9375rem; color: var(--button-fg);">'
            f"Excluir integração Asaas</a>"
        )

    delete_link.short_description = "Excluir"

    # Badge de status
    def status_badge(self, instance):
        if not instance or not instance.status:
            return "-"

        css_class = "badge badge-" + instance.status.replace("_", "-").replace(
            "ã", "a"
        ).replace("í", "i")

        return format_html(
            '<span class="{}">{}</span>', css_class, instance.get_status_display()
        )

    status_badge.short_description = "Status"

    # Campos exibidos
    def get_fields(self, request, obj=None):
        if not obj:
            return ["token_api"]

        instance = obj.asaas_config.first()

        base = ["status_badge", "externalId", "delete_link"]

        if instance:
            if instance.status == "conectado":
                return base
            else:
                return ["token_api"] + base

        return ["token_api"]

    def has_add_permission(self, request, obj):
        # Só permite adicionar se não existir ainda
        if AfiliadoAsaas.objects.filter(afiliado=obj).exists():
            return False
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Informações Pessoais"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "cpf_cnpj",
                    "birth_date",
                    "company_type",
                    "income_value",
                )
            },
        ),
        (_("Contato"), {"fields": ("phone", "mobile_phone", "site")}),
        (
            _("Endereço"),
            {
                "fields": (
                    "address",
                    "address_number",
                    "complement",
                    "province",
                    "postal_code",
                )
            },
        ),
        (_("Comissão"), {"fields": ("fixedValue", "percentualValue")}),
        (
            _("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Datas Importantes"), {"fields": ("last_login", "date_joined")}),
    )
    inlines = [AfiliadoAsaasInline]
    filter_horizontal = ("groups", "user_permissions", "groups")

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "get_groups",
    )
    search_fields = ("email", "username", "first_name", "last_name", "cpf_cnpj")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email", "username", "date_joined")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "birth_date"),
            },
        ),
    )

    def get_groups(self, obj):
        return ", ".join([profile.name for profile in obj.groups.all()])

    get_groups.short_description = _("Perfis")

    # ---------------------------------------------------------------------
    # 🛑 BLOQUEAR EXCLUSÃO DE SI MESMO E DE SUPERUSUÁRIOS
    # ---------------------------------------------------------------------
    def has_delete_permission(self, request, obj=None):
        # Superuser pode excluir qualquer um EXCETO ele mesmo
        if obj:
            if obj.pk == request.user.pk:
                return False  # impedir excluir a si mesmo

            if obj.is_superuser and not request.user.is_superuser:
                return False  # impedir que não-super delete super

            # mesmo superuser não pode excluir outro superuser (boa prática)
            if obj.is_superuser:
                return False

        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        # bloqueio em massa

        if queryset.filter(pk=request.user.pk).exists():
            messages.error(request, "Você não pode excluir sua própria conta.")
            return

        if queryset.filter(is_superuser=True).exists():
            messages.error(request, "Você não pode excluir superusuários.")
            return

        return super().delete_queryset(request, queryset)

    # ---------------------------------------------------------------------
    # RESTRIÇÕES QUE VOCÊ JÁ TINHA — mantidas
    # ---------------------------------------------------------------------
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is not None and obj != request.user:
            return False

        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)

        campos_restritos = [
            "fixedValue",
            "cpf_cnpj",
            "username",
            "percentualValue",
            "last_login",
            "date_joined",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

        return list(
            set(super().get_readonly_fields(request, obj)) | set(campos_restritos)
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            fieldsets = [fs for fs in fieldsets if fs[0] != _("Permissões")]

        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(pk=request.user.pk)

    def get_inline_instances(self, request, obj=None):
        integracao_existe = AsaasConfig.objects.filter(status="conectado").exists()

        inline_instances = []
        for inline_class in self.inlines:
            # Se este inline for o AfiliadoAsaasInline e NÃO houver integração → não adiciona
            if inline_class is AfiliadoAsaasInline and not integracao_existe:
                continue

            inline_instances.append(inline_class(self.model, self.admin_site))

        return inline_instances
