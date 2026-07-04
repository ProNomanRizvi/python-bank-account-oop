class Account:
    def __init__(self, owner_name, acc_no, balance=0):
        self.owner_name = owner_name
        self.acc_no = acc_no
        self._balance = balance          # Encapsulated balance
        self.transaction_history = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if not isinstance(amount, (int, float)):
            raise TypeError("Deposit amount must be a number.")

        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._balance += amount
        self.transaction_history.append(f"Deposited: {amount}")

    def withdraw(self, amount):
        if not isinstance(amount, (int, float)):
            raise TypeError("Withdrawal amount must be a number.")

        if amount < 0:
            raise ValueError("Withdrawal amount cannot be negative.")

        if amount == 0:
            raise ValueError("Withdrawal amount cannot be zero.")

        if amount > self._balance:
            raise ValueError("Insufficient balance.")

        self._balance -= amount
        self.transaction_history.append(f"Withdrawn: {amount}")

    def get_balance(self):
        return self._balance

    def __str__(self):
        return (
            f"Account Holder : {self.owner_name}\n"
            f"Account Number : {self.acc_no}\n"
            f"Current Balance: {self._balance}"
        )