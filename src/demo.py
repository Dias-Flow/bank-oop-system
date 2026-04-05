from bank_system import Bank, Client
from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import Currency, TransactionType, TransactionStatus, AuditLevel
from transactions import Transaction, TransactionQueue, TransactionProcessor
from audit import AuditLog, RiskAnalyzer
from reports import ReportBuilder


def create_bank_system():
    bank = Bank("Dias Demo Bank")
    audit_log = AuditLog("audit.log")
    risk_analyzer = RiskAnalyzer()
    queue = TransactionQueue()
    processor = TransactionProcessor(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )

    return bank, audit_log, risk_analyzer, queue, processor


def create_clients(bank: Bank):
    clients = [
        Client(
            full_name="Dias Flow",
            age=21,
            contacts={"phone": "+77001112233", "email": "dias@mail.com"}
        ),
        Client(
            full_name="Alex Ivanov",
            age=30,
            contacts={"phone": "+77004445566", "email": "alex@mail.com"}
        ),
        Client(
            full_name="Maria Petrova",
            age=27,
            contacts={"phone": "+77007778899", "email": "maria@mail.com"}
        ),
        Client(
            full_name="Ivan Sokolov",
            age=35,
            contacts={"phone": "+77005556677", "email": "ivan@mail.com"}
        ),
        Client(
            full_name="Alina Kim",
            age=24,
            contacts={"phone": "+77009990011", "email": "alina@mail.com"}
        ),
        Client(
            full_name="Sergey Volkov",
            age=40,
            contacts={"phone": "+77008887766", "email": "sergey@mail.com"}
        ),
    ]

    for client in clients:
        bank.add_client(client)

    return clients


def create_accounts(bank: Bank, clients: list[Client]):
    accounts = []

    account_definitions = [
        SavingsAccount(
            owner=clients[0].full_name,
            balance=5000,
            currency=Currency.USD,
            min_balance=500,
            interest_rate=0.02
        ),
        PremiumAccount(
            owner=clients[0].full_name,
            balance=3000,
            currency=Currency.EUR,
            overdraft_limit=4000,
            transaction_fee=20
        ),
        InvestmentAccount(
            owner=clients[1].full_name,
            balance=7000,
            currency=Currency.USD,
            portfolio={"stocks": 10000, "bonds": 3000, "etf": 5000}
        ),
        SavingsAccount(
            owner=clients[1].full_name,
            balance=2000,
            currency=Currency.KZT,
            min_balance=200,
            interest_rate=0.01
        ),
        PremiumAccount(
            owner=clients[2].full_name,
            balance=2500,
            currency=Currency.USD,
            overdraft_limit=5000,
            transaction_fee=15
        ),
        InvestmentAccount(
            owner=clients[2].full_name,
            balance=8000,
            currency=Currency.EUR,
            portfolio={"stocks": 15000, "bonds": 5000, "etf": 4000}
        ),
        SavingsAccount(
            owner=clients[3].full_name,
            balance=4500,
            currency=Currency.CNY,
            min_balance=300,
            interest_rate=0.015
        ),
        PremiumAccount(
            owner=clients[3].full_name,
            balance=1200,
            currency=Currency.USD,
            overdraft_limit=2500,
            transaction_fee=25
        ),
        InvestmentAccount(
            owner=clients[4].full_name,
            balance=6000,
            currency=Currency.USD,
            portfolio={"stocks": 9000, "bonds": 4000, "etf": 3500}
        ),
        SavingsAccount(
            owner=clients[4].full_name,
            balance=1800,
            currency=Currency.RUB,
            min_balance=150,
            interest_rate=0.01
        ),
        PremiumAccount(
            owner=clients[5].full_name,
            balance=2200,
            currency=Currency.EUR,
            overdraft_limit=3500,
            transaction_fee=18
        ),
        SavingsAccount(
            owner=clients[5].full_name,
            balance=3900,
            currency=Currency.USD,
            min_balance=400,
            interest_rate=0.02
        ),
    ]

    client_to_accounts = {
        clients[0].client_id: [account_definitions[0], account_definitions[1]],
        clients[1].client_id: [account_definitions[2], account_definitions[3]],
        clients[2].client_id: [account_definitions[4], account_definitions[5]],
        clients[3].client_id: [account_definitions[6], account_definitions[7]],
        clients[4].client_id: [account_definitions[8], account_definitions[9]],
        clients[5].client_id: [account_definitions[10], account_definitions[11]],
    }

    for client_id, client_accounts in client_to_accounts.items():
        for account in client_accounts:
            bank.open_account(client_id, account)
            accounts.append(account)

    return accounts

