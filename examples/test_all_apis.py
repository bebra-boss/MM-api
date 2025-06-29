#!/usr/bin/env python3
"""
Полный тест всех API методов MerchantAPI
Этот скрипт тестирует все доступные методы API по очереди
"""

import sys
import time
from merchant_api import MerchantAPI
from settings import api_key, secret_key_b64

def print_separator(title):
    """Печать разделителя для лучшей читаемости"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(method_name, success, data=None, error=None):
    """Печать результата тестирования метода"""
    status = "✅ УСПЕХ" if success else "❌ ОШИБКА"
    print(f"{status} {method_name}")
    
    if success and data:
        print(f"  Результат: {str(data)[:200]}...")
    elif error:
        print(f"  Ошибка: {error}")
    print("-" * 40)

def test_api_method(api, method_name, method_func, *args, **kwargs):
    """Универсальная функция для тестирования API методов"""
    try:
        print(f"🔄 Тестирование {method_name}...")
        result = method_func(*args, **kwargs)
        print_result(method_name, True, result)
        return True, result
    except Exception as e:
        print_result(method_name, False, error=str(e))
        return False, None

def main():
    """Основная функция тестирования"""
    print_separator("ТЕСТИРОВАНИЕ API МЕРЧАНТА")
    print(f"API Key: {api_key[:20]}...")
    print(f"Secret Key: {secret_key_b64[:20]}...")
    
    # Инициализация API клиента
    try:
        api = MerchantAPI(api_key, secret_key_b64)
        print("✅ API клиент инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации API: {e}")
        return
    
    # Счетчики для статистики
    total_tests = 0
    successful_tests = 0
    transaction_id = None
    dispute_id = None
    
    # 1. Тест получения timestamp
    print_separator("1. ТЕСТ ПОЛУЧЕНИЯ TIMESTAMP")
    total_tests += 1
    success, result = test_api_method(api, "get_timestamp", api.get_timestamp)
    if success:
        successful_tests += 1
        print(f"  Timestamp: {result}")
    
    # 2. Тест получения информации о мерчанте
    print_separator("2. ТЕСТ ИНФОРМАЦИИ О МЕРЧАНТЕ")
    total_tests += 1
    success, result = test_api_method(api, "get_merchant_info", api.get_merchant_info)
    if success:
        successful_tests += 1
        merchant_name = result.get('merchant', {}).get('name', 'N/A')
        merchant_balance = result.get('merchant', {}).get('balance', 'N/A')
        print(f"  Мерчант: {merchant_name}")
        print(f"  Баланс: {merchant_balance}")
    
    # 3. Тест получения списка банков
    print_separator("3. ТЕСТ СПИСКА БАНКОВ")
    total_tests += 1
    success, result = test_api_method(api, "get_banks_list", api.get_banks_list)
    if success:
        successful_tests += 1
        deposit_banks = len(result.get('deposit', []))
        withdraw_banks = len(result.get('withdraw', []))
        print(f"  Банки для депозитов: {deposit_banks}")
        print(f"  Банки для выводов: {withdraw_banks}")
    
    # 4. Тест получения списка валют
    print_separator("4. ТЕСТ СПИСКА ВАЛЮТ")
    total_tests += 1
    success, result = test_api_method(api, "get_currencies_list", api.get_currencies_list)
    if success:
        successful_tests += 1
        crypto_count = len(result.get('crypto', []))
        print(f"  Криптовалют: {crypto_count}")
    
    # 5. Тест создания транзакции
    print_separator("5. ТЕСТ СОЗДАНИЯ ТРАНЗАКЦИИ")
    total_tests += 1
    success, result = test_api_method(
        api, "create_deposit_transaction", api.create_deposit_transaction,
        amount=502,
        user_id="test_user_123",
        order_type=1,  # C2C
        bank="Sberbank",
        back_url="https://example.com/success"
    )
    if success:
        successful_tests += 1
        transaction_id = result.get('transaction_id')
        payment_link = result.get('link')
        amount_info = result.get('amount', {})
        print(f"  Transaction ID: {transaction_id}")
        print(f"  Ссылка для оплаты: {payment_link}")
        print(f"  Сумма: {amount_info.get('rub')} RUB / {amount_info.get('usdt')} USDT")
    
    # 6. Тест получения информации о транзакции
    if transaction_id:
        print_separator("6. ТЕСТ ИНФОРМАЦИИ О ТРАНЗАКЦИИ")
        total_tests += 1
        success, result = test_api_method(
            api, "get_transaction_info", api.get_transaction_info,
            transaction_id
        )
        if success:
            successful_tests += 1
            status = result.get('status', 'N/A')
            amount = result.get('amount', 'N/A')
            print(f"  Статус: {status}")
            print(f"  Сумма: {amount}")
    
    # 7. Тест получения списка транзакций
    print_separator("7. ТЕСТ СПИСКА ТРАНЗАКЦИЙ")
    total_tests += 1
    success, result = test_api_method(
        api, "get_transactions_list", api.get_transactions_list,
        page=1, per_page=5
    )
    if success:
        successful_tests += 1
        deposits_count = len(result.get('deposits', []))
        total_transactions = result.get('pagination', {}).get('total', 0)
        print(f"  Транзакций на странице: {deposits_count}")
        print(f"  Всего транзакций: {total_transactions}")
    
    # 8. Тест получения транзакций по контрагенту
    print_separator("8. ТЕСТ ТРАНЗАКЦИЙ ПО КОНТРАГЕНТУ")
    total_tests += 1
    test_contr_agent = "test_user_123"
    success, result = test_api_method(
        api, "get_transactions_by_contr_agent", api.get_transactions_by_contr_agent,
        contr_agent=test_contr_agent, page=1, per_page=5
    )
    if success:
        successful_tests += 1
        deposits_count = len(result.get('deposits', []))
        contr_agent = result.get('contr_agent', 'N/A')
        print(f"  Контрагент: {contr_agent}")
        print(f"  Транзакций найдено: {deposits_count}")
    
    # 9. Тест получения списка диспутов
    print_separator("9. ТЕСТ СПИСКА ДИСПУТОВ")
    total_tests += 1
    success, result = test_api_method(
        api, "get_disputes_list", api.get_disputes_list,
        page=1, per_page=5
    )
    if success:
        successful_tests += 1
        disputes_count = len(result.get('disputes', []))
        total_disputes = result.get('pagination', {}).get('total', 0)
        print(f"  Диспутов на странице: {disputes_count}")
        print(f"  Всего диспутов: {total_disputes}")
        
        # Сохраняем ID первого диспута для дальнейшего тестирования
        if disputes_count > 0:
            dispute_id = result['disputes'][0]['id']
    
    # 10. Тест получения диспутов по контрагенту
    print_separator("10. ТЕСТ ДИСПУТОВ ПО КОНТРАГЕНТУ")
    total_tests += 1
    success, result = test_api_method(
        api, "get_disputes_by_contr_agent", api.get_disputes_by_contr_agent,
        contr_agent=test_contr_agent, page=1, per_page=5
    )
    if success:
        successful_tests += 1
        disputes_count = len(result.get('disputes', []))
        contr_agent = result.get('contr_agent', 'N/A')
        print(f"  Контрагент: {contr_agent}")
        print(f"  Диспутов найдено: {disputes_count}")
    
    # 11. Тест получения информации о диспуте
    if dispute_id:
        print_separator("11. ТЕСТ ИНФОРМАЦИИ О ДИСПУТЕ")
        total_tests += 1
        success, result = test_api_method(
            api, "get_dispute_info", api.get_dispute_info,
            dispute_id
        )
        if success:
            successful_tests += 1
            dispute_status = result.get('dispute', {}).get('status', 'N/A')
            transaction_info = result.get('dispute', {}).get('transaction', {})
            print(f"  Статус диспута: {dispute_status}")
            print(f"  ID транзакции: {transaction_info.get('id', 'N/A')}")
    
    # 12. Тест изменения callback URL (осторожно - может изменить настройки!)
    print_separator("12. ТЕСТ ИЗМЕНЕНИЯ CALLBACK URL")
    print("⚠️  ПРОПУЩЕН - может изменить настройки мерчанта")
    print("   Для тестирования раскомментируйте код ниже:")
    print("   # success, result = test_api_method(")
    print("   #     api, 'change_callback_url', api.change_callback_url,")
    print("   #     'https://example.com/webhook'")
    print("   # )")
    
    # Тест создания SBP транзакции
    print_separator("13. ТЕСТ СОЗДАНИЯ SBP ТРАНЗАКЦИИ")
    total_tests += 1
    success, result = test_api_method(
        api, "create_sbp_transaction", api.create_deposit_transaction,
        amount=750,
        user_id="test_sbp_user_" + str(int(time.time())),
        order_type=2,  # SBP
        bank="Sberbank"
    )
    if success:
        successful_tests += 1
        transaction_id_sbp = result.get('transaction_id')
        print(f"  SBP Transaction ID: {transaction_id_sbp}")
    
    # Финальная статистика
    print_separator("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Успешных: {successful_tests}")
    print(f"Неудачных: {total_tests - successful_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Отличный результат! API работает стабильно.")
    elif success_rate >= 60:
        print("⚠️  Хороший результат, но есть проблемы с некоторыми методами.")
    else:
        print("❌ Много ошибок. Необходимо проверить конфигурацию API.")
    
    print("\n" + "="*60)
    print("Тестирование завершено!")
    print("="*60)

if __name__ == "__main__":
    main() 