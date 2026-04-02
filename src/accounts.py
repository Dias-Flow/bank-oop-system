from abc import ABC, abstractmethod
from uuid import uuid4
from enums import AccountStatus, Currency


class AbstractAccount(ABC):
    def __init__(self, account_id: str, owner: str, balance: float, status: AccountStatus):
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.status = status

    @abstractmethod
    def deposit(self, amount: float):
        pass

    @abstractmethod
    def withdraw(self, amount: float):
        pass

    @abstractmethod
    def get_account_info(self):
        pass


class BankAccount(AbstractAccount):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.RUB,
        account_id: str | None = None
    ):

        if not owner or not owner.strip():
            raise ValueError("Владелец счета не может быть пустым")

        if balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным")

        if not isinstance(status, AccountStatus):
            raise ValueError("Некорректный статус счета")

        if not isinstance(currency, Currency):
            raise ValueError("Некорректная валюта счета")

        if account_id is None:
            account_id = str(uuid4())[:8]

        super().__init__(
            account_id=account_id,
            owner=owner,
            balance=balance,
            status=status
        )


        self.currency = currency

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self._balance,
            "status": self.status.value,
            "currency": self.currency.value
        }