from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Billing, BillingSplit
from django.db.models import Q
from account.models import User
from django.contrib import admin, messages
import requests
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import admin, messages


def delete_billing_from_asaas(asaasId):
    url = f"https://api-sandbox.asaas.com/v3/payments/{asaasId}"

    headers = {
        "accept": "application/json",
        "access_token": "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjFiMWE5OTM4LTI0YjUtNGE1YS1iMzZmLWVjOGRlZGVmMWUwMjo6JGFhY2hfNTU0NGI4NDQtMTczZC00NWUzLTliY2UtNmZhYzQ4MjA5N2M0"
    }

    response = requests.delete(url, headers=headers)
    print("response.status_code: ", response.status_code)
    print("response.json(): ", response.json())
    if response.status_code == 200:
        return {
            'status': response.status_code,
            'description': "Cobrança deletada com sucesso!"
        }
    
    else:
        try:
            response_text = response.json() 
            errors = response_text.get('errors', [])
            if errors:
                for error in errors:
                    return {
                        'status': 400,
                        'description': error.get('description', 'Erro desconhecido')
                    }
        except ValueError:  
            return {
                'status': response.status_code,
                'description': f"Erro desconhecido, código {response.status_code} recebido. Corpo da resposta: {response.text}"
            }

        return {
            'status': response.status_code,
            'description': f"Erro desconhecido, código {response.status_code} recebido. Corpo da resposta: {response.text}"
        }
    

class BillingSplitInline(admin.TabularInline):
    model = BillingSplit
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subaccount":
            kwargs["queryset"] = User.objects.exclude(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    inlines = [BillingSplitInline]
    actions = None
    readonly_fields = (
        "paylink",
        "asaasId",
        "created_at",
        "created_by",  
    )

    list_display = (
        "title",
        "link_clickável",
        "value",
        "billingType",
        "customer_name",
        "criado_por",  
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


    def save_model(self, request, obj, form, change):
        if not obj.paylink:
            super().save_model(request, obj, form, change)
        elif not obj.pk:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)    
        else:
            messages.warning(request, "Você não pode salvar este modelo pois ele já possui um link de pagamento.")


    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj.asaasId:
            print("obj: ", obj.asaasId) 
            print("request.method: ", request.method) 
            if request.method == 'POST':
                response_data = delete_billing_from_asaas(obj.asaasId)

                if response_data['status'] != 200:
                    messages.error(request, response_data['description'])
                    return HttpResponseRedirect(reverse('admin:billings_billing_changelist'))

        return super().delete_view(request, object_id, extra_context=extra_context)
    




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
