import requests
from dotenv import load_dotenv
import os


url = "https://www.asaas.com/api/v3/paymentLinks/0d9cbf25-f531-4166-8c10-58546bd6f0de"

headers = {
    "accept": "application/json",
    "access_token": os.getenv('ASAAS_API')
}

response = requests.delete(url, headers=headers)

print(response.text)