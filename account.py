from datetime import datetime


class Account:
    def __init__(self, owner_name, acc_no, balance=0):
        if not isinstance(owner_name, str) or not owner_name.strip():
            raise ValueError("Owner name must be a non-empty string.")

        if not isinstance(acc_no, str) or not acc_no.strip():
            raise ValueError("Account number must be a non-empty string.")

        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            raise TypeError("Balance must be a number.")

        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        self.owner_name = owner_name
        self.acc_no = acc_no
        self._balance = balance
        self.transaction_history = []

    def _validate_amount(self, amount):
        """Validate that amount is a numeric value (not bool)."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")

    @property
    def balance(self):
        """Read-only access to balance."""
        return self._balance

    def deposit(self, amount):
        """Deposit money into the account."""
        self._validate_amount(amount)

        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._balance += amount

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
        """
        Transfer money from this account to another account.
        """

        # Destination must be an Account (or subclass).
        if not isinstance(other_account, Account):
            raise TypeError("Destination must be an Account.")

        # Reject self-transfer because it has no useful effect and only creates
        # unnecessary transactions.
        if other_account is self:
            raise ValueError("Cannot transfer to the same account.")

        # Withdraw from source account first.
        self.withdraw(amount)

        try:
            # Deposit into destination account.
            other_account.deposit(amount)

        # Catch validation/runtime errors from deposit(), rollback, then re-raise.
        except (TypeError, ValueError):
            self.deposit(amount)
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
        self._balance = balance
        self.transaction_history = transaction_history