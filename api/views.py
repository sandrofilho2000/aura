from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import User  
from billings.models import BillingSplit, Billing
from billings.serializers import BillingSplitSerializer, BillingSerializer
import json
from django.db import IntegrityError
from random import randint
from django.shortcuts import get_object_or_404
import requests
from django.conf import settings


@login_required
def check_auth(request):
    return JsonResponse({"authenticated": True})


class SearchItemsView(View):
    def get(self, request, *args, **kwargs):
        query_params = request.GET
        filtered_items = []
        valid_fields = []
        model = None
        serializer = None
        prefetch_related_fields = []
        select_related_fields = []

        field = query_params.get('field')
        operation = query_params.get('operation')
        value = query_params.get('value')

        if not request.user.has_perm(f"{query_params['app']}s.view_{query_params['app']}"):
            return JsonResponse({"message": "Você não possui privilégios para isso!", "status": 401})

        if query_params['app'] == "subaccount":
            model = User
            valid_fields = ['first_name', 'last_name', 'username', 'email', 'id', 'walletId', 'fixedValue', 'percentualValue']

        elif query_params['app'] == "billing":
            splits = Billing.objects.select_related('customer').filter(**{field: value})
            serializer = BillingSerializer(splits, many=True)
            return JsonResponse({"results": serializer.data, "status": 200}, safe=False)
              
        elif query_params['app'] == "billingsplit":
            splits = BillingSplit.objects.select_related('subaccount').filter(**{field: value})
            serializer = BillingSplitSerializer(splits, many=True)
            return JsonResponse({"results": serializer.data, "status": 200}, safe=False)

        
        else:
            return JsonResponse({"message": "App inválido", "status": 400})


        
        if valid_fields and field not in valid_fields:
            return JsonResponse({"message": "Campo inválido", "status": 400})

        filter_kwargs = {}
        if field and operation == 'contains':
            filter_kwargs = {f"{field}__icontains": value}
        elif field and operation == 'equals':
            
            filter_kwargs = {f"{field}": value}

        queryset = model.objects.all()
            
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)
        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)
        

        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)

        filtered_items = list(queryset.values(*valid_fields))

        return JsonResponse({"results": filtered_items, "status": 200})


class CreateBillingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data  

            billing_id = data.get("id")
            billing = Billing.objects.get(id=billing_id)

            url = "https://api-sandbox.asaas.com/v3/payments"

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "access_token": settings.ASAAS_ACCESS_TOKEN  
            }

            
            if(data.get("installmentCount") and data.get("billingType") == "CREDIT_CARD"):
                value = float(data.get("value"))
                installmentCount = float(data.get("installmentCount"))
                installmentValue = value / installmentCount
                data['installmentValue'] = installmentValue
            else:
                data.pop("installmentCount")

            if(data.get("successUrl")):
                callback = {
                    "autoRedirect": data.get("autoRedirect"),
                    "successUrl": data.get("successUrl")
                }
                data['callback'] = callback
                
            data['externalReference'] = str(data.get('id'))
            data.pop('paylink', None)
            data.pop('id', None)
            
            if request.user.groups.filter(name='Vendedores').exists():
                split = {}
                walletId = request.user.walletId
                if walletId:
                    percentualValue = float(request.user.percentualValue or 0)
                    fixedValue = float(request.user.fixedValue or 0)
                    split["walletId"] = walletId
                    split["fixedValue"] = fixedValue
                    split["percentualValue"] = percentualValue
                    data['split'] = [split]

            for item in data.get("split", []):
                item['externalReference'] = str(item.get("id"))
                item.pop("id", None)
                item.pop("subaccount", None)
                
            print("data: ", data)
            response = requests.post(url, json=data, headers=headers)

            if response.status_code - 200 <= 10:
                try:
                    res_json = response.json()
                except Exception as e:
                    return Response({
                        'error': 'Erro ao interpretar resposta da API Asaas',
                        'detalhe': str(e)
                    }, status=500)

                paylink = res_json.get('invoiceUrl')
                asaasId = res_json.get('id')

                billing.paylink = paylink
                billing.asaasId = asaasId
                billing.save()

                return Response({
                    'status': response.status_code,
                    'description': "Cobrança criada com sucesso!",
                    'paylink': paylink,
                    'asaasId': asaasId,
                })

            else:
                try:
                    response_text = response.json()
                    errors = response_text.get('errors', [])
                    print("🚀 ~ errors:", errors)
                    return Response({
                        'status': response.status_code,
                        'errors': errors
                    })
                
                except Exception:
                    return Response({
                        'status': response.status_code,
                        'description': 'Erro desconhecido ao criar cobrança',
                        'resposta': response.text
                    }, status=response.status_code)

        except Billing.DoesNotExist:
            return Response({"error": "Cobrança não encontrada."}, status=404)

        except IntegrityError:
            return Response({"error": "Erro de integridade, verifique os dados."}, status=400)

        except Exception as e:
            print("e:", e)
            return Response({"error": str(e)}, status=500)


class GetJWTTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token)})

