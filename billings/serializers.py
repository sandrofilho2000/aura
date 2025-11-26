from rest_framework import serializers
from .models import Billing, BillingSplit
from account.models import User
from clients.models import Client  


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name'] 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class BillingSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='customer', write_only=True
    )
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Billing
        fields = "__all__"

    
    def get_customer(self, obj):
        return obj.customer.asaasId if obj.customer else None
