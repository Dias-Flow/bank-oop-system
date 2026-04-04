from bank_system import Bank, Client
from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import Currency, TransactionType, AuditLevel
from transactions import Transaction, TransactionQueue, TransactionProcessor
from audit import AuditLog, RiskAnalyzer


def main():
    bank = Bank("Dias Bank")

    audit_log = AuditLog("audit.log")
    risk_analyzer = RiskAnalyzer()
    processor = TransactionProcessor(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )
    queue = TransactionQueue()

    # Клиенты
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

    # Счета
    acc1 = SavingsAccount(
        owner=client1.full_name,
        balance=6000,
        currency=Currency.USD,
        min_balance=500,
        interest_rate=0.02
    )
    acc2 = PremiumAccount(
        owner=client2.full_name,
        balance=3000,
        currency=Currency.EUR,
        overdraft_limit=4000,
        transaction_fee=20
    )
    acc3 = InvestmentAccount(
        owner=client3.full_name,
        balance=8000,
        currency=Currency.USD,
        portfolio={"stocks": 12000, "bonds": 5000, "etf": 4000}
    )
    acc4 = SavingsAccount(
        owner=client1.full_name,
        balance=1200,
        currency=Currency.KZT,
        min_balance=200,
        interest_rate=0.01
    )

    bank.open_account(client1.client_id, acc1)
    bank.open_account(client2.client_id, acc2)
    bank.open_account(client3.client_id, acc3)
    bank.open_account(client1.client_id, acc4)

    print("=== НАЧАЛЬНЫЕ БАЛАНСЫ ===")
    print(acc1)
    print(acc2)
    print(acc3)
    print(acc4)
    print()

    # Обычные и подозрительные транзакции
    transactions = [
        Transaction(TransactionType.TRANSFER, 200, Currency.USD, sender=acc1, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 150, Currency.EUR, sender=acc2, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 100, Currency.USD, sender=acc3, receiver=acc2),

        # Подозрительные: крупные суммы / новые получатели / серия операций
        Transaction(TransactionType.TRANSFER, 7000, Currency.USD, sender=acc1, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 5200, Currency.USD, sender=acc3, receiver=acc4),
        Transaction(TransactionType.TRANSFER, 300, Currency.USD, sender=acc1, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 350, Currency.USD, sender=acc1, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 400, Currency.USD, sender=acc1, receiver=acc2),

        # Ошибочные
        Transaction(TransactionType.TRANSFER, 15000, Currency.USD, sender=acc1, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 500, Currency.KZT, sender=acc4, receiver=acc2),
    ]

    # Добавляем в очередь
    queue.add_transaction(transactions[0])
    queue.add_transaction(transactions[1])
    queue.add_transaction(transactions[2], priority=True)
    queue.add_transaction(transactions[3], priority=True)
    queue.add_transaction(transactions[4])
    queue.add_transaction(transactions[5])
    queue.add_transaction(transactions[6])
    queue.add_transaction(transactions[7])
    queue.add_transaction(transactions[8])
    queue.add_transaction(transactions[9], delayed=True)

    print("=== ОБРАБОТКА ТРАНЗАКЦИЙ ===")
    processed_transactions = []

    while True:
        transaction = queue.get_next_transaction()
        if transaction is None:
            break

        result = processor.process_with_retry(transaction)
        processed_transactions.append(result)

        print(result)
        if result.failure_reason:
            print("Причина:", result.failure_reason)
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

    print("=== ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ ===")
    suspicious_report = risk_analyzer.get_suspicious_operations_report()
    for item in suspicious_report:
        tx = item["transaction"]
        print(
            f"{tx.transaction_id} | {item['risk_level'].value} | "
            f"score={item['risk_score']} | reasons={', '.join(item['reasons'])}"
        )
    print()

    print("=== РИСК-ПРОФИЛЬ КЛИЕНТОВ ===")
    for client in [client1, client2, client3]:
        profile = risk_analyzer.get_client_risk_profile(client.full_name)
        print(profile)
    print()

    print("=== СТАТИСТИКА ОШИБОК ===")
    error_stats = processor.get_error_statistics()
    for reason, count in error_stats.items():
        print(f"{reason}: {count}")
    print()

    print("=== АУДИТ: WARNING ===")
    for log in audit_log.filter_logs(AuditLevel.WARNING):
        print(f"[{log['time']}] [{log['level'].value}] {log['message']}")
    print()

    print("=== АУДИТ: CRITICAL ===")
    for log in audit_log.filter_logs(AuditLevel.CRITICAL):
        print(f"[{log['time']}] [{log['level'].value}] {log['message']}")
    print()


if __name__ == "__main__":
    main()