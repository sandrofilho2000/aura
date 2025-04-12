from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Billing, BillingSplit
from django.db.models import Q

class BillingSplitInline(admin.TabularInline):
    model = BillingSplit
    extra = 0

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    inlines = [BillingSplitInline]

    readonly_fields = (
        "paylink",
        "asaasId",
        "created_at",
        "created_by",  # campo não editável
    )

    list_display = (
        "title",
        "link_clickável",
        "value",
        "billingType",
        "customer_name",
        "criado_por",  # exibição do usuário criador
    )

    verbose_name = "Link de pagamento"
    verbose_name_plural = "Links de pagamentos"

    fieldsets_base = (
        (_('Informações da cobrança'), {
            'fields': (
                'title',
                'value',
                'billingType',
                'dueDate',
                'installmentCount',
                'customer',
                'created_at',
                'created_by',
            )
        }),
        (_('Callback'), {
            'fields': (
                'successUrl',
                'autoRedirect',
            )
        }),
        (_('Informações do Asaas'), {
            'fields': (
                'paylink',
                'asaasId',
            )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets_base)

        if request.user.groups.filter(name='Vendedores').exists() and obj:
            fieldsets.append(
                (_('Sua comissão'), {
                    'fields': (
                        'comissao_percentual_usuario',
                        'comissao_fixa_usuario',
                    )
                })
            )
        return fieldsets

    def get_queryset(self, request): 
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name='Vendedores').exists():
            return qs.filter(
                Q(splits__subaccount=request.user) | Q(created_by=request.user)
            ).distinct()

        return qs

    def get_form(self, request, obj=None, **kwargs):
        self._request_user = request.user
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.groups.filter(name='Vendedores').exists():
            readonly += ['comissao_percentual_usuario', 'comissao_fixa_usuario']
        return readonly

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def criado_por(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "-"
    criado_por.short_description = "Criado por"

    def link_clickável(self, obj):
        if obj.paylink:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.paylink, obj.paylink)
        return "-"
    link_clickável.short_description = "Link de Pagamento"

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "-"
    customer_name.short_description = "Cliente"

    def comissao_percentual_usuario(self, obj):
        split = obj.splits.filter(subaccount=self._request_user).first()
        return f"{split.percentualValue}%" if split else "-"
    comissao_percentual_usuario.short_description = "Comissão (%)"

    def comissao_fixa_usuario(self, obj):
        split = obj.splits.filter(subaccount=self._request_user).first()
        return f"R$ {split.fixedValue:.2f}" if split and split.fixedValue else "-"
    comissao_fixa_usuario.short_description = "Comissão Fixa"
