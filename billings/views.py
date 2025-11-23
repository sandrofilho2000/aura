from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from billings.models import Billing
import json

@csrf_exempt
def asaas_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    print("Webhook Asaas recebido:", payload)

    try:
        payment_data = payload.get("payment", {})
        payment_id = payment_data.get("id")  
        event = payload.get("event")        

        if not payment_id:
            return JsonResponse({"status": "ignorado", "motivo": "sem payment.id"})

        # Extrai apenas a parte que aparece no link
        # pay_84rgzwrgc0wo2k8o → 84rgzwrgc0wo2k8o
        identifier = payment_id.replace("pay_", "")

        # Busca cobrança onde o paylink termina com esse id
        billing = Billing.objects.filter(paylink__endswith=identifier).first()

        if not billing:
            return JsonResponse({"status": "ignorado", "motivo": "billing não encontrado"})

        # Atualiza o status
        billing.status = event
        billing.save(update_fields=["status"])

        return JsonResponse({"status": "ok", "billing": billing.id})

    except Exception as e:
        print("Erro webhook:", e)
        return JsonResponse({"error": str(e)}, status=500)