def create_transactions(accounts: list):
    transactions = []

    # Для удобства дадим короткие имена
    acc1 = accounts[0]
    acc2 = accounts[1]
    acc3 = accounts[2]
    acc4 = accounts[3]
    acc5 = accounts[4]
    acc6 = accounts[5]
    acc7 = accounts[6]
    acc8 = accounts[7]
    acc9 = accounts[8]
    acc10 = accounts[9]
    acc11 = accounts[10]
    acc12 = accounts[11]

    # Нормальные транзакции
    normal_transactions = [
        Transaction(TransactionType.TRANSFER, 150, Currency.USD, sender=acc1, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 200, Currency.EUR, sender=acc2, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 120, Currency.USD, sender=acc3, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 300, Currency.KZT, sender=acc4, receiver=acc10),
        Transaction(TransactionType.TRANSFER, 250, Currency.USD, sender=acc5, receiver=acc9),
        Transaction(TransactionType.TRANSFER, 400, Currency.EUR, sender=acc6, receiver=acc11),
        Transaction(TransactionType.TRANSFER, 180, Currency.CNY, sender=acc7, receiver=acc12),
        Transaction(TransactionType.TRANSFER, 220, Currency.USD, sender=acc8, receiver=acc6),
        Transaction(TransactionType.TRANSFER, 160, Currency.USD, sender=acc9, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 140, Currency.RUB, sender=acc10, receiver=acc4),
        Transaction(TransactionType.TRANSFER, 190, Currency.EUR, sender=acc11, receiver=acc8),
        Transaction(TransactionType.TRANSFER, 210, Currency.USD, sender=acc12, receiver=acc7),
    ]

    # Подозрительные транзакции
    suspicious_transactions = [
        Transaction(TransactionType.TRANSFER, 7000, Currency.USD, sender=acc1, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 6500, Currency.USD, sender=acc3, receiver=acc10),
        Transaction(TransactionType.TRANSFER, 5200, Currency.EUR, sender=acc6, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 300, Currency.USD, sender=acc1, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 350, Currency.USD, sender=acc1, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 400, Currency.USD, sender=acc1, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 450, Currency.USD, sender=acc1, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 500, Currency.USD, sender=acc1, receiver=acc5),
    ]

    # Ошибочные транзакции
    failed_transactions = [
        Transaction(TransactionType.TRANSFER, 20000, Currency.USD, sender=acc1, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 15000, Currency.EUR, sender=acc2, receiver=acc6),
        Transaction(TransactionType.TRANSFER, 50000, Currency.KZT, sender=acc4, receiver=acc10),
        Transaction(TransactionType.TRANSFER, 9000, Currency.CNY, sender=acc7, receiver=acc12),
        Transaction(TransactionType.TRANSFER, 25000, Currency.RUB, sender=acc10, receiver=acc4),
    ]

    # Ещё обычные, чтобы выйти на хорошее количество
    extra_transactions = [
        Transaction(TransactionType.TRANSFER, 130, Currency.USD, sender=acc5, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 170, Currency.USD, sender=acc9, receiver=acc3),
        Transaction(TransactionType.TRANSFER, 260, Currency.EUR, sender=acc11, receiver=acc6),
        Transaction(TransactionType.TRANSFER, 110, Currency.USD, sender=acc8, receiver=acc2),
        Transaction(TransactionType.TRANSFER, 145, Currency.CNY, sender=acc7, receiver=acc9),
        Transaction(TransactionType.TRANSFER, 230, Currency.USD, sender=acc12, receiver=acc1),
        Transaction(TransactionType.TRANSFER, 310, Currency.USD, sender=acc3, receiver=acc8),
        Transaction(TransactionType.TRANSFER, 280, Currency.EUR, sender=acc2, receiver=acc11),
        Transaction(TransactionType.TRANSFER, 95, Currency.USD, sender=acc5, receiver=acc6),
        Transaction(TransactionType.TRANSFER, 125, Currency.USD, sender=acc9, receiver=acc12),
        Transaction(TransactionType.TRANSFER, 175, Currency.USD, sender=acc1, receiver=acc8),
        Transaction(TransactionType.TRANSFER, 205, Currency.EUR, sender=acc6, receiver=acc5),
        Transaction(TransactionType.TRANSFER, 155, Currency.RUB, sender=acc10, receiver=acc11),
        Transaction(TransactionType.TRANSFER, 240, Currency.USD, sender=acc3, receiver=acc7),
        Transaction(TransactionType.TRANSFER, 115, Currency.USD, sender=acc8, receiver=acc4),
    ]

    transactions.extend(normal_transactions)
    transactions.extend(suspicious_transactions)
    transactions.extend(failed_transactions)
    transactions.extend(extra_transactions)

    return transactions


