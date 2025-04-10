from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def criar_cliente_api(payload):
    url = "https://api-sandbox.asaas.com/v3/customers"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": settings.ASAAS_ACCESS_TOKEN  
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code - 200 <= 10:
            return {
                        'status': response.status_code,
                        'description': "Cliente Asaas criado com sucesso!",
                        'asaasId': response.json()['id']
                    }                     
 

        else:
            response_text = response.json() 
            errors = response_text.get('errors', [])  

            if errors:
                for error in errors:
                    return {
                        'status': 400,
                        'description': error.get('description', 'Error')  
                    }                     


    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao conectar com a API: {str(e)}")

def atualizar_cliente_api(payload, asaasId):
    url = f"https://api-sandbox.asaas.com/v3/customers/{asaasId}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": settings.ASAAS_ACCESS_TOKEN  
    }

    try:
        response = requests.put(url, json=payload, headers=headers)

        if response.status_code - 200 <= 10:
            return {
                        'status': response.status_code,
                        'description': "Cliente Asaas atualizado com sucesso!",
                    }                     
 

        else:
            response_text = response.json() 
            errors = response_text.get('errors', [])  

            if errors:
                for error in errors:
                    return {
                        'status': 400,
                        'description': error.get('description', 'Error')  
                    }                     


    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao conectar com a API: {str(e)}")

def delete_cliente_api(asaasId):
    url = f"https://api-sandbox.asaas.com/v3/customers/{asaasId}"
    headers = {"accept": "application/json", 'access_token': settings.ASAAS_ACCESS_TOKEN }
    response = requests.delete(url, headers=headers)
    if response.status_code - 200 <= 10:
        return {
                    'status': response.status_code,
                    'description': "Cliente Asaas deletado com sucesso!",
                    'asaasId': response.json()['id'],
                }                     


    else:
        response_text = response.json() 
        errors = response_text.get('errors', [])  

        if errors:
            for error in errors:
                return {
                    'status': 400,
                    'description': error.get('description', 'Error')  
                }   

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    cpf_cnpj = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    asaasId=models.CharField(max_length=100, unique=True, editable=False, verbose_name="Asaas ID")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")
    address_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complement = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    province = models.CharField(max_length=255, blank=True, null=True, verbose_name="Estado")
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="cep")
    additional_emails = models.TextField(blank=True, null=True, verbose_name="Emails adicionais" ,help_text="Emails separados por vírgula")
    observations = models.TextField(blank=True, null=True, verbose_name="Observações")
    company = models.CharField(max_length=255, blank=True, null=True)
    foreign_customer = models.BooleanField(default=False, verbose_name="Cliente estrangeiro?")

    
    class meta:
        verbose_name = 'Cliente'

    def __str__(self):
        return f"{self.name} ({self.asaasId})"


    def save(self, *args, **kwargs):
        payload = {
            "name": self.name,  
            "cpfCnpj": self.cpf_cnpj,  
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "address_number": self.address_number,
            "complement": self.complement,
            "province": self.province,
            "postalCode": self.postal_code,
            "phone": self.phone,
            "additional_emails": self.additional_emails,
            "observations": self.observations,
            "company": self.company,
            "foreign_customer": self.foreign_customer,
        }

        client = Client.objects.filter(pk=self.pk).first()
        
        if not client:
            response_data = criar_cliente_api(payload)
            if response_data['status'] == 400:
                raise ValidationError(f"Erro ao criar cliente Asaas: {response_data['description']}")
            
            if response_data['asaasId']:
                self.asaasId = response_data['asaasId']

        if client:
            response_data = atualizar_cliente_api(payload, self.asaasId)
            if response_data['status'] == 400:
                raise ValidationError(f"Erro ao atualizar cliente Asaas: {response_data['description']}")
            

        
        super().save(*args, **kwargs)


    def delete(self,  *args, **kwargs):
        response_data = delete_cliente_api(self.asaasId)
        if response_data['status'] == 400:
            raise ValidationError(f"Erro ao criar cliente Asaas: {response_data['description']}")

        return super().delete(*args, **kwargs)
    

    