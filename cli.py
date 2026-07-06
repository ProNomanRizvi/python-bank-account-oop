from account_factory import AccountFactory
from checking_account import CheckingAccount
from persistence import (
    save_accounts_to_json,
    load_accounts_from_json,
)
from savings_account import SavingsAccount

FILEPATH = "transactions.json"


def load_accounts():
    """
    Load all accounts from the JSON file.

    Returns:
        dict[str, Account]: Mapping of account number -> account object.
    """
    try:
        accounts = load_accounts_from_json(FILEPATH)
    except ValueError as e:
        print(f"\nWarning: {e}")
        print("Starting with an empty account database.")
        return {}

    return {account.acc_no: account for account in accounts}


def create_account_flow(accounts):
    """
    Create a new account.
    """
    print("\n========== Create Account ==========")
    print("1. Account")
    print("2. Savings Account")
    print("3. Checking Account")

    account_map = {
        "1": "account",
        "2": "savings",
        "3": "checking",
    }

    choice = input("Select account type: ").strip()

    if choice not in account_map:
        print("Invalid account type.")
        return

    account_type = account_map[choice]

    owner_name = input("Owner name: ").strip()
    acc_no = input("Account number: ").strip()

    if acc_no in accounts:
        print("Account number already exists.")
        return

    kwargs = {}

    if account_type == "savings":
        try:
            interest = float(
                input("Interest rate (%): ")
            )
            kwargs["interest_rate"] = interest / 100
        except ValueError:
            print("Interest rate must be numeric.")
            return

    elif account_type == "checking":
        try:
            overdraft = float(
                input("Overdraft limit: ")
            )
            kwargs["overdraft_limit"] = overdraft
        except ValueError:
            print("Overdraft limit must be numeric.")
            return

    try:
        account = AccountFactory.create_account(
            account_type,
            owner_name,
            acc_no,
            **kwargs,
        )
    except (TypeError, ValueError) as e:
        print(f"Failed to create account: {e}")
        return

    accounts[acc_no] = account

    print("\nAccount created successfully!")
    print(account)


