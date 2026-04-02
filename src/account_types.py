from accounts import BankAccount
from enums import AccountStatus, Currency
from exceptions import InsufficientFundsError

class SavingsAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.RUB,
        account_id: str | None = None,
        min_balance: float = 0.0,
        interest_rate: float = 0.01
    ):
        super().__init__(
            owner=owner,
            balance=balance,
            status=status,
            currency=currency,
            account_id=account_id
        )

        if min_balance < 0:
            raise ValueError("Минимальный остаток не может быть отрицательным")

        if interest_rate < 0:
            raise ValueError("Процентная ставка не может быть отрицательной")

        self.min_balance = min_balance
        self.interest_rate = interest_rate

    def withdraw(self, amount: float):
        self._check_account_status()
        self._validate_amount(amount)

        if self._balance - amount < self.min_balance:
            raise InsufficientFundsError(
                "Нельзя снять средства ниже минимального остатка"
            )

        self._balance -= amount

    def apply_monthly_interest(self):
        interest = self._balance * self.interest_rate
        self._balance += interest

class PremiumAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.RUB,
        account_id: str | None = None,
        overdraft_limit: float = 1000.0,
        transaction_fee: float = 10.0
    ):
        super().__init__(
            owner=owner,
            balance=balance,
            status=status,
            currency=currency,
            account_id=account_id
        )

        if overdraft_limit < 0:
            raise ValueError("Лимит овердрафта не может быть отрицательным")

        if transaction_fee < 0:
            raise ValueError("Комиссия не может быть отрицательной")

        self.overdraft_limit = overdraft_limit
        self.transaction_fee = transaction_fee

    def withdraw(self, amount: float):
        self._check_account_status()
        self._validate_amount(amount)

        total_amount = amount + self.transaction_fee

        if self._balance - total_amount < -self.overdraft_limit:
            raise InsufficientFundsError(
                "Превышен лимит овердрафта для премиум-счета"
            )

        self._balance -= total_amount

    def get_account_info(self):
        info = super().get_account_info()
        info["overdraft_limit"] = self.overdraft_limit
        info["transaction_fee"] = self.transaction_fee
        info["account_type"] = "PremiumAccount"
        return info

    def __str__(self):
        last_four = self.account_id[-4:]
        return (
            f"PremiumAccount | {self.owner} | ****{last_four} | "
            f"{self.status.value} | {self._balance:.2f} {self.currency.value} | "
            f"overdraft={self.overdraft_limit:.2f} | fee={self.transaction_fee:.2f}"
        )

class InvestmentAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
        account_id: str | None = None,
        portfolio: dict | None = None
    ):
        super().__init__(
            owner=owner,
            balance=balance,
            status=status,
            currency=currency,
            account_id=account_id
        )

        if portfolio is None:
            portfolio = {
                "stocks": 0.0,
                "bonds": 0.0,
                "etf": 0.0
            }

        if not isinstance(portfolio, dict):
            raise ValueError("Портфель должен быть словарем")

        required_assets = {"stocks", "bonds", "etf"}
        if set(portfolio.keys()) != required_assets:
            raise ValueError("Портфель должен содержать stocks, bonds и etf")

        for asset_name, asset_value in portfolio.items():
            if not isinstance(asset_value, (int, float)) or asset_value < 0:
                raise ValueError(
                    f"Значение актива {asset_name} должно быть неотрицательным числом"
                )

        self.portfolio = portfolio

    def project_yearly_growth(self):
        growth_rates = {
            "stocks": 0.12,
            "bonds": 0.05,
            "etf": 0.08
        }

        projected_portfolio = {}

        for asset_name, asset_value in self.portfolio.items():
            projected_value = asset_value * (1 + growth_rates[asset_name])
            projected_portfolio[asset_name] = round(projected_value, 2)

        return projected_portfolio

    def get_account_info(self):
        info = super().get_account_info()
        info["portfolio"] = self.portfolio
        info["portfolio_total"] = sum(self.portfolio.values())
        info["account_type"] = "InvestmentAccount"
        return info

    def __str__(self):
        last_four = self.account_id[-4:]
        portfolio_total = sum(self.portfolio.values())
        return (
            f"InvestmentAccount | {self.owner} | ****{last_four} | "
            f"{self.status.value} | {self._balance:.2f} {self.currency.value} | "
            f"portfolio={portfolio_total:.2f}"
        )

    def withdraw(self, amount: float):
        self._check_account_status()
        self._validate_amount(amount)

        if amount > self._balance:
            raise InsufficientFundsError(
                "Недостаточно денежных средств на инвестиционном счете"
            )

        self._balance -= amount