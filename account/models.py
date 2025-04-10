from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
import re
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import requests
from django.conf import settings
from decimal import Decimal
import uuid 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group

def validate_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove qualquer caractere não numérico

    # Verificar se o CPF tem 11 caracteres
    if len(cpf) != 11:
        return False

    # Não permitir CPFs com números repetidos, como "111.111.111-11"
    if cpf == cpf[0] * 11:
        return False

    # Calcular e validate os dois últimos dígitos do CPF
    def calcular_digitos(cpf, pesos):
        soma = sum(int(digit) * peso for digit, peso in zip(cpf, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos para o primeiro e segundo dígitos de verificação
    pesos_primeiro_digito = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo_digito = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    primeiro_digito = calcular_digitos(cpf[:9], pesos_primeiro_digito)
    segundo_digito = calcular_digitos(cpf[:10], pesos_segundo_digito)

    return cpf[-2:] == f'{primeiro_digito}{segundo_digito}'

def validate_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)  

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digitos(cnpj, pesos):
        soma = sum(int(digit) * peso for digit, peso in zip(cnpj, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos_primeiro_digito = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo_digito = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    primeiro_digito = calcular_digitos(cnpj[:12], pesos_primeiro_digito)
    segundo_digito = calcular_digitos(cnpj[:13], pesos_segundo_digito)

    return cnpj[-2:] == f'{primeiro_digito}{segundo_digito}'

def validate_cpf_cnpj(value):
    value = re.sub(r'\D', '', value) 

    if len(value) == 11:  # CPF
        if not validate_cpf(value):
            raise ValidationError(_('O CPF fornecido é inválido.'))
    elif len(value) == 14:  # CNPJ
        if not validate_cnpj(value):
            raise ValidationError(_('O CNPJ fornecido é inválido.'))
    else:
        raise ValidationError(_('O valor fornecido deve ser um CPF ou CNPJ válido.'))

def validate_celular(celular):
    celular_formatado = re.sub(r'\D', '', celular)  # Remove caracteres não numéricos

    # Verifica se o número de celular tem 11 ou 10 dígitos
    if len(celular_formatado) not in [10, 11]:
        raise ValidationError(_('O número de celular deve ter 10 ou 11 dígitos.'))

    # Verifica se o número começa com "9" para números de celular
    if len(celular_formatado) == 11 and celular_formatado[2] != '9':
        raise ValidationError(_('O número de celular deve começar com 9 após o DDD.'))

    # Verifica se o número contém apenas dígitos
    if not celular_formatado.isdigit():
        raise ValidationError(_('O número de celular contém caracteres inválidos.'))

    return True

class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

def criar_conta_api(payload):
    url = "https://api-sandbox.asaas.com/v3/accounts"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": settings.ASAAS_ACCESS_TOKEN  
    }

    try:
        print("payload: ", payload)
        payload['birthDate'] = payload['birthDate'].isoformat()
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code - 200 <= 10:
            return {
                        'status': response.status_code,
                        'description': "Subconta criada com sucesso!",
                        'walletId': response.json()['walletId']
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


class CompanyType(models.TextChoices):
    MEI = "MEI", _("MEI")
    LIMITED = "LIMITED", _("Limited")
    INDIVIDUAL = "INDIVIDUAL", _("Individual")
    ASSOCIATION = "ASSOCIATION", _("Association")


class CommissionType(models.TextChoices):
    Fixo = "FIXED", _("Fixo")
    Porcento = "PERCENTAGE", _("Porcento")


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError(_('O email precisa ser definido.'))
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not email:
            raise ValueError("Superuser must have an email address.")

        if not username:
            username = email.split("@")[0]

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField( 
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False) 
    username = models.CharField(
        _('username'),
        max_length=100,
        unique=True,
        help_text=_('Obrigatório. 100 caractéres ou menos. Letras, números e @/./+/-/_ caractéres'),
        validators=[
            validators.RegexValidator(
                re.compile(r'^[\w.@+-]+$'),
                _('Enter a valid username.'),
                _('invalid')
            )
        ]
    )

    first_name = models.CharField(_('Primeiro Nome'), max_length=30)
    walletId = models.CharField(_('Wallet ID'), max_length=255, blank=True, help_text=_('Vazio para nova subconta.'))
    last_name = models.CharField(_('Sobrenome'), max_length=30)
    email = models.EmailField(_('Email'), max_length=255, unique=True)
    login_email = models.EmailField(_('Email de Login'), max_length=255, blank=True, null=True, help_text=_('Email de login para a conta Asaas.'))
    cpf_cnpj = models.CharField(
            _('CPF/CNPJ'),
            max_length=18,
            unique=True,
            validators=[validate_cpf_cnpj] 
        )    
    birth_date = models.DateField(_('Data de Nascimento'), blank=True, null=True)
    
    company_type = models.CharField(
        _('Tipo da Empresa'),
        max_length=20,
        choices=CompanyType.choices,
        blank=True,
        null=True
    )
    
    phone = models.CharField(_('Telefone Fixo'), max_length=20, blank=True, null=True)
    mobile_phone = models.CharField(
        _('Telefone Celular'),
        max_length=20,
        blank=True,
        validators=[validate_celular]  
    )    
    site = models.URLField(_('Site'), max_length=255, blank=True, null=True)
    income_value = models.DecimalField(_('Faturamento/Renda Mensal'), max_digits=10, decimal_places=2, null=True)
    address = models.CharField(_('Endereço'), max_length=255, null=True)
    address_number = models.CharField(_('Número'), max_length=10, null=True)
    complement = models.CharField(_('Complemento'), max_length=255, blank=True, null=True)
    province = models.CharField(_('Bairro'), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    
    is_staff = models.BooleanField(_('Membro da equipe'), default=False)
    is_active = models.BooleanField(_('Ativo'), default=True)
    date_joined = models.DateTimeField(_('Data de criação'), default=timezone.now)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('Perfis'),
        blank=True,
        related_name='custom_user_set'  
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('Permissões do usuário'),
        blank=True,
        related_name="user_permissions",
        help_text=_('Permissões específicas para este usuário.'),
    )

    pages_allowed = models.ManyToManyField(
        'pages.page',
        verbose_name=_('Páginas autorizadas'),
        blank=True,
        related_name="user_pages_allowed", 
    )

    subpages_allowed = models.ManyToManyField(
        'pages.subpage',
        verbose_name=_('Subpáginas autorizadas'),
        blank=True,
        related_name="user_subpages_allowed", 
    )
    fixedValue = models.DecimalField(
        _('Comissão fixa (R$)'),
        max_digits=12,
        null=True,
        blank=True,
        decimal_places=2,
        help_text=_('Valor da comissão fixa padrão do usuário.')
    )
    percentualValue = models.DecimalField(
        _('Comissão percentual'),
        max_digits=5, 
        decimal_places=2,
        default=10.00,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Valor da comissão percentual padrão do usuário.')
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'cpf_cnpj', 'birth_date', 'mobile_phone', 'income_value', 'address', 'address_number', 'province', 'postal_code']

    objects = UserManager()

    class Meta:
        verbose_name = _('Subconta')
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email
    
    def save(self, *args, **kwargs):
        payload = {
            "companyType": self.company_type,
            "birthDate": self.birth_date,
            "cpfCnpj": self.cpf_cnpj,  
            "email": self.email,
            "name": f"{self.first_name} {self.last_name}",
            "loginEmail": self.email,
            "phone": self.phone,
            "address": self.address,
            "province": self.province,
            "postalCode": self.postal_code,
            "mobilePhone": self.mobile_phone,
            "incomeValue": float(self.income_value) if isinstance(self.income_value, Decimal) else self.income_value,
            "site": self.site,
            "addressNumber": self.address_number,
            "complement": self.complement,
        }

        account = User.objects.filter(pk=self.pk).first()      

        if account:
            if not account.walletId and not self.walletId:
                response_data = criar_conta_api(payload)

                if response_data['status'] == 400:
                    raise ValidationError(f"Erro ao criar subconta Asaas: {response_data['description']}")
                
                if response_data['walletId']:
                    self.walletId = response_data['walletId']
        
        super().save(*args, **kwargs)
       

        