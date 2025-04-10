import requests
from dotenv import load_dotenv
import os


url = "https://api-sandbox.asaas.com/v3/finance/split/statistics"

headers = {
    "accept": "application/json",
    "access_token": os.getenv('ASAAS_API')
}

response = requests.get(url, headers=headers)

print(response.text)