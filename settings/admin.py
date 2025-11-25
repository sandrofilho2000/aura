from django.contrib import admin
from settings.models import Settings

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        # Permite adicionar apenas se ainda não existe nenhum registro
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Ninguém pode excluir
        return False