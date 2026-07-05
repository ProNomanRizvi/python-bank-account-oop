from account import Account
from savings_account import SavingsAccount
from checking_account import CheckingAccount


class AccountFactory:
    @staticmethod
    def create_account(account_type, owner_name, acc_no, **kwargs):
        if not isinstance(account_type, str):
            raise TypeError("account_type must be a string")

        account_type = account_type.strip().lower()

        if account_type == "account":
            return Account(owner_name, acc_no)

        elif account_type == "savings":
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
            "Expected 'account', 'savings' or 'checking'."
        )

    @staticmethod
    def create_from_dict(data):
        account_type = data["type"]
        owner_name = data["owner_name"]
        acc_no = data["acc_no"]

        if account_type == "account":
            account = AccountFactory.create_account(
                "account",
                owner_name,
                acc_no
            )

        elif account_type == "savings":
            account = AccountFactory.create_account(
                "savings",
                owner_name,
                acc_no,
                interest_rate=data["interest_rate"]
            )

        elif account_type == "checking":
            account = AccountFactory.create_account(
                "checking",
                owner_name,
                acc_no,
                overdraft_limit=data["overdraft_limit"]
            )

        else:
            raise ValueError(f"Invalid account type: {account_type!r}")

        account._restore_state(
            data["balance"],
            data["transaction_history"]
        )

        return account