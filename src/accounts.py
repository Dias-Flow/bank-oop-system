from abc import ABC, abstractmethod

from enums import AccountStatus


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