from account_types import SavingsAccount, PremiumAccount, InvestmentAccount
from enums import Currency
from exceptions import InsufficientFundsError


def main():
    print("===== SAVINGS ACCOUNT =====")
    savings = SavingsAccount(
        owner="Dias",
        balance=2000,
        currency=Currency.USD,
        min_balance=500,
        interest_rate=0.02
    )
    print(savings)
    print("Информация:", savings.get_account_info())

    savings.apply_monthly_interest()
    print("После начисления процентов:")
    print(savings)

    try:
        savings.withdraw(1700)
    except InsufficientFundsError as e:
        print("Ошибка снятия:", e)

    savings.withdraw(1000)
    print("После допустимого снятия:")
    print(savings)
    print()

    print("===== PREMIUM ACCOUNT =====")
    premium = PremiumAccount(
        owner="Alex",
        balance=300,
        currency=Currency.EUR,
        overdraft_limit=1000,
        transaction_fee=15
    )
    print(premium)
    print("Информация:", premium.get_account_info())

    premium.withdraw(500)
    print("После снятия с овердрафтом:")
    print(premium)

    premium.deposit(200)
    print("После пополнения:")
    print(premium)
    print()

    print("===== INVESTMENT ACCOUNT =====")
    investment = InvestmentAccount(
        owner="Maria",
        balance=1500,
        portfolio={
            "stocks": 5000,
            "bonds": 2000,
            "etf": 3000
        }
    )
    print(investment)
    print("Информация:", investment.get_account_info())
    print("Прогноз роста портфеля на год:")
    print(investment.project_yearly_growth())

    investment.withdraw(500)
    print("После снятия денег с денежного баланса:")
    print(investment)


if __name__ == "__main__":
    main()