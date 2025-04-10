import requests
from dotenv import load_dotenv
import os


url = "https://api-sandbox.asaas.com/v3/accounts"

payload = {
    "loginEmail": "somdaterra3@gmail.com",
    "companyType": "MEI",
    "name": "Thayna Soares",
    "email": "somdaterra3@gmail.com",
    "phone": "21966832617",
    "address": "RUA RIO GRANDE DO SUL",
    "province": "RJ",
    "postalCode": "24859124",
    "cpfCnpj": "57544816000101",
    "birthDate": "2000-05-22",
    "mobilePhone": "21966832617",
    "site": "somdaterra.store",
    "incomeValue": 20000
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "access_token": os.getenv('ASAAS_API')  # Insira a chave da API aqui
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
