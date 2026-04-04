from bank_system import Bank, Client
from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import Currency, TransactionType
from transactions import Transaction, TransactionQueue, TransactionProcessor


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

    bank.add_client(client1)
    bank.add_client(client2)
    bank.add_client(client3)

    # Создаем счета
    acc1 = SavingsAccount(
        owner=client1.full_name,
        balance=5000,
        currency=Currency.USD,
        min_balance=500,
        interest_rate=0.02
    )

    acc2 = PremiumAccount(
        owner=client2.full_name,
        balance=2000,
        currency=Currency.EUR,
        overdraft_limit=3000,
        transaction_fee=20
    )

    acc3 = InvestmentAccount(
        owner=client3.full_name,
        balance=7000,
        currency=Currency.USD,
        portfolio={"stocks": 10000, "bonds": 4000, "etf": 3000}
    )

    acc4 = SavingsAccount(
        owner=client1.full_name,
        balance=1500,
        currency=Currency.KZT,
        min_balance=200,
        interest_rate=0.01
    )

    bank.open_account(client1.client_id, acc1)
    bank.open_account(client2.client_id, acc2)
    bank.open_account(client3.client_id, acc3)
    bank.open_account(client1.client_id, acc4)

    # Создаем очередь и процессор
    queue = TransactionQueue()
    processor = TransactionProcessor(bank)

    # Создаем 10 транзакций
    transactions = [
        Transaction(TransactionType.TRANSFER, 300, Currency.USD, sender=acc1, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 250, Currency.EUR, sender=acc2, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 100, Currency.USD, sender=acc3, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 1200, Currency.USD, sender=acc1, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 500, Currency.KZT, sender=acc4, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 200, Currency.USD, sender=acc3, receiver=acc4),
        Transaction(TransactionType.TRANSFER, 50, Currency.EUR, sender=acc2, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 9000, Currency.USD, sender=acc1, receiver=acc3),   # должен провалиться
        Transaction(TransactionType.TRANSFER, 400, Currency.USD, sender=acc3, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 150, Currency.KZT, sender=acc4, receiver=acc2),
    ]

    # Добавляем транзакции в очередь
    queue.add_transaction(transactions[0], priority=True)
    queue.add_transaction(transactions[1])
    queue.add_transaction(transactions[2])
    queue.add_transaction(transactions[3], priority=True)
    queue.add_transaction(transactions[4])
    queue.add_transaction(transactions[5], delayed=True)
    queue.add_transaction(transactions[6])
    queue.add_transaction(transactions[7])
    queue.add_transaction(transactions[8], priority=True)
    queue.add_transaction(transactions[9])

    print("=== НАЧАЛЬНЫЕ БАЛАНСЫ ===")
    print(acc1)
    print(acc2)
    print(acc3)
    print(acc4)
    print()

    print("=== ОБРАБОТКА ОЧЕРЕДИ ТРАНЗАКЦИЙ ===")
    processed_transactions = []

    while True:
        transaction = queue.get_next_transaction()
        if transaction is None:
            break

        result = processor.process_with_retry(transaction)
        processed_transactions.append(result)
        print(result)
        if result.failure_reason:
            print("Причина ошибки:", result.failure_reason)
        print()

    print("=== ОТЛОЖЕННЫЕ ТРАНЗАКЦИИ ===")
    for delayed_transaction in queue.delayed_queue:
        print(delayed_transaction)
    print()

    print("=== ИТОГОВЫЕ БАЛАНСЫ ===")
    print(acc1)
    print(acc2)
    print(acc3)
    print(acc4)
    print()

    print("=== НЕУДАЧНЫЕ ТРАНЗАКЦИИ ===")
    for failed_transaction in processor.failed_transactions:
        print(failed_transaction)
        print("Причина:", failed_transaction.failure_reason)
        print()


if __name__ == "__main__":
    main()