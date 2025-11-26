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
from django.conf import settings
from django.utils.safestring import mark_safe

friendly_status = {
"PAYMENT_AUTHORIZED": "Pagamento autorizado",
"PAYMENT_APPROVED_BY_RISK_ANALYSIS": "Aprovado pela análise de risco",
"PAYMENT_CREATED": "Cobrança criada",
"PAYMENT_CONFIRMED": "Pagamento confirmado",
"PAYMENT_ANTICIPATED": "Pagamento antecipado",
"PAYMENT_DELETED": "Cobrança removida",
"PAYMENT_REFUNDED": "Estornado",
"PAYMENT_REFUND_DENIED": "Estorno negado",
"PAYMENT_CHARGEBACK_REQUESTED": "Chargeback solicitado",
"PAYMENT_AWAITING_CHARGEBACK_REVERSAL": "Aguardando repasse após disputa",
"PAYMENT_DUNNING_REQUESTED": "Negativação solicitada",
"PAYMENT_CHECKOUT_VIEWED": "Fatura visualizada",
"PAYMENT_PARTIALLY_REFUNDED": "Estorno parcial",
"PAYMENT_SPLIT_DIVERGENCE_BLOCK": "Valor bloqueado por split divergente",
"PAYMENT_AWAITING_RISK_ANALYSIS": "Aguardando análise de risco",
"PAYMENT_REPROVED_BY_RISK_ANALYSIS": "Reprovado pela análise de risco",
"PAYMENT_UPDATED": "Cobrança atualizada",
"PAYMENT_RECEIVED": "Pagamento recebido",
"PAYMENT_OVERDUE": "Atrasado",
"PAYMENT_RESTORED": "Cobrança restaurada",
"PAYMENT_REFUND_IN_PROGRESS": "Estorno em processamento",
"PAYMENT_RECEIVED_IN_CASH_UNDONE": "Recebimento em dinheiro desfeito",
"PAYMENT_CHARGEBACK_DISPUTE": "Disputa de chargeback",
"PAYMENT_DUNNING_RECEIVED": "Recebimento negativado",
"PAYMENT_BANK_SLIP_VIEWED": "Boleto visualizado",
"PAYMENT_CREDIT_CARD_CAPTURE_REFUSED": "Captura do cartão recusada",
"PAYMENT_SPLIT_CANCELLED": "Split cancelado",
"PAYMENT_SPLIT_DIVERGENCE_BLOCK_FINISHED": "Bloqueio de split finalizado",
}

def delete_billing_from_asaas(asaasId):
    url = f"{settings.ASAAS_URL_API}/payments/{asaasId}"

    headers = {
        "accept": "application/json",
        "access_token": settings.ASAAS_TOKEN_API
    }

    response = requests.delete(url, headers=headers)

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
        # "paylink",
        # "asaasId",
        "created_at",
        "created_by",  
        "badge_status" 
    )

    list_display = (
        "title",
        "value",
        "billingType",
        "customer_name",
        "criado_por", 
        "badge_status" 
    )

    verbose_name = "Link de pagamento"
    verbose_name_plural = "Links de pagamentos"

    fieldsets_base = (
        (_('Informações principais'), {
            'fields': (
                'title',
                'value',
                'billingType',
                'installmentCount',
                'customer',
            )
        }),
        (_('Vencimento e parcelas'), {
            'fields': (
                'dueDate',
                'daysAfterDueDateToRegistrationCancellation',
            )
        }),
        (_('Juros'), {
            'fields': (
                'interest_enabled',
                'interest_value',
                'interest_start_after_days',
            )
        }),
        
        (_('Desconto'), {
            'fields': (
                'discount_dueDateLimitDays',
                'discount_type',
                'discount_value',
            )
        }),
        (_('Multa'), {
            'fields': (
                'fine_enabled',
                'fine_type',
                'fine_value',
            )
        }),
        (_('Callback'), {
            'fields': (
                'successUrl',
                'autoRedirect',
            )
        }),
        (_('Auditoria'), {
            'fields': (
                'created_at',
                'created_by',
                'badge_status',
            ),
        }),
        (_('Descrição'), {
            'fields': (
                'description',
            )
        }),
    )
    
    def badge_status(self, obj):
        status_key = obj.status or "Criada"
        human = friendly_status.get(status_key, status_key.replace("_", " ").title())
        html = f'<span class="badge status-{status_key}">{human}</span>'
        return mark_safe(html)
    
    badge_status.allow_tags = True
    badge_status.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
            if request.user.groups.filter(name='Vendedores').exists() and obj:
                print("obj: ", obj)
                billing_split = BillingSplit(
                    subaccount=request.user,
                    billing=obj,
                    fixedValue=request.user.fixedValue,
                    percentualValue=request.user.percentualValue,
                )
                billing_split.save()
            super().save_model(request, obj, form, change)
        else:
            if obj.paylink:
                messages.warning(request, "Você não pode salvar este modelo pois ele já possui um link de pagamento.")
            else:
                print("request.user.pk> ", request.user.pk)
                super().save_model(request, obj, form, change)


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
        if obj is None: 
            fieldsets = [
                fs for fs in fieldsets
                if fs[0] != _('Auditoria') and fs[0] != _('Informações do Asaas')
            ]

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
    criado_por.short_description = "Criada por"

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


