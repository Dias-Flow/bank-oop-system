from bank_system import Client, Bank
from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import Currency
from exceptions import AccountFrozenError


def main():
    bank = Bank("Dias Bank")

    # Создаем клиентов
    client1 = Client(
        full_name="Dias Flow",
        age=21,
        contacts={"phone": "+77001112233", "email": "dias@mail.com"}
    )

    client2 = Client(
        full_name="Alex Ivanov",
        age=30,
        contacts={"phone": "+77004445566", "email": "alex@mail.com"}
    )

    client3 = Client(
        full_name="Maria Petrova",
        age=27,
        contacts={"phone": "+77007778899", "email": "maria@mail.com"}
    )

    # Добавляем клиентов в банк
    bank.add_client(client1)
    bank.add_client(client2)
    bank.add_client(client3)

    print("=== КЛИЕНТЫ ДОБАВЛЕНЫ В БАНК ===")
    print(client1)
    print(client2)
    print(client3)
    print()

    # Создаем счета
    savings_account = SavingsAccount(
        owner=client1.full_name,
        balance=3000,
        currency=Currency.USD,
        min_balance=500,
        interest_rate=0.02
    )

    premium_account = PremiumAccount(
        owner=client2.full_name,
        balance=1000,
        currency=Currency.EUR,
        overdraft_limit=2000,
        transaction_fee=20
    )

    investment_account = InvestmentAccount(
        owner=client3.full_name,
        balance=5000,
        portfolio={
            "stocks": 10000,
            "bonds": 4000,
            "etf": 6000
        }
    )

    # Открываем счета в банке
    bank.open_account(client1.client_id, savings_account)
    bank.open_account(client2.client_id, premium_account)
    bank.open_account(client3.client_id, investment_account)

    print("=== СЧЕТА ОТКРЫТЫ ===")
    print(savings_account)
    print(premium_account)
    print(investment_account)
    print()

    # Проверка поиска счетов клиента
    print("=== СЧЕТА КЛИЕНТА Dias Flow ===")
    for account in bank.search_accounts(client1.client_id):
        print(account)
    print()

    # Проверка успешной аутентификации
    print("=== УСПЕШНАЯ АУТЕНТИФИКАЦИЯ ===")
    authenticated_client = bank.authenticate_client(client1.client_id)
    print("Вход выполнен:", authenticated_client)
    print()

    # Проверка неудачных попыток входа
    print("=== НЕУДАЧНЫЕ ПОПЫТКИ ВХОДА ===")
    fake_id = "wrong123"

    for attempt in range(1, 4):
        try:
            bank.authenticate_client(fake_id)
        except ValueError as e:
            print(f"Попытка {attempt}: {e}")

    print("Заблокированные клиенты:", bank.blocked_clients)
    print()

    # Заморозка счета
    print("=== ЗАМОРОЗКА СЧЕТА ===")
    bank.freeze_account(savings_account.account_id)
    print("Статус счета после заморозки:", savings_account.status.value)

    try:
        savings_account.deposit(100)
    except AccountFrozenError as e:
        print("Ошибка операции:", e)
    print()

    # Разморозка счета
    print("=== РАЗМОРОЗКА СЧЕТА ===")
    bank.unfreeze_account(savings_account.account_id)
    print("Статус счета после разморозки:", savings_account.status.value)
    savings_account.deposit(100)
    print("После пополнения:", savings_account)
    print()

    # Аналитика банка
    print("=== ОБЩИЙ БАЛАНС БАНКА ===")
    print(bank.get_total_balance())
    print()

    print("=== РЕЙТИНГ КЛИЕНТОВ ===")
    for full_name, total_balance in bank.get_clients_ranking():
        print(f"{full_name}: {total_balance:.2f}")
    print()

    print("=== ПОДОЗРИТЕЛЬНЫЕ ДЕЙСТВИЯ ===")
    for action in bank.suspicious_actions:
        print(action)


if __name__ == "__main__":
    main()