def deposit_flow(accounts):
    """
    Deposit money into an account.
    """
    print("\n========== Deposit ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    try:
        amount = float(input("Deposit amount: "))
    except ValueError:
        print("Amount must be numeric.")
        return

    try:
        account.deposit(amount)
    except (TypeError, ValueError) as e:
        print(f"Deposit failed: {e}")
        return

    print("\nDeposit successful.")
    print(f"Current Balance: {account.balance:.2f}")

def withdraw_flow(accounts):
    """
    Withdraw money from an account.
    """
    print("\n========== Withdraw ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    try:
        amount = float(input("Withdrawal amount: "))
    except ValueError:
        print("Amount must be numeric.")
        return

    try:
        account.withdraw(amount)
    except (TypeError, ValueError) as e:
        print(f"Withdrawal failed: {e}")
        return

    print("\nWithdrawal successful.")
    print(f"Current Balance: {account.balance:.2f}")


def transfer_flow(accounts):
    """
    Transfer money between two accounts.
    """
    print("\n========== Transfer ==========")

    source_acc_no = input("Source account number: ").strip()
    source_account = accounts.get(source_acc_no)

    if source_account is None:
        print("Source account not found.")
        return

    destination_acc_no = input("Destination account number: ").strip()
    destination_account = accounts.get(destination_acc_no)

    if destination_account is None:
        print("Destination account not found.")
        return

    try:
        amount = float(input("Transfer amount: "))
    except ValueError:
        print("Amount must be numeric.")
        return

    try:
        source_account.transfer(destination_account, amount)
    except (TypeError, ValueError) as e:
        print(f"Transfer failed: {e}")
        return

    print("\nTransfer completed successfully.")
    print(
        f"Source ({source_account.acc_no}) Balance      : "
        f"{source_account.balance:.2f}"
    )
    print(
        f"Destination ({destination_account.acc_no}) Balance : "
        f"{destination_account.balance:.2f}"
    )


def balance_flow(accounts):
    """
    Display complete account information.
    """
    print("\n========== Account Details ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    print()
    print(account)


def history_flow(accounts):
    """
    Display transaction history.
    """
    print("\n========== Transaction History ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    history = account.transaction_history

    if not history:
        print("No transactions found.")
        return

    print()

    for index, transaction in enumerate(history, start=1):
        print(f"Transaction {index}")
        print(f"  Type      : {transaction.get('type')}")
        print(f"  Amount    : {transaction.get('amount')}")
        print(f"  Timestamp : {transaction.get('timestamp')}")
        print("-" * 40)


def list_accounts_flow(accounts):
    """
    Display all accounts.
    """
    print("\n========== All Accounts ==========")

    if not accounts:
        print("No accounts available.")
        return

    print()

    for account in accounts.values():
        print(
            f"Account No : {account.acc_no}"
            f" | Owner : {account.owner_name}"
            f" | Balance : {account.balance:.2f}"
        )


def delete_account_flow(accounts):
    """
    Delete an account (only if balance is zero).
    """
    print("\n========== Delete Account ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    if abs(account.balance) > 1e-9:
        print("Cannot delete an account with a non-zero balance.")
        return

    confirm = input(
        f"Delete account '{acc_no}'? (Y/N): "
    ).strip().lower()

    if confirm != "y":
        print("Deletion cancelled.")
        return

    del accounts[acc_no]

    print("Account deleted successfully.")


def apply_interest_flow(accounts):
    """
    Apply interest to a SavingsAccount.
    """
    print("\n========== Apply Interest ==========")

    acc_no = input("Savings account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    if not isinstance(account, SavingsAccount):
        print("Interest can only be applied to Savings Accounts.")
        return

    try:
        account.add_interest()
    except (TypeError, ValueError) as e:
        print(f"Failed to apply interest: {e}")
        return

    print("Interest applied successfully.")
    print(f"Current Balance: {account.balance:.2f}")


def search_account_flow(accounts):
    """
    Search an account by account number.
    """
    print("\n========== Search Account ==========")

    acc_no = input("Account number: ").strip()

    account = accounts.get(acc_no)

    if account is None:
        print("Account not found.")
        return

    print()
    print(account)


def statistics_flow(accounts):
    """
    Display simple bank statistics.
    """
    print("\n========== Statistics ==========")

    if not accounts:
        print("No accounts available.")
        return

    total_accounts = len(accounts)
    total_balance = sum(acc.balance for acc in accounts.values())

    savings = sum(
        isinstance(acc, SavingsAccount)
        for acc in accounts.values()
    )

    checking = sum(
    isinstance(acc, CheckingAccount)
    for acc in accounts.values()
    )

    plain = total_accounts - savings - checking

    print(f"Total Accounts : {total_accounts}")
    print(f"Plain Accounts : {plain}")
    print(f"Savings        : {savings}")
    print(f"Checking       : {checking}")
    print(f"Total Balance  : {total_balance:.2f}")


def main():
    accounts = load_accounts()

    actions = {
        "1": create_account_flow,
        "2": deposit_flow,
        "3": withdraw_flow,
        "4": transfer_flow,
        "5": balance_flow,
        "6": history_flow,
        "7": list_accounts_flow,
        "8": delete_account_flow,
        "9": apply_interest_flow,
        "10": search_account_flow,
        "11": statistics_flow,
    }

    while True:
        print("\n" + "=" * 40)
        print("        Banking System")
        print("=" * 40)
        print("1.  Create Account")
        print("2.  Deposit")
        print("3.  Withdraw")
        print("4.  Transfer")
        print("5.  Check Balance")
        print("6.  Transaction History")
        print("7.  List All Accounts")
        print("8.  Delete Account")
        print("9.  Apply Interest")
        print("10. Search Account")
        print("11. Statistics")
        print("12. Save & Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "12":
            save_accounts_to_json(
                list(accounts.values()),
                FILEPATH,
            )

            print("\nAccounts saved successfully.")
            print("Goodbye!")
            break

        action = actions.get(choice)

        if action is None:
            print("Invalid choice. Please try again.")
            continue

        action(accounts)


if __name__ == "__main__":
    main()