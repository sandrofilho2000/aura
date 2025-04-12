from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import User, CommissionType
from django.db import transaction
from datetime import timedelta
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

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
        verbose_name="Criado por",
        related_name='created_billings'
    )
    created_at = models.DateTimeField(verbose_name="Criado em",auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dueDate = models.DateField("Data de vencimento", default=get_due_date)
    paylink = models.URLField("Link de pagamento", null=True, editable=False)
    asaasId = models.CharField("ID Asaas", null=True, editable=False)
    installmentCount = models.IntegerField("Número de parcelas", validators=[MinValueValidator(0), MaxValueValidator(12)], help_text=_("Somente no caso de cobrança parcelada."), null=True)
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

    class Meta:
        verbose_name = 'Cobrança'

    
    def __str__(self):
        return self.title
    

class BillingSplit(models.Model):
    subaccount = models.ForeignKey(
        User,
        related_name='subaccount',
        verbose_name="Subconta",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    billing = models.ForeignKey( 
        Billing,
        related_name='splits',  # <- Aqui está corrigido
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
        verbose_name = "Subconta"
        verbose_name_plural = "Subcontas"
        ordering = ['subaccount__first_name']

    def __str__(self):
        return self.subaccount.first_name if self.subaccount else "-"