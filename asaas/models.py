from django.db import models
from django.conf import settings


class AfiliadoAsaas(models.Model):
    afiliado = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="asaas_config"
    )
    externalId = models.CharField("Identificador da carteira (Wallet ID)", null=True, max_length=255)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("afiliado",)
        verbose_name = "Configuração Asaas do Afiliado"
        verbose_name_plural = "Configuração Asaas dos Afiliados"

    def __str__(self):
        return f"{self.afiliado.nome} - {self.ambiente}"
