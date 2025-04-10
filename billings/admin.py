from django.contrib import admin
from .models import Billing, BillingSplit
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

class BillingSplitInline(admin.TabularInline):
    model = BillingSplit
    extra = 1

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    inlines = [BillingSplitInline]
    readonly_fields = ("paylink", "asaasId", "created_at") 
    list_display = ("title", "link_clickável", "value", "billingType", "customer_name")
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
                'created_at'
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
            return qs.filter(splits__subaccount=request.user).distinct()

        return qs

    def comissao_percentual_usuario(self, obj):
        split = obj.splits.filter(subaccount=self._request_user).first()
        return f"{split.percentualValue}%" if split else "-"

    def comissao_fixa_usuario(self, obj):
        split = obj.splits.filter(subaccount=self._request_user).first()
        return f"R$ {split.fixedValue:.2f}" if split and split.fixedValue else "-"

    def get_form(self, request, obj=None, **kwargs):
        self._request_user = request.user
        return super().get_form(request, obj, **kwargs)

    def link_clickável(self, obj):
        if obj.paylink:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.paylink, obj.paylink)
        return "-"
    link_clickável.short_description = "Link de Pagamento"

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "-"
    customer_name.short_description = "Cliente"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.groups.filter(name='Vendedores').exists():
            readonly += ['comissao_percentual_usuario', 'comissao_fixa_usuario']
        return readonly
