from accounts import BankAccount
from enums import AccountStatus, Currency
from exceptions import AccountFrozenError


def main():
    # Создаем активный счет
    active_account = BankAccount(
        owner="Dias",
        balance=1000,
        currency=Currency.USD
    )

    print("Активный счет создан:")
    print(active_account)
    print()

    # Пополнение счета
    active_account.deposit(500)
    print("После пополнения:")
    print(active_account)
    print()

    # Снятие денег
    active_account.withdraw(300)
    print("После снятия:")
    print(active_account)
    print()

    # Создаем замороженный счет
    frozen_account = BankAccount(
        owner="Alex",
        balance=2000,
        status=AccountStatus.FROZEN,
        currency=Currency.EUR
    )

    print("Замороженный счет создан:")
    print(frozen_account)
    print()

    # Попытка операции с замороженным счетом
    try:
        frozen_account.deposit(100)
    except AccountFrozenError as e:
        print("Ошибка операции:")
        print(e)


if __name__ == "__main__":
    main()