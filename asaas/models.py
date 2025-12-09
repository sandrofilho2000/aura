from django.db import models
import requests


class AfiliadoAsaas(models.Model):
    STATUS_CHOICES = [
        ("nao_configurado", "Não configurado"),
        ("aguardando_teste", "Aguardando teste"),
        ("conectado", "Conectado"),
        ("token_invalido", "Token inválido"),
        ("erro_de_conexao", "Erro de conexão"),
        ("api_indisponivel", "API indisponível"),
        ("erro_desconhecido", "Erro desconhecido"),
    ]

    afiliado = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="asaas_config"
    )
    externalId = models.CharField(
        "Identificador da carteira (Wallet ID)", null=True, max_length=255
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="não_configurado",
        editable=False,
    )

    class Meta:
        unique_together = ("afiliado",)
        verbose_name = "Configuração Asaas do Afiliado"
        verbose_name_plural = "Configuração Asaas dos Afiliados"
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # evita requisições duplicadas
        self._status_checked = False
        self.check_status()
        
    def check_status(self):
        """ if self.externalId:
            return """

        self._status_checked = True

        asaas_config = AsaasConfig.objects.filter(status="conectado").first()
        if not asaas_config.token_api:
            return 
        
        if not self.externalId:
            self.status = "não_configurado"
            return

        url = f"https://api-sandbox.asaas.com/v3/accounts/{self.externalId}"

        try:
            response = requests.get(
                url,
                headers={
                    "accept": "application/json",
                    "access_token": asaas_config.token_api,
                },
                timeout=5,
            )

            if response.status_code == 200:
                self.status = "conectado"
            elif response.status_code == 401:
                self.status = "token_invalido"
            elif response.status_code == 503:
                self.status = "api_indisponivel"
            else:
                self.status = "erro_de_conexao"

        except requests.exceptions.RequestException:
            self.status = "erro_de_conexao"

        # grava o novo status caso tenha mudado
        super().save(update_fields=["status"])



    def __str__(self):
        if self.afiliado.first_name:
            return f"{self.afiliado.first_name} {self.afiliado.last_name}"
        return self.afiliado.email





class AsaasConfig(models.Model):
    STATUS_CHOICES = [
        ("nao_configurado", "Não configurado"),
        ("aguardando_teste", "Aguardando teste"),
        ("conectado", "Conectado"),
        ("token_invalido", "Token inválido"),
        ("erro_de_conexao", "Erro de conexão"),
        ("api_indisponivel", "API indisponível"),
        ("erro_desconhecido", "Erro desconhecido"),
    ]

    token_api = models.CharField("Token API", max_length=255, blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="não_configurado",
        editable=False,
    )

    integration = models.OneToOneField(
        "integrations.Integration",
        on_delete=models.CASCADE,
        related_name="asaas_config",
    )

    # --- executa sempre que o objeto é carregado ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # evita requisições duplicadas
        self._status_checked = False
        self.check_status()

    # --- testa o token na API ---
    def check_status(self):
        if self._status_checked:
            return  # evita loop

        self._status_checked = True

        if not self.token_api:
            self.status = "não_configurado"
            return

        url = "https://api-sandbox.asaas.com/v3/customers?limit=1"

        try:
            response = requests.get(
                url,
                headers={
                    "accept": "application/json",
                    "access_token": self.token_api,
                },
                timeout=5,
            )

            if response.status_code == 200:
                self.status = "conectado"
            elif response.status_code == 401:
                self.status = "token_invalido"
            elif response.status_code == 503:
                self.status = "api_indisponivel"
            else:
                self.status = "erro_de_conexao"

        except requests.exceptions.RequestException:
            self.status = "erro_de_conexao"

        # grava o novo status caso tenha mudado
        super().save(update_fields=["status"])

    def save(self, *args, **kwargs):
        # ainda mantemos a regra de só existir 1
        if not self.pk and AsaasConfig.objects.exists():
            raise Exception("Só pode existir uma configuração Asaas.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuração Asaas"
