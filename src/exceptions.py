class AccountError(Exception):
    """Базовая ошибка для всех ошибок, связанных со счетом."""
    pass


class AccountFrozenError(AccountError):
    """Ошибка: счет заморожен."""
    pass


class AccountClosedError(AccountError):
    """Ошибка: счет закрыт."""
    pass


class InvalidOperationError(AccountError):
    """Ошибка: операция недопустима."""
    pass


class InsufficientFundsError(AccountError):
    """Ошибка: недостаточно средств."""
    pass