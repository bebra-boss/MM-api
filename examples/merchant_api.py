import requests
import json
import base64
import hmac
import hashlib
from settings import api_key, secret_key_b64

class MerchantAPI:
    def __init__(self, api_key, secret_key_b64, base_url="https://monkeysmoney.net/monkey"):
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
        if response.status_code != 200:
            raise Exception(f"Failed to get timestamp: {response.text}")
        
        data = response.json()
        return data["timestamp"]
    
    def _generate_signature(self, method, path, body='{}', timestamp=None):
        """Генерация HMAC подписи для запроса"""
        if timestamp is None:
            timestamp = self.get_timestamp()
        
        message = f"{method}:{path}:{body}:{timestamp}"
        secret_key_bytes = base64.b64encode(self.secret_key_b64.encode())
        
        signature = hmac.new(
            secret_key_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def _make_request(self, method, path, data=None, params=None):
        """Универсальный метод для выполнения запросов"""
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
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    
    def create_deposit_transaction(self, amount, user_id, order_type, bank, back_url=None):
        """
        Создание депозитной транзакции
        
        Args:
            amount (int): Сумма в копейках
            user_id (str): ID пользователя
            order_type (int): Тип заказа (1 - C2C, 2 - SBP)
            bank (str): Название банка
            back_url (str, optional): URL для возврата после оплаты
        
        Returns:
            dict: Информация о созданной транзакции
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
        print(response)
        
        if response.status_code != 201:
            raise Exception(f"Failed to create transaction: {response.text}")
        
        return response.json()
    
    def get_transaction_info(self, transaction_id):
        """Получение информации о транзакции"""
        params = {"transaction_id": transaction_id}
        response = self._make_request('GET', '/api/v1/merchant/transaction/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get transaction info: {response.text}")
        
        return response.json()
    
    def get_transactions_list(self, page=1, per_page=10):
        """Получение списка транзакций"""
        params = {"page": page, "per_page": per_page}
        response = self._make_request('GET', '/api/v1/merchant/transactions/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get transactions list: {response.text}")
        
        return response.json()
    
    def get_transactions_by_contr_agent(self, contr_agent, page=1, per_page=10):
        """Получение списка транзакций по контрагенту"""
        params = {"contr_agent": contr_agent, "page": page, "per_page": per_page}
        response = self._make_request('GET', '/api/v1/merchant/transactions/by-contr-agent/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get transactions by contr_agent: {response.text}")
        
        return response.json()
    
    def get_merchant_info(self):
        """Получение информации о мерчанте"""
        response = self._make_request('GET', '/api/v1/merchant/info/')
        
        if response.status_code != 200:
            raise Exception(f"Failed to get merchant info: {response.text}")
        
        return response.json()
    
    def get_banks_list(self):
        """Получение списка банков"""
        response = self._make_request('GET', '/api/v1/merchant/banks/')
        
        if response.status_code != 200:
            raise Exception(f"Failed to get banks list: {response.text}")
        
        return response.json()
    
    def get_currencies_list(self):
        """Получение списка валют"""
        response = self._make_request('GET', '/api/v1/merchant/currency/')
        
        if response.status_code != 200:
            raise Exception(f"Failed to get currencies list: {response.text}")
        
        return response.json()
    
    def change_callback_url(self, url):
        """Изменение callback URL"""
        data = {"url": url}
        response = self._make_request('POST', '/api/v1/merchant/change/callback-url/', data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to change callback URL: {response.text}")
        
        return response.json()
    
    def get_disputes_list(self, page=1, per_page=10):
        """Получение списка диспутов"""
        params = {"page": page, "per_page": per_page}
        response = self._make_request('GET', '/api/v1/merchant/disputes/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get disputes list: {response.text}")
        
        return response.json()
    
    def get_disputes_by_contr_agent(self, contr_agent, page=1, per_page=10):
        """Получение списка диспутов по контрагенту"""
        params = {"contr_agent": contr_agent, "page": page, "per_page": per_page}
        response = self._make_request('GET', '/api/v1/merchant/disputes/by-contr-agent/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get disputes by contr_agent: {response.text}")
        
        return response.json()
    
    def get_dispute_info(self, dispute_id):
        """Получение информации о диспуте"""
        params = {"dispute_id": dispute_id}
        response = self._make_request('GET', '/api/v1/merchant/dispute/', params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get dispute info: {response.text}")
        
        return response.json()

# Пример использования
if __name__ == "__main__":
    # Инициализация API клиента
    api = MerchantAPI(api_key, secret_key_b64)
    
    try:
        # Создание C2C транзакции
        print("Создание C2C транзакции...")
        transaction = api.create_deposit_transaction(
            amount=1001,
            user_id="test_user_123",
            order_type=1,  # C2C
            bank="",
            back_url="https://example.com/success"
        )
        
        print(transaction)
        print(f"Транзакция создана:")
        print(f"ID: {transaction['transaction_id']}")
        print(f"Ссылка для оплаты: {transaction['link']}")
        print(f"Сумма: {transaction['amount']['rub']} RUB")
        
        # Получение информации о транзакции
        print("\nПолучение информации о транзакции...")
        info = api.get_transaction_info(transaction['transaction_id'])
        print(f"Статус: {info['status']}")
        
        # Получение информации о мерчанте
        print("\nИнформация о мерчанте:")
        merchant_info = api.get_merchant_info()
        print(f"Название: {merchant_info['merchant']['name']}")
        print(f"Баланс: {merchant_info['merchant']['balance']}")
        
    except Exception as e:
        print(f"Ошибка: {e}") 