def enqueue_transactions(queue: TransactionQueue, transactions: list[Transaction]):
    for index, transaction in enumerate(transactions):
        if index % 10 == 0:
            queue.add_transaction(transaction, priority=True)
            print(f"[QUEUE] Приоритетная транзакция добавлена: {transaction.transaction_id}")
        elif index % 13 == 0:
            queue.add_transaction(transaction, delayed=True)
            print(f"[QUEUE] Отложенная транзакция добавлена: {transaction.transaction_id}")
        else:
            queue.add_transaction(transaction)
            print(f"[QUEUE] Обычная транзакция добавлена: {transaction.transaction_id}")


def process_all_transactions(queue: TransactionQueue, processor: TransactionProcessor):
    processed_transactions = []

    while True:
        transaction = queue.get_next_transaction()
        if transaction is None:
            break

        result = processor.process_with_retry(transaction)
        processed_transactions.append(result)

        if result.status == TransactionStatus.COMPLETED:
            print(f"[SUCCESS] Транзакция выполнена: {result.transaction_id}")
        else:
            print(f"[FAILED] Транзакция отклонена: {result.transaction_id}")
            print(f"         Причина: {result.failure_reason}")

    return processed_transactions


def show_client_accounts(bank: Bank, client: Client):
    print(f"=== СЧЕТА КЛИЕНТА: {client.full_name} ===")
    accounts = bank.search_accounts(client.client_id)
    for account in accounts:
        print(account)
    print()


def show_client_transaction_history(processed_transactions: list[Transaction], client: Client):
    print(f"=== ИСТОРИЯ ТРАНЗАКЦИЙ КЛИЕНТА: {client.full_name} ===")
    found = False

    for transaction in processed_transactions:
        sender_owner = transaction.sender.owner if transaction.sender else None
        receiver_owner = transaction.receiver.owner if transaction.receiver else None

        if sender_owner == client.full_name or receiver_owner == client.full_name:
            print(transaction)
            found = True

    if not found:
        print("Транзакции не найдены")

    print()


def show_suspicious_operations_for_client(risk_analyzer: RiskAnalyzer, client: Client):
    print(f"=== ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ КЛИЕНТА: {client.full_name} ===")
    found = False

    for item in risk_analyzer.get_suspicious_operations_report():
        transaction = item["transaction"]
        if transaction.sender and transaction.sender.owner == client.full_name:
            print(
                f"{transaction.transaction_id} | "
                f"{item['risk_level'].value} | "
                f"score={item['risk_score']} | "
                f"reasons={', '.join(item['reasons'])}"
            )
            found = True

    if not found:
        print("Подозрительные операции не найдены")

    print()


