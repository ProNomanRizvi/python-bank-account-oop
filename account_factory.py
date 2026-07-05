from account import Account
from savings_account import SavingsAccount
from checking_account import CheckingAccount


class AccountFactory:
    @staticmethod
    def create_account(account_type, owner_name, acc_no, **kwargs):
        if not isinstance(account_type, str):
            raise TypeError("account_type must be a string")

        account_type = account_type.strip().lower()

        if account_type == "savings":
            if "interest_rate" not in kwargs:
                raise TypeError("Missing required argument: interest_rate")

            return SavingsAccount(
                owner_name,
                acc_no,
                kwargs["interest_rate"]
            )

        elif account_type == "checking":
            if "overdraft_limit" not in kwargs:
                raise TypeError("Missing required argument: overdraft_limit")

            return CheckingAccount(
                owner_name,
                acc_no,
                kwargs["overdraft_limit"]
            )

        raise ValueError(
            f"Invalid account type: {account_type!r}. "
            "Expected 'savings' or 'checking'."
        )