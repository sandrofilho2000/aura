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

