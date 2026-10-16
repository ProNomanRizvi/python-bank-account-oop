from copy import deepcopy
from datetime import datetime
from math import isfinite


class Account:
    def __init__(self, owner_name, acc_no, balance=0):
        if not isinstance(owner_name, str) or not owner_name.strip():
            raise ValueError("Owner name must be a non-empty string.")

        if not isinstance(acc_no, str) or not acc_no.strip():
            raise ValueError("Account number must be a non-empty string.")

        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            raise TypeError("Balance must be a number.")

        if isinstance(balance, float) and not isfinite(balance):
            raise ValueError("Balance must be finite.")

        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        self.owner_name = owner_name
        self.acc_no = acc_no
        self._balance = balance
        self.transaction_history = []

    def _validate_amount(self, amount):
        """Validate that amount is numeric and finite (not bool)."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if isinstance(amount, float) and not isfinite(amount):
            raise ValueError("Amount must be finite.")

    @property
    def balance(self):
        """Read-only access to balance."""
        return self._balance

    def deposit(self, amount):
        """Deposit money into the account."""
        self._validate_amount(amount)

        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        new_balance = self._balance + amount
        if isinstance(new_balance, float) and not isfinite(new_balance):
            raise ValueError("Resulting balance must be finite.")
        self._balance = new_balance

        self.transaction_history.append({
            "type": "deposit",
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "balance_after": self._balance
        })

    def withdraw(self, amount):
        """Withdraw money from the account."""
        self._validate_amount(amount)

        if amount < 0:
            raise ValueError("Withdrawal amount cannot be negative.")

        if amount == 0:
            raise ValueError("Withdrawal amount cannot be zero.")

        if amount > self._balance:
            raise ValueError("Insufficient balance.")

        self._balance -= amount

        self.transaction_history.append({
            "type": "withdraw",
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "balance_after": self._balance
        })

    def get_balance(self):
        """Return the current account balance."""
        return self._balance

    def __str__(self):
        return (
            f"Account Holder : {self.owner_name}\n"
            f"Account Number : {self.acc_no}\n"
            f"Current Balance: {self._balance}"
        )

    def transfer(self, other_account, amount):
        """Transfer between two Account objects with in-memory rollback."""
        if not isinstance(other_account, Account):
            raise TypeError("Destination must be an Account.")
        if other_account is self:
            raise ValueError("Cannot transfer to the same account.")

        source_balance = self._balance
        destination_balance = other_account._balance
        source_history = deepcopy(self.transaction_history)
        destination_history = deepcopy(other_account.transaction_history)

        try:
            self.withdraw(amount)
            other_account.deposit(amount)
        except Exception:
            # Restore both sides, including transaction logs, even if a subclass
            # changed its balance or history before raising.
            self._balance = source_balance
            self.transaction_history = source_history
            other_account._balance = destination_balance
            other_account.transaction_history = destination_history
            raise

    def to_dict(self):
        return {
            "type": "account",
            "owner_name": self.owner_name,
            "acc_no": self.acc_no,
            "balance": self._balance,
            "transaction_history": self.transaction_history,
        }

    def _restore_state(self, balance, transaction_history):
        self._validate_amount(balance)
        if balance < -getattr(self, "overdraft_limit", 0):
            raise ValueError("Stored balance exceeds allowed overdraft.")
        if not isinstance(transaction_history, list):
            raise ValueError("Stored transaction history must be a list.")
        self._balance = balance
        self.transaction_history = transaction_history
