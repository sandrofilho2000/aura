from django.contrib import admin
from .models import Client
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import admin, messages
from .models import Client
import requests


def check_if_client_exist(asaasId):
    url = f"https://www.asaas.com/api/v3/customers/{asaasId}/restore"
    print("🚀 ~ asaasId:", asaasId)

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjFiMWE5OTM4LTI0YjUtNGE1YS1iMzZmLWVjOGRlZGVmMWUwMjo6JGFhY2hfNTU0NGI4NDQtMTczZC00NWUzLTliY2UtNmZhYzQ4MjA5N2M0"
    }

    response = requests.post(url, headers=headers)
    if int(response.status_code) - 200 < 100:
        return True
    else:
        return False

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'cpf_cnpj', 'asaasId')}),
        ('Contato', {'fields': ('phone', 'email')}),
        ('Endereço', {'fields': ('address', 'address_number', 'complement', 'province', 'postal_code')}),
        ('Outros', {'fields': ('additional_emails', 'observations', 'company', 'foreign_customer')}),
    )
    readonly_fields=("asaasId",)
    list_display = ('name', 'cpf_cnpj','asaasId', 'email', 'phone', 'company', 'foreign_customer')
    search_fields = ('name', 'cpf_cnpj', 'email', 'company')
    list_filter = ('foreign_customer',)
    ordering = ('name', 'cpf_cnpj')

    def get_form(self, request, obj=None, **kwargs):
        if obj: 
            client_exist = check_if_client_exist(obj.asaasId)
            if not client_exist:
                messages.warning(request, f"Parece que este cliente foi deletado em sua plataforma Asaas. Verifique no painel do seu banco em Meus Clientes > Clientes e procure por {obj.name}!")
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        try:        
            client = Client.objects.filter(pk=obj.pk).first()
            super().save_model(request, obj, form, change)

            if not client:
                messages.success(request, "Cliente criado na Asaas!")

            if client:
                messages.success(request, "Cliente atualizado na Asaas!")

        except (ValidationError, IntegrityError) as e:
            message_error = "; ".join(e.messages) if isinstance(e, ValidationError) else str(e)
            messages.error(request, message_error)

    def delete_model(self, request, obj):
        if 1==1:
            messages.success(request, "Cliente deletado na Asaas!")
        return super().delete_model(request, obj)