def print_reports(
    bank: Bank,
    processor: TransactionProcessor,
    risk_analyzer: RiskAnalyzer,
    audit_log: AuditLog,
    processed_transactions: list[Transaction]
):
    print("=== ТОП-3 КЛИЕНТОВ ===")
    ranking = bank.get_clients_ranking()[:3]
    for index, (full_name, total_balance) in enumerate(ranking, start=1):
        print(f"{index}. {full_name}: {total_balance:.2f}")
    print()

    print("=== СТАТИСТИКА ТРАНЗАКЦИЙ ===")
    total_count = len(processed_transactions)
    completed_count = sum(1 for tx in processed_transactions if tx.status == TransactionStatus.COMPLETED)
    failed_count = sum(1 for tx in processed_transactions if tx.status == TransactionStatus.FAILED)
    suspicious_count = len(risk_analyzer.get_suspicious_operations_report())

    print(f"Всего обработано: {total_count}")
    print(f"Успешно: {completed_count}")
    print(f"С ошибкой: {failed_count}")
    print(f"Подозрительных: {suspicious_count}")
    print()

    print("=== ОБЩИЙ БАЛАНС БАНКА ===")
    print(f"{bank.get_total_balance():.2f}")
    print()

    print("=== СТАТИСТИКА ОШИБОК ===")
    error_stats = processor.get_error_statistics()
    if error_stats:
        for reason, count in error_stats.items():
            print(f"{reason}: {count}")
    else:
        print("Ошибок нет")
    print()

    print("=== АУДИТ WARNING ===")
    warning_logs = audit_log.filter_logs(AuditLevel.WARNING)
    if warning_logs:
        for log in warning_logs:
            print(f"[{log['time']}] [{log['level'].value}] {log['message']}")
    else:
        print("WARNING записей нет")
    print()

    print("=== АУДИТ CRITICAL ===")
    critical_logs = audit_log.filter_logs(AuditLevel.CRITICAL)
    if critical_logs:
        for log in critical_logs:
            print(f"[{log['time']}] [{log['level'].value}] {log['message']}")
    else:
        print("CRITICAL записей нет")
    print()

def main():
    bank, audit_log, risk_analyzer, queue, processor = create_bank_system()
    clients = create_clients(bank)
    accounts = create_accounts(bank, clients)

    print("=== БАНК СОЗДАН ===")
    print(bank.name)
    print()

    print("=== КЛИЕНТЫ ===")
    for client in clients:
        print(client)
    print()

    print("=== СЧЕТА ===")
    for account in accounts:
        print(account)
    print()

    transactions = create_transactions(accounts)

    print("=== ДОБАВЛЕНИЕ ТРАНЗАКЦИЙ В ОЧЕРЕДЬ ===")
    enqueue_transactions(queue, transactions)
    print()

    print("=== ОБРАБОТКА ТРАНЗАКЦИЙ ===")
    processed_transactions = process_all_transactions(queue, processor)
    print()

    print("=== ОТЛОЖЕННЫЕ ТРАНЗАКЦИИ ===")
    for delayed_transaction in queue.delayed_queue:
        print(delayed_transaction)
    print()

    show_client_accounts(bank, clients[0])
    show_client_transaction_history(processed_transactions, clients[0])
    show_suspicious_operations_for_client(risk_analyzer, clients[0])

    print_reports(
        bank=bank,
        processor=processor,
        risk_analyzer=risk_analyzer,
        audit_log=audit_log,
        processed_transactions=processed_transactions
    )

    report_builder = ReportBuilder(
        bank=bank,
        processor=processor,
        risk_analyzer=risk_analyzer,
        audit_log=audit_log,
        processed_transactions=processed_transactions
    )

    client_report = report_builder.build_client_report(clients[0])
    bank_report = report_builder.build_bank_report()
    risk_report = report_builder.build_risk_report()

    report_builder.export_to_json(client_report, "client_report.json")
    report_builder.export_to_json(bank_report, "bank_report.json")
    report_builder.export_to_json(risk_report, "risk_report.json")

    report_builder.export_to_csv(client_report, "client_report.csv")
    report_builder.export_to_csv(bank_report, "bank_report.csv")
    report_builder.export_to_csv(risk_report, "risk_report.csv")

    report_builder.export_to_csv(client_report["accounts"], "client_accounts.csv")
    report_builder.export_to_csv(client_report["suspicious_operations"], "client_suspicious_operations.csv")
    report_builder.export_to_csv(risk_report["operations"], "risk_operations.csv")

    report_builder.save_charts(clients[0])

    print("=== DAY 7 REPORTS ===")
    print("Отчёты и графики сохранены в папку reports_output")
    print()

if __name__ == "__main__":
    main()