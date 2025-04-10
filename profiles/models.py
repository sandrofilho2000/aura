from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission

def validate_group_name(value):
    if not value.strip():
        raise ValidationError(_('O nome do grupo não pode estar vazio.'))

class ProfileManager(models.Manager):
    def create_group(self, name, description=""):
        if not name:
            raise ValueError(_('O nome do grupo é obrigatório.'))
        group = self.model(name=name, description=description)
        group.save(using=self._db)
        return group


class Profile(models.Model):
    name = models.CharField(_('Nome do Grupo'), max_length=150, unique=True)
    description = models.TextField(_('Descrição'), blank=True, default="")
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Permissões do perfil'),
        blank=True,
        related_name="profile_permissions"
    )
    pages_allowed = models.ManyToManyField(
        'pages.page',
        verbose_name=_('Páginas autorizadas'),
        blank=True,
        related_name="group_pages_allowed", 
    )

    subpages_allowed = models.ManyToManyField(
        'pages.subpage',
        verbose_name=_('Subpáginas autorizadas'),
        blank=True,
        related_name="group_subpages_allowed", 
    )

    class Meta:
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')

    def __str__(self):
        return self.name
    






