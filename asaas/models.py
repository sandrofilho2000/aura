from django.db import models
from django.conf import settings

class AfiliadoAsaas(models.Model):
    afiliado = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="asaas_config"
    )
    externalId = models.CharField(
        "Identificador da carteira (Wallet ID)", null=True, max_length=255
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("afiliado",)
        verbose_name = "Configuração Asaas do Afiliado"
        verbose_name_plural = "Configuração Asaas dos Afiliados"

    def __str__(self):
        if self.afiliado.first_name:
            return f"{self.afiliado.first_name} {self.afiliado.last_name}"
        else:
            return self.afiliado.email


class AsaasConfig(models.Model):
    token_api = models.CharField("Token API", max_length=255, blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    integration = models.OneToOneField(
        "integrations.Integration",
        on_delete=models.CASCADE,
        related_name="asaas_config",
    )

    def save(self, *args, **kwargs):
        if not self.pk and AsaasConfig.objects.exists():
            raise Exception("Só pode existir um registro de AsaasConfig.")
        return super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk and AsaasConfig.objects.exists():
            raise Exception("Só pode existir uma configuração Asaas.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuração Asaas"