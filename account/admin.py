from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'username', 'walletId', 'cpf_cnpj', 'birth_date', 'company_type', 'income_value')}),
        (_('Contato'), {'fields': ('phone', 'mobile_phone', 'site')}),
        (_('Endereço'), {'fields': ('address', 'address_number', 'complement', 'province', 'postal_code')}),
        (_('Comissão'), {'fields': ('fixedValue', 'percentualValue')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas Importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions', 'groups')

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'get_groups')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'cpfCnpj')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('email', 'username', 'date_joined')

    def get_groups(self, obj):
        return ", ".join([profile.name for profile in obj.groups.all()])
    
    get_groups.short_description = _('Perfis')

    def save_model(self, request, obj, form, change):
        try:        
            account = User.objects.filter(pk=obj.pk).first()
            super().save_model(request, obj, form, change)

            if account and not account.walletId:
                messages.success(request, "Subconta criada na Asaas!")

        except (ValidationError, IntegrityError) as e:
            message_error = "; ".join(e.messages) if isinstance(e, ValidationError) else str(e)
            messages.error(request, message_error)

    def has_change_permission(self, request, obj=None):
        # Superusers podem tudo
        if request.user.is_superuser:
            return True
        
        # Se estiver tentando editar outra conta, bloqueia
        if obj is not None and obj != request.user:
            return False
        
        # Pode editar a própria conta
        return super().has_change_permission(request, obj)
    

    def get_readonly_fields(self, request, obj=None):
        # Superusuários podem editar tudo
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        
        # Usuários comuns não podem editar esses campos
        campos_restritos = ['fixedValue', 'percentualValue', 'walletId', 'last_login', 'date_joined' ,'is_active', 'is_staff', 'is_superuser']
        
        # Mantém os campos já readonly por padrão + os campos restritos
        return list(set(super().get_readonly_fields(request, obj)) | set(campos_restritos))
        
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        # Se não for superusuário, remove o fieldset "Permissões"
        if not request.user.is_superuser:
            fieldsets = [fs for fs in fieldsets if fs[0] != _('Permissões')]

        return fieldsets
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Superusers veem tudo
        if request.user.is_superuser:
            return qs

        # Usuários comuns veem apenas a própria conta
        return qs.filter(pk=request.user.pk)