from datetime import datetime
from uuid import uuid4

from enums import Currency, TransactionType, TransactionStatus


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