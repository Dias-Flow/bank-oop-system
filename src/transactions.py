from datetime import datetime
from uuid import uuid4

from enums import Currency, TransactionType, TransactionStatus, AccountStatus, AuditLevel, RiskLevel
from audit import AuditLog, RiskAnalyzer


class Transaction:

    def __init__(
        self,
        transaction_type: TransactionType,
        amount: float,
        currency: Currency,
        sender=None,
        receiver=None,
        fee: float = 0.0,
        transaction_id: str | None = None
    ):
        if not isinstance(transaction_type, TransactionType):
            raise ValueError("Некорректный тип транзакции")

        if amount <= 0:
            raise ValueError("Сумма транзакции должна быть больше нуля")

        if not isinstance(currency, Currency):
            raise ValueError("Некорректная валюта транзакции")

        if fee < 0:
            raise ValueError("Комиссия не может быть отрицательной")

        if transaction_id is None:
            transaction_id = str(uuid4())[:8]

        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.fee = fee
        self.sender = sender
        self.receiver = receiver
        self.status = TransactionStatus.PENDING
        self.failure_reason = None
        self.created_at = datetime.now()
        self.processed_at = None

    def mark_processing(self):
        self.status = TransactionStatus.PROCESSING

    def mark_completed(self):
        self.status = TransactionStatus.COMPLETED
        self.processed_at = datetime.now()

    def mark_failed(self, reason: str):
        self.status = TransactionStatus.FAILED
        self.failure_reason = reason
        self.processed_at = datetime.now()

    def mark_cancelled(self, reason: str = "Операция отменена"):
        self.status = TransactionStatus.CANCELLED
        self.failure_reason = reason
        self.processed_at = datetime.now()

    def __str__(self):
        sender_id = self.sender.account_id if self.sender else "None"
        receiver_id = self.receiver.account_id if self.receiver else "None"

        return (
            f"Transaction | ID: {self.transaction_id} | "
            f"type: {self.transaction_type.value} | "
            f"amount: {self.amount:.2f} {self.currency.value} | "
            f"fee: {self.fee:.2f} | "
            f"sender: {sender_id} | receiver: {receiver_id} | "
            f"status: {self.status.value}"
        )

class TransactionQueue:
    def __init__(self):
        self.priority_queue = []
        self.regular_queue = []
        self.delayed_queue = []

    def add_transaction(
        self,
        transaction: Transaction,
        priority: bool = False,
        delayed: bool = False
    ):
        if not isinstance(transaction, Transaction):
            raise ValueError("Можно добавлять только объект Transaction")

        if delayed:
            self.delayed_queue.append(transaction)
        elif priority:
            self.priority_queue.append(transaction)
        else:
            self.regular_queue.append(transaction)

    def get_next_transaction(self):
        if self.priority_queue:
            return self.priority_queue.pop(0)

        if self.regular_queue:
            return self.regular_queue.pop(0)

        return None

    def cancel_transaction(self, transaction_id: str):
        for queue in [self.priority_queue, self.regular_queue, self.delayed_queue]:
            for transaction in queue:
                if transaction.transaction_id == transaction_id:
                    transaction.mark_cancelled("Отменено пользователем")
                    queue.remove(transaction)
                    return transaction

        return None

class TransactionProcessor:

    def __init__(self, bank, audit_log=None, risk_analyzer=None):
        self.processed_transactions = None
        self.bank = bank
        self.retry_limit = 3
        self.failed_transactions = []
        self.audit_log = audit_log if audit_log is not None else AuditLog()
        self.risk_analyzer = risk_analyzer if risk_analyzer is not None else RiskAnalyzer()

    def process_transaction(self, transaction: Transaction):
        try:
            transaction.mark_processing()

            risk_result = self.risk_analyzer.analyze_transaction(transaction)
            risk_level = risk_result["risk_level"]
            risk_reasons = risk_result["reasons"]

            self.audit_log.log_event(
                AuditLevel.INFO,
                f"Начата обработка транзакции {transaction.transaction_id} "
                f"с уровнем риска {risk_level.value}"
            )

            if risk_level == RiskLevel.HIGH:
                reason_text = ", ".join(risk_reasons) if risk_reasons else "Высокий уровень риска"
                transaction.mark_failed(f"Операция заблокирована из-за высокого риска: {reason_text}")
                self.failed_transactions.append(transaction)

                self.audit_log.log_event(
                    AuditLevel.CRITICAL,
                    f"Транзакция {transaction.transaction_id} заблокирована. Причины: {reason_text}"
                )

                return transaction

            if risk_level == RiskLevel.MEDIUM:
                self.audit_log.log_event(
                    AuditLevel.WARNING,
                    f"Подозрительная транзакция {transaction.transaction_id}. "
                    f"Причины: {', '.join(risk_reasons)}"
                )

            if transaction.transaction_type != TransactionType.TRANSFER:
                raise ValueError("Сейчас поддерживаются только переводы")

            sender = transaction.sender
            receiver = transaction.receiver

            if sender is None or receiver is None:
                raise ValueError("Для перевода нужны отправитель и получатель")

            if sender.status == AccountStatus.FROZEN or receiver.status == AccountStatus.FROZEN:
                raise ValueError("Переводы с замороженными счетами запрещены")

            transaction.fee = self.calculate_fee(transaction)
            total_amount = transaction.amount + transaction.fee

            if sender.__class__.__name__ != "PremiumAccount" and sender._balance < total_amount:
                raise ValueError("Недостаточно средств для перевода")

            sender.withdraw(total_amount)

            received_amount = self.convert_currency(
                transaction.amount,
                transaction.currency,
                receiver.currency
            )

            receiver.deposit(received_amount)

            transaction.mark_completed()

            self.audit_log.log_event(
                AuditLevel.INFO,
                f"Транзакция {transaction.transaction_id} успешно выполнена"
            )

            return transaction

        except Exception as error:
            transaction.mark_failed(str(error))

            if transaction not in self.failed_transactions:
                self.failed_transactions.append(transaction)

            self.audit_log.log_event(
                AuditLevel.CRITICAL,
                f"Ошибка транзакции {transaction.transaction_id}: {str(error)}"
            )

            return transaction


    def calculate_fee(self, transaction: Transaction):
        sender = transaction.sender
        receiver = transaction.receiver

        if sender is None or receiver is None:
            return 0.0

        if sender.owner != receiver.owner:
            return round(transaction.amount * 0.02, 2)

        return 0.0

    def convert_currency(self, amount: float, from_currency: Currency, to_currency: Currency):
        if from_currency == to_currency:
            return amount

        rates_to_usd = {
            Currency.USD: 1.0,
            Currency.EUR: 1.08,
            Currency.RUB: 0.011,
            Currency.KZT: 0.0021,
            Currency.CNY: 0.14,
        }

        amount_in_usd = amount * rates_to_usd[from_currency]
        converted_amount = amount_in_usd / rates_to_usd[to_currency]
        return round(converted_amount, 2)

    def process_with_retry(self, transaction: Transaction):
        last_error = None

        for _ in range(self.retry_limit):
            result = self.process_transaction(transaction)

            if result.status == TransactionStatus.COMPLETED:
                return result

            last_error = result.failure_reason

        transaction.mark_failed(f"Транзакция не выполнена после {self.retry_limit} попыток: {last_error}")
        if transaction not in self.failed_transactions:
            self.failed_transactions.append(transaction)

        return transaction

    def get_error_statistics(self):
        stats = {}

        for transaction in self.failed_transactions:
            reason = transaction.failure_reason or "Неизвестная ошибка"
            stats[reason] = stats.get(reason, 0) + 1

        return stats