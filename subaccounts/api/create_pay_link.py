import requests
from dotenv import load_dotenv
import os

load_dotenv()


url = f"{settings.ASAAS_URL_API}/paymentLinks"

payload = {
    "name": "Produto Exemplo",
    "description": "Descrição do produto",
    "value": 5020.00,  
    "billingType": "PIX",  
    "chargeType": "DETACHED",  
    "dueDateLimitDays": 5, 
    "split": [
        {
            "walletId": "def32dec-fa03-4ad5-af40-de9ae8b43888",  
            "fixedValue": None,
            "percentualValue": 80.0 
             
        },
        {
            "walletId": "ce7c35aa-9be9-4ca9-a542-ec3a525a8cd9",  
            "fixedValue": None,
            "percentualValue": 20.0 
        }
    ]
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "access_token": "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjFiMWE5OTM4LTI0YjUtNGE1YS1iMzZmLWVjOGRlZGVmMWUwMjo6JGFhY2hfNTU0NGI4NDQtMTczZC00NWUzLTliY2UtNmZhYzQ4MjA5N2M0"
}

response = requests.post(url, json=payload, headers=headers)
