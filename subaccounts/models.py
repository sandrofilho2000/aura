from django.db import models

class SubAccount(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome')
    
    class Meta:
        verbose_name = "Subconta"

    def __str__(self):
        return self.name
