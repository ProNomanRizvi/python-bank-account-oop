from account import Account
from datetime import datetime


class CheckingAccount(Account):
    def __init__(self, owner_name, account_number, overdraft_limit):
        super().__init__(owner_name, account_number)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        self._validate_amount(amount)

        if amount < 0:
            raise ValueError("Withdrawal amount cannot be negative.")

        if amount == 0:
            raise ValueError("Withdrawal amount cannot be zero.")

        if amount > (self._balance + self.overdraft_limit):
            raise ValueError("Overdraft limit exceeded.")

        # Store balance before withdrawal
        balance_before = self._balance

        # Perform withdrawal
        self._balance -= amount

        # Store balance after withdrawal
        balance_after = self._balance

        # Determine transaction type
        if balance_before >= 0 and balance_after < 0:
            transaction_type = "overdraft"
        else:
            transaction_type = "withdraw"

        self.transaction_history.append({
            "type": transaction_type,
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "balance_after": self._balance
        })