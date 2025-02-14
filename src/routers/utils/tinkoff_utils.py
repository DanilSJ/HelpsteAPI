import requests
import json
import hashlib
import re
from src.database.requests import create_user_payment

TERMINAL_KEY = "TinkoffBankTest"
PASSWORD = "TinkoffBankTest"

async def generate_token(terminal_key, password, params, description, orderid, amount):
    data = [
        {"TerminalKey": terminal_key},
        {"Amount": str(amount)},
        {"OrderId": str(orderid)},
        {"Description": description},
        {"Password": password}
    ]

    sorted_data = sorted(data, key=lambda x: list(x.keys())[0])

    concatenated_values = ''.join([list(item.values())[0] for item in sorted_data])

    token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()

    return token

async def make_payment(amount, order_id, description, user_id):
    url = "https://securepay.tinkoff.ru/v2/Init"

    payload = {
        "TerminalKey": TERMINAL_KEY,
        "Amount": amount,
        "OrderId": order_id,
        "Description": description,
    }

    payload["Token"] = await generate_token(
        terminal_key=TERMINAL_KEY,
        password=PASSWORD,
        amount=amount,
        orderid=order_id,
        description=description,
        params=payload
    )

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        if response.status_code == 200:
            pattern = r"Подписка\s([^\s,]+).*время:\s([^\s]+)"
            match = re.search(pattern, description)

            if match:
                await create_user_payment(user_id, response.json()['PaymentId'], match.group(1), match.group(2),
                                             response.json()['Amount'])
                return response.json()

        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


async def check_payment_status(payment_id):
    url = "https://securepay.tinkoff.ru/v2/GetState"

    payload = {
        "TerminalKey": TERMINAL_KEY,
        "PaymentId": payment_id
    }

    # Генерация токена для проверки
    token_string = f"{TERMINAL_KEY}{payment_id}{PASSWORD}"

    payload["Token"] = hashlib.sha256(token_string.encode('utf-8')).hexdigest()

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
