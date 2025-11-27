from django.db import models

class Integration(models.Model):
    name = models.CharField(max_length=50, default="Configurações do Sistema")

    def save(self, *args, **kwargs):
        if not self.pk and Integration.objects.exists():
            raise Exception("Só pode existir um registro de Integration.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Integrações do Sistema"