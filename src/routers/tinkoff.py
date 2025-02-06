from fastapi import APIRouter, HTTPException, Depends

import re
from datetime import datetime

import requests
import json
import hashlib
from src.database.requests import create_user_payment
from pydantic import BaseModel
from .users import get_current_user

router = APIRouter()

class TinkoffAddModel(BaseModel):
    id: int
    amount: int
    subscription_type: str
    subscription_time: str

async def generate_token(terminal_key, password, params, description, orderid, amount):
    filtered_params = {k: v for k, v in params.items() if v is not None and k != "Token"}
    sorted_params = sorted(filtered_params.items())

    token_string = (
            "" + str(amount) + str(description) + str(orderid) + password + terminal_key
    )

    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()


async def make_payment(amount, order_id, description, user_id):
    url = "https://securepay.tinkoff.ru/v2/Init"

    TERMINAL_KEY = "TinkoffBankTest"
    PASSWORD = "TinkoffBankTest"

    payload = {
        "TerminalKey": TERMINAL_KEY,
        "Amount": amount,
        "OrderId": order_id,
        "Description": description,
        "CustomerKey": "string",
        "Recurrent": "Y",
        "Language": "ru",
        "NotificationURL": "http://example.com",
        "SuccessURL": "http://example.com",
        "FailURL": "http://example.com",
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

    TERMINAL_KEY = "TinkoffBankTest"
    PASSWORD = "TinkoffBankTest"

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


@router.post("/")
async def add_tinkoff(request: TinkoffAddModel, current_user: dict = Depends(get_current_user)):
    order_id = str(datetime.now().timestamp()).replace('.', '')
    description = f"Подписка {request.subscription_type}, время: {request.subscription_time}"
    payment = await make_payment(request.amount, order_id, description, user_id=request.id)

    if not payment:
        raise HTTPException(status_code=404, detail="Error")
    return {"message": payment}

@router.get("/{payment_id}/")
async def check_tinkoff_status_payment(payment_id: int, current_user: dict = Depends(get_current_user)):
    payment = await check_payment_status(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Error")
    return {"message": payment}
