from uuid import uuid4

from accounts import BankAccount
from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import AccountStatus
from datetime import datetime


class Client:
    def __init__(
        self,
        full_name: str,
        age: int,
        contacts: dict,
        client_id: str | None = None,
        status: str = "active"
    ):

        if not full_name or not full_name.strip():
            raise ValueError("ФИО клиента не может быть пустым")

        if age < 18:
            raise ValueError("Клиент должен быть старше 18 лет")

        if not isinstance(contacts, dict):
            raise ValueError("Контакты должны быть словарем")

        if client_id is None:
            client_id = str(uuid4())[:8]

        self.client_id = client_id
        self.full_name = full_name
        self.age = age
        self.contacts = contacts
        self.status = status
        self.accounts = []

    def add_account(self, account_id: str):
        if account_id not in self.accounts:
            self.accounts.append(account_id)

    def remove_account(self, account_id: str):
        if account_id in self.accounts:
            self.accounts.remove(account_id)

    def get_accounts(self):
        return self.accounts

    def __str__(self):
        return (
            f"Client | {self.full_name} | ID: {self.client_id} | "
            f"status: {self.status} | accounts: {len(self.accounts)}"
        )

class Bank:
    def __init__(self, name: str):
        if not name or not name.strip():
            raise ValueError("Название банка не может быть пустым")

        self.name = name
        self.clients = {}
        self.accounts = {}
        self.failed_login_attempts = {}
        self.blocked_clients = set()
        self.suspicious_actions = []

    def add_client(self, client: Client):
        if client.client_id in self.clients:
            raise ValueError("Клиент с таким ID уже существует")

        self.clients[client.client_id] = client

    def open_account(self, client_id: str, account):
        if client_id not in self.clients:
            raise ValueError("Клиент не найден")

        if not isinstance(account, BankAccount):
            raise ValueError("Неверный тип счета")

        account_id = account.account_id

        if account_id in self.accounts:
            raise ValueError("Счет уже существует в банке")

        self.accounts[account_id] = account

        client = self.clients[client_id]
        client.add_account(account_id)

        return account

    def close_account(self, client_id: str, account_id: str):
        if client_id not in self.clients:
            raise ValueError("Клиент не найден")

        if account_id not in self.accounts:
            raise ValueError("Счет не найден")

        client = self.clients[client_id]
        account = self.accounts[account_id]

        if account_id not in client.accounts:
            raise ValueError("Этот счет не принадлежит клиенту")

        account.status = AccountStatus.CLOSED
        client.remove_account(account_id)

    def freeze_account(self, account_id: str):
        if account_id not in self.accounts:
            raise ValueError("Счет не найден")

        account = self.accounts[account_id]
        account.status = AccountStatus.FROZEN

    def unfreeze_account(self, account_id: str):
        if account_id not in self.accounts:
            raise ValueError("Счет не найден")

        account = self.accounts[account_id]
        account.status = AccountStatus.ACTIVE


    def authenticate_client(self, client_id: str):
        if client_id in self.blocked_clients:
            raise ValueError("Клиент заблокирован")

        if client_id not in self.clients:
            current_attempts = self.failed_login_attempts.get(client_id, 0) + 1
            self.failed_login_attempts[client_id] = current_attempts

            if current_attempts >= 3:
                self.blocked_clients.add(client_id)
                self.suspicious_actions.append(
                    f"Клиент с ID {client_id} заблокирован после 3 неудачных попыток входа"
                )

            raise ValueError("Неверный ID клиента")

        self.failed_login_attempts[client_id] = 0
        return self.clients[client_id]

    def search_accounts(self, client_id: str):
        if client_id not in self.clients:
            raise ValueError("Клиент не найден")

        client = self.clients[client_id]
        return [
            self.accounts[account_id]
            for account_id in client.get_accounts()
            if account_id in self.accounts
        ]

    def get_total_balance(self):
        total = 0.0

        for account in self.accounts.values():
            total += account._balance

        return total

    def get_clients_ranking(self):
        ranking = []

        for client in self.clients.values():
            total_balance = 0.0

            for account_id in client.get_accounts():
                if account_id in self.accounts:
                    total_balance += self.accounts[account_id]._balance

            ranking.append((client.full_name, total_balance))

        ranking.sort(key=lambda item: item[1], reverse=True)
        return ranking

    def _check_operation_time(self):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 5:
            self.suspicious_actions.append(
                "Попытка выполнить операцию в запрещенное ночное время"
            )
            raise ValueError("Операции запрещены с 00:00 до 05:00")

