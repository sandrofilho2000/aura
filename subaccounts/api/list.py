import requests
from dotenv import load_dotenv
import os


url = f"{settings.ASAAS_URL_API}/accounts"

headers = {
    "accept": "application/json",
    "access_token": os.getenv('ASAAS_API')
}

response = requests.get(url, headers=headers)

print(response.text)