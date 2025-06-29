# Документация API для Мерчантов

## Содержание
1. [Авторизация](#авторизация)
2. [Создание транзакций](#создание-транзакций)
3. [Управление транзакциями](#управление-транзакциями)
4. [Диспуты](#диспуты)
5. [Справочная информация](#справочная-информация)
6. [Настройки мерчанта](#настройки-мерчанта)
7. [Callbacks (Webhooks)](#callbacks-webhooks)
8. [Коды ошибок](#коды-ошибок)

## Авторизация

Все запросы к API мерчанта требуют аутентификации с использованием API-ключа и HMAC-подписи.

### Заголовки запроса
```
X-API-KEY: MCH76cce1e3cae543a9be748972534441
X-SIGNATURE: <hmac_signature>
X-TIMESTAMP: <unix_timestamp>
Content-Type: application/json
```

### Получение timestamp

Для получения актуального timestamp используйте специальный endpoint:

**Endpoint:** `GET /api/v1/merchant/timestamp/`

```python
import requests

def get_timestamp():
    url = "https://monkeysmoney.net/monkey/api/v1/merchant/timestamp/"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["timestamp"]
```

### Генерация подписи

Подпись генерируется по алгоритму HMAC-SHA256:

```python
import json
import base64
import hmac
import hashlib

# Данные мерчанта (получены при регистрации)
api_key = "MCH76cce1e3cae543a9be748972534441"
secret_key_b64 = "S4TWesEluAkCUJOCkvQyOZgISqWof72HD05dXfUETHo="  # Base64 строка

# Получение timestamp
timestamp = get_timestamp()

# Данные запроса
data = {"amount": 10000, "user_id": "12", "order_type": 1, "bank": "Sberbank"}
body = json.dumps(data, separators=(',', ':'))  # Без пробелов

# Формирование сообщения для подписи
message = f"POST:/api/v1/create/deposit-transaction/:{body}:{timestamp}"

# Кодируем секретный ключ в Base64
secret_key_bytes = base64.b64encode(secret_key_b64.encode())

# Генерация подписи
signature = hmac.new(
    secret_key_bytes,
    message.encode('utf-8'),
    hashlib.sha256
).hexdigest()
```

### Формат сообщения для подписи
```
{HTTP_METHOD}:{PATH}:{BODY}:{TIMESTAMP}
```

**Примеры:**
- GET запрос: `GET:/api/v1/merchant/info/:{}:1640995200`
- POST запрос: `POST:/api/v1/create/deposit-transaction/:{"amount":10000,"user_id":"12","order_type":1,"bank":"Sberbank"}:1640995200`
- Multipart запрос: `POST:/api/v1/merchant/create/dispute/:{}:1640995200`

### Пример полного запроса

```python
import requests

headers = {
    "X-API-KEY": api_key,
    "X-SIGNATURE": signature,
    "X-TIMESTAMP": timestamp,
    "Content-Type": "application/json"
}

response = requests.post(
    "https://monkeysmoney.net/monkey/api/v1/create/deposit-transaction/",
    headers=headers,
    data=body
)
```

## Создание транзакций

### Создание депозитных транзакций

**Endpoint:** `POST /api/v1/create/deposit-transaction/`

**Параметры:**
```json
{
    "amount": 501,
    "user_id": "12",
    "order_type": 1,
    "bank": "Sberbank" // не нужен если SBP,
    "back_url": "https://your-site.com/success" // опционально
}
```

**Типы заказов (order_type):**
- `1` - C2C депозит
- `2` - SBP депозит

**Ответ:**
```json
{
    "detail": "Transaction created successfully",
    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": {
        "rub": 501.0,
        "usdt": 5.27
    },
    "rate": 95.0,
    "terminal": "terminal-uuid",
    "link": "https://processing.example.com/550e8400-e29b-41d4-a716-446655440000"
}
```

## Управление транзакциями

### Получение списка транзакций

**Endpoint:** `GET /api/v1/merchant/transactions/`

**Параметры запроса:**
- `page` (int, default: 1) - номер страницы
- `per_page` (int, default: 10) - количество элементов на странице

### Получение списка транзакций по контрагенту

**Endpoint:** `GET /api/v1/merchant/transactions/by-contr-agent/`

**Параметры запроса:**
- `contr_agent` (string, обязательный) - ID контрагента/пользователя
- `page` (int, default: 1) - номер страницы
- `per_page` (int, default: 10) - количество элементов на странице

**Ответ:**
```json
{
    "deposits": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "amount": 10000,
            "currency_transaction": 95.0,
            "status": "pending",
            "type_transaction": "deposit",
            "payment_details": {
                "id": "payment-uuid",
                "bank": {
                    "name": "Sberbank",
                    "full_name": "ПАО Сбербанк"
                },
                "card": "1234567890123456",
                "phone_number": "+79001234567"
            },
            "go_back_url": "https://your-site.com/success",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
    ],
    "pagination": {
        "total": 100,
        "per_page": 10,
        "current_page": 1,
        "total_pages": 10,
        "has_next": true,
        "has_previous": false
    }
}
```

**Ответ для транзакций по контрагенту:**
```json
{
    "deposits": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "contr_agent": "user123",
            "amount": 10000,
            "currency_transaction": 95.0,
            "status": "pending",
            "type_transaction": "deposit",
            "payment_details": {
                "id": "payment-uuid",
                "bank": {
                    "name": "Sberbank",
                    "full_name": "ПАО Сбербанк"
                },
                "card": "1234567890123456",
                "phone_number": "+79001234567"
            },
            "go_back_url": "https://your-site.com/success",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
    ],
    "contr_agent": "user123",
    "pagination": {
        "total": 15,
        "per_page": 10,
        "current_page": 1,
        "total_pages": 2,
        "has_next": true,
        "has_previous": false
    }
}
```

### Получение информации о транзакции

**Endpoint:** `GET /api/v1/merchant/transaction/`

**Параметры запроса:**
- `transaction_id` (UUID) - ID транзакции

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 10000,
    "type_transaction": "deposit",
    "status": "pending",
    "payment_details": {
        "card": "1234567890123456",
        "bank": "Sberbank",
        "phone_number": "+79001234567"
    },
    "currency_transaction": 95.0,
    "go_back_url": "https://your-site.com/success",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

## Диспуты

### Создание диспута

**Endpoint:** `POST /api/v1/merchant/create/dispute/`

**Content-Type:** `multipart/form-data`

**Параметры:**
- `transaction_id` (UUID) - ID транзакции
- `note` (string, опционально) - комментарий к диспуту
- `file` (file[]) - файлы-доказательства (обязательно)

**Поддерживаемые форматы файлов:** pdf, jpeg, jpg, png, mp4
**Максимальный размер файла:** 100MB

**Ответ:**
```json
{
    "message": "Dispute created successfully",
    "dispute_id": "dispute-uuid",
    "files": [
        "https://s3.example.com/disputes/dispute-uuid/file1.pdf",
        "https://s3.example.com/disputes/dispute-uuid/file2.jpg"
    ]
}
```

### Получение списка диспутов

**Endpoint:** `GET /api/v1/merchant/disputes/`

**Параметры запроса:**
- `page` (int, default: 1) - номер страницы
- `per_page` (int, default: 10) - количество элементов на странице

### Получение списка диспутов по контрагенту

**Endpoint:** `GET /api/v1/merchant/disputes/by-contr-agent/`

**Параметры запроса:**
- `contr_agent` (string, обязательный) - ID контрагента/пользователя
- `page` (int, default: 1) - номер страницы
- `per_page` (int, default: 10) - количество элементов на странице

**Ответ:**
```json
{
    "disputes": [
        {
            "id": "dispute-uuid",
            "status": "waiting",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "transaction": {
                "id": "transaction-uuid",
                "status": "dispute",
                "created_at": "2024-01-01T11:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "amount": 10000,
                "go_back_url": "https://your-site.com/success",
                "currency_transaction": 95.0
            },
            "comments": "Платеж не поступил",
            "files_from_merchant": [
                "https://s3.example.com/disputes/dispute-uuid/file1.pdf"
            ],
            "files_from_trader": []
        }
    ],
    "pagination": {
        "total": 5,
        "per_page": 10,
        "current_page": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

**Ответ для диспутов по контрагенту:**
```json
{
    "disputes": [
        {
            "id": "dispute-uuid",
            "status": "waiting",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "transaction": {
                "id": "transaction-uuid",
                "contr_agent": "user123",
                "status": "dispute",
                "created_at": "2024-01-01T11:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "amount": 10000,
                "go_back_url": "https://your-site.com/success",
                "currency_transaction": 95.0
            },
            "comments": "Платеж не поступил",
            "files_from_merchant": [
                "https://s3.example.com/disputes/dispute-uuid/file1.pdf"
            ],
            "files_from_trader": []
        }
    ],
    "contr_agent": "user123",
    "pagination": {
        "total": 3,
        "per_page": 10,
        "current_page": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

### Получение информации о диспуте

**Endpoint:** `GET /api/v1/merchant/dispute/`

**Параметры запроса:**
- `dispute_id` (UUID) - ID диспута

**Ответ:**
```json
{
    "dispute": {
        "id": "dispute-uuid",
        "status": "waiting",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "transaction": {
            "id": "transaction-uuid",
            "status": "dispute",
            "created_at": "2024-01-01T11:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "amount": 10000,
            "go_back_url": "https://your-site.com/success",
            "currency_transaction": 95.0
        },
        "comments": "Платеж не поступил",
        "files_from_merchant": [
            "https://s3.example.com/disputes/dispute-uuid/file1.pdf"
        ],
        "files_from_trader": []
    }
}
```

## Справочная информация

### Получение списка банков

**Endpoint:** `GET /api/v1/merchant/banks/`

**Ответ:**
```json
{
    "deposit": [
        {
            "name": "Sberbank",
            "full_name": "ПАО Сбербанк"
        },
        {
            "name": "VTB",
            "full_name": "Банк ВТБ (ПАО)"
        }
    ],
    "withdraw": [
        {
            "name": "Tinkoff",
            "full_name": "АО Тинькофф Банк"
        }
    ]
}
```

### Получение списка валют

**Endpoint:** `GET /api/v1/merchant/currency/`

**Ответ:**
```json
{
    "crypto": [
        {
            "name": "Tether",
            "symbol": "USDT"
        },
        {
            "name": "Bitcoin",
            "symbol": "BTC"
        }
    ],
    "deposit": [
        {
            "name": "Russian Ruble",
            "symbol": "₽"
        }
    ],
    "withdraw": [
        {
            "name": "US Dollar",
            "symbol": "$"
        }
    ]
}
```

## Настройки мерчанта

### Получение информации о мерчанте

**Endpoint:** `GET /api/v1/merchant/info/`

**Ответ:**
```json
{
    "merchant": {
        "id": "merchant-uuid",
        "name": "My Shop",
        "address": "TRX7n2oDZeXoNb1eYoAaKxgTdgPWiQh9gC",
        "balance": 1500.25,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

### Изменение Callback URL

**Endpoint:** `POST /api/v1/merchant/change/callback-url/`

**Параметры:**
```json
{
    "url": "https://your-site.com/webhook"
}
```

**Ответ:**
```json
{
    "message": "Callback URL changed successfully"
}
```

## Callbacks (Webhooks)

Система автоматически отправляет уведомления на ваш webhook URL при изменении статуса транзакций и диспутов.

### Callback для транзакций

**URL:** Ваш webhook URL  
**Method:** POST  
**Content-Type:** application/json  
**Headers:**
- `X-SIGNATURE` - HMAC-SHA256 подпись для проверки подлинности
- `X-TIMESTAMP` - Unix timestamp запроса
- `User-Agent` - MineFactory-Callback/1.0

**Структура данных:**
```json
{
    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "amount": 10000.0,
    "currency_transaction": 95.0,
    "type_transaction": "deposit"
}
```

### Callback для диспутов

**URL:** Ваш webhook URL  
**Method:** POST  
**Content-Type:** application/json  
**Headers:**
- `X-SIGNATURE` - HMAC-SHA256 подпись для проверки подлинности
- `X-TIMESTAMP` - Unix timestamp запроса
- `User-Agent` - MineFactory-Callback/1.0

**Структура данных:**
```json
{
    "dispute": {
        "id": "dispute-uuid",
        "status": "completed_towards_merchant"
    },
    "transaction": {
        "id": "transaction-uuid",
        "status": "completed",
        "amount": 10000.0,
        "currency_transaction": 95.0,
        "type_transaction": "deposit"
    }
}
```

### Проверка подписи callback

Подпись передается в заголовке `X-SIGNATURE` и генерируется по тому же алгоритму, что и в основном API:

```python
import hmac
import hashlib
import json
import base64

def verify_callback_signature(request_data, signature_header, timestamp_header, secret_key_b64):
    """
    Проверяет подпись callback запроса
    """
    if not signature_header or not timestamp_header:
        return False
    
    # Формируем сообщение для проверки
    if 'transaction_id' in request_data:
        path = 'mm/callback-merchant-deposit'
    else:
        path = 'mm/callback-merchant-dispute'
    
    body = json.dumps(request_data, separators=(',', ':'))
    message = f"POST:{path}:{body}:{timestamp_header}"
    
    secret_key_bytes = base64.b64encode(secret_key_b64.encode())
    expected_signature = hmac.new(
        secret_key_bytes,
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature_header, expected_signature)
```

## Статусы транзакций

- `pending` - Ожидает оплаты
- `verification` - На проверке
- `complete` - Завершена
- `dispute` - В диспуте
- `canceled` - Отменена
- `expired` - Истекла (автоматически через 30 минут)

## Статусы диспутов

- `waiting` - Ожидает доказательств
- `consideration` - На рассмотрении
- `deepconsideration` - Углубленное рассмотрение
- `completed_towards_merchant` - Завершен в пользу мерчанта
- `completed_towards_trader` - Завершен в пользу трейдера

## Коды ошибок

### HTTP статусы

- `200` - Успешно
- `201` - Создано
- `400` - Неверный запрос
- `401` - Неавторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера
- `503` - Сервис недоступен

### Типичные ошибки

**Неверная подпись:**
```json
{
    "error": "Invalid signature"
}
```

**Неверный API ключ:**
```json
{
    "error": "Invalid authentication credentials"
}
```

**Отсутствует timestamp:**
```json
{
    "error": "Timestamp header is required"
}
```

**Устаревший timestamp:**
```json
{
    "error": "Timestamp is expired"
}
```

**Отсутствует подпись:**
```json
{
    "error": "Signature header is required"
}
```

**Недостаточно средств:**
```json
{
    "detail": "No available terminals with sufficient balance"
}
```

**Неверная сумма:**
```json
{
    "detail": "Invalid amount value"
}
```

**Транзакция не найдена:**
```json
{
    "error": "Transaction not found"
}
```

**Диспут уже существует:**
```json
{
    "error": "Dispute for transaction already exists"
}
```

## Ограничения

- Минимальная сумма транзакции: 100 RUB
- Максимальный размер файла для диспута: 100MB
- Поддерживаемые форматы файлов: pdf, jpeg, jpg, png, mp4
- Время жизни транзакции: 30 минут
- Webhook URL должен использовать HTTPS
- Timestamp не должен отличаться от серверного времени более чем на 1000 секунд
- Все запросы должны содержать заголовки X-API-KEY, X-SIGNATURE и X-TIMESTAMP

## Примеры интеграции

### Создание депозита с проверкой статуса

```python
import requests
import time
import json
import base64
import hmac
import hashlib

class MerchantAPI:
    def __init__(self, api_key, secret_key_b64, base_url):
        self.api_key = api_key
        self.secret_key_b64 = secret_key_b64
        self.base_url = base_url
    
    def get_timestamp(self):
        """Получение актуального timestamp с сервера"""
        url = f"{self.base_url}/api/v1/merchant/timestamp/"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["timestamp"]
    
    def _generate_signature(self, method, path, body='', timestamp=None):
        if timestamp is None:
            timestamp = self.get_timestamp()
        
        message = f"{method}:{path}:{body}:{timestamp}"
        secret_key_bytes = base64.b64encode(self.secret_key_b64.encode())
        return hmac.new(
            secret_key_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest(), timestamp
    
    def _make_request(self, method, path, data=None):
        body = json.dumps(data, separators=(',', ':')) if data else '{}'
        signature, timestamp = self._generate_signature(method, path, body)
        
        headers = {
            "X-API-KEY": self.api_key,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{path}"
        
        if method == 'GET':
            return requests.get(url, headers=headers)
        elif method == 'POST':
            return requests.post(url, headers=headers, data=body)
    
    def create_deposit(self, amount, user_id, order_type, bank, back_url=None):
        """
        Создание депозитной транзакции
        order_type: 1 - C2C, 2 - SBP
        """
        data = {
            "amount": amount,
            "user_id": user_id,
            "order_type": order_type,
            "bank": bank
        }
        if back_url:
            data["back_url"] = back_url
        
        response = self._make_request('POST', '/api/v1/create/deposit-transaction/', data)
        return response.json()
    
    def get_transaction_info(self, transaction_id):
        response = self._make_request('GET', f'/api/v1/merchant/transaction/?transaction_id={transaction_id}')
        return response.json()

# Использование
api = MerchantAPI(
    api_key="MCH76cce1e3cae543a9be748972534441",
    secret_key_b64="S4TWesEluAkCUJOCkvQyOZgISqWof72HD05dXfUETHo=",
    base_url="https://monkeysmoney.net/monkey"
)

# Создание C2C депозита
result = api.create_deposit(
    amount=501,
    user_id="12",
    order_type=1,  # C2C
    bank="Sberbank",
    back_url="https://mysite.com/success"
)

transaction_id = result['transaction_id']
payment_link = result['link']

print(f"Транзакция создана: {transaction_id}")
print(f"Ссылка для оплаты: {payment_link}")

# Проверка статуса
while True:
    info = api.get_transaction_info(transaction_id)
    status = info['status']
    
    print(f"Статус: {status}")
    
    if status in ['complete', 'canceled', 'expired']:
        break
    
    time.sleep(30)  # Проверяем каждые 30 секунд
```
