from django.db import models

class Settings(models.Model):
    site_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    theme_color = models.CharField(max_length=20)

    def __str__(self):
        return "Configurações do Sistema"

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
        
    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)