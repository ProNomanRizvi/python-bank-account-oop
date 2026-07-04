from account import Account


class SavingsAccount(Account):
    def __init__(self, owner_name, account_number, interest_rate):
        super().__init__(owner_name, account_number)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self._balance * self.interest_rate

        # Nothing to add if interest is zero or negative
        if interest <= 0:
            return 0

        # Reuse deposit() for validation and balance update
        self.deposit(interest)

        # Change the last transaction type from "deposit" to "interest"
        # so the transaction history clearly shows where the money came from.
        if self.transaction_history:
            self.transaction_history[-1]["type"] = "interest"

        return interest