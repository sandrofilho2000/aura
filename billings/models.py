from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import User, CommissionType
from django.db import transaction
from datetime import timedelta
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import requests


def get_due_date():
    return now().date() + timedelta(days=7)


class PaymentMethod(models.TextChoices):
    CREDIT_CARD = "CREDIT_CARD", _("Crédito")
    BOLETO = "BOLETO", _("Boleto")
    PIX = "PIX", _("PIX")


class Billing(models.Model):
    title = models.CharField(verbose_name="Título", max_length=255)
    billingType = models.CharField(
        _('Forma de pagamento'),
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        verbose_name="Criada por",
        related_name='created_billings'
    )
    created_at = models.DateTimeField(verbose_name="Criado em",auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dueDate = models.DateField("Data de vencimento", default=get_due_date,  help_text=(
        "Data de vencimento da cobrança. "
        "No caso de cobrança parcelada, esta data será usada apenas como vencimento "
        "da primeira parcela. As demais parcelas terão sua data calculada "
        "automaticamente pelo Asaas, mês a mês."
    ))
    daysAfterDueDateToRegistrationCancellation = models.PositiveIntegerField(
        verbose_name="Dias para cancelamento do registro",
        null=True,
        blank=True,
        help_text=(
            "Dias após o vencimento para cancelamento automático do registro "
            "(somente para boletos bancários)."
        )
    )
    paylink = models.URLField("Link de pagamento", null=True, editable=False)
    asaasId = models.CharField("ID Asaas", null=True, editable=False, max_length=255)
    installmentCount = models.IntegerField(
        "Número de parcelas",
        choices=[(i, str(i)) for i in range(1, 13)],
        null=True,
        blank=True,
        help_text="Somente no caso de cobrança parcelada."
        )
    value = models.DecimalField(
        _("Valor da cobrança"),  
        max_digits=12,  
        decimal_places=2,  
        blank=False,  
        null=False,  
        help_text=_("Informe o valor total da cobrança em reais (R$). Exemplo: 99.90")
    )
    successUrl = models.URLField("URL", 
        help_text="URL para a qual o cliente será redirecionado após o pagamento bem-sucedido da fatura ou link de pagamento.", null=True, blank=True
    )
    autoRedirect = models.BooleanField(
        "Auto redirecionamento",
        default=False,
        help_text="Define se o redirecionamento será automático após o pagamento. Se falso, o cliente verá um botão para retornar manualmente."
    )
    customer = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='pay_links',
        verbose_name="Cliente"
    )
    status = models.CharField(
        "Status",
        max_length=50,
        default="Criada",
        editable=False
    )

    discount_value = models.DecimalField(
        "Valor do desconto",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor percentual ou fixo do desconto."
    )

    discount_dueDateLimitDays = models.IntegerField(
        "Dias limite para aplicar desconto",
        null=True,
        blank=True,
        help_text="Dias antes do vencimento para aplicar o desconto (0 = até o vencimento)."
    )

    discount_type = models.CharField(
        "Tipo de desconto",
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ("PERCENTAGE", "Percentual"),
            ("FIXED", "Fixo")
        ]
    )
    
    interest_enabled = models.BooleanField(
        verbose_name="Habilitar juros",
        default=False,
        help_text="Ativa a cobrança de juros após o vencimento."
    )

    interest_value = models.DecimalField(
        verbose_name="Valor do juros (%)",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    interest_start_after_days = models.PositiveIntegerField(
        verbose_name="Início da cobrança (dias)",
        blank=True,
        null=True,
        help_text="Quantidade de dias após o vencimento para começar a cobrar os juros."
    )
    
    fine_enabled = models.BooleanField(
        verbose_name="Habilitar multa",
        default=False,
        help_text="Ativa a cobrança de multa para pagamentos após o vencimento."
    )

    fine_type = models.CharField(
        verbose_name="Tipo de multa",
        max_length=20,
        choices=(
            ('PERCENTAGE', 'Percentual (%)'),
            ('FIXED', 'Valor Fixo (R$)')
        ),
        blank=True,
        null=True,
        help_text="Define se a multa será percentual ou um valor fixo."
    )

    fine_value = models.DecimalField(
        verbose_name="Valor da multa",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Valor da multa (em % ou em R$, conforme o tipo selecionado)."
    )
    description = models.CharField(
        verbose_name="Descrição",
        max_length=500,
        null=True,
        blank=True,
        help_text="Descrição da cobrança (máx. 500 caracteres)."
    )
    
    class Meta:
        verbose_name = 'Cobrança'

    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class BillingSplit(models.Model):
    subaccount = models.ForeignKey(
        User,
        related_name='subaccount',
        verbose_name="Afiliado",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    billing = models.ForeignKey( 
        Billing,
        related_name='splits', 
        on_delete=models.CASCADE,
        verbose_name=_("Link de pagamento")
    )
    fixedValue = models.DecimalField(
        _('Comissão fixa (R$)'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
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

    class Meta:
        verbose_name = "Afiliado"
        verbose_name_plural = "Afiliados"
        ordering = ['subaccount__first_name']

    def __str__(self):
        return self.subaccount.first_name if self.subaccount else "-"
 
     