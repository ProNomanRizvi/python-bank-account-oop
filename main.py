from account_factory import AccountFactory
from persistence import save_accounts_to_json, load_accounts_from_json


def main():
    print("\n=== Creating Accounts ===\n")

    savings = AccountFactory.create_account(
        "savings",
        "Ali",
        "S001",
        interest_rate=0.05
    )

    checking = AccountFactory.create_account(
        "checking",
        "Ahmed",
        "C001",
        overdraft_limit=500
    )

    account = AccountFactory.create_account(
        "account",
        "Sara",
        "A001"
    )

    print("Accounts created successfully.")

    print("\n=== Performing Transactions ===\n")

    savings.deposit(1000)
    savings.add_interest()

    checking.deposit(800)
    checking.withdraw(1000)        # Uses overdraft

    account.deposit(500)
    account.transfer(savings, 200)

    print("Transactions completed successfully.")

    print("\n=== Current Account Details ===\n")

    print(savings)
    print("-" * 40)

    print(checking)
    print("-" * 40)

    print(account)

    accounts = [savings, checking, account]

    print("\n=== Saving Accounts to JSON ===\n")

    save_accounts_to_json(accounts, "transactions.json")

    print("Accounts saved to transactions.json")

    print("\n=== Loading Accounts from JSON ===\n")

    loaded_accounts = load_accounts_from_json("transactions.json")

    print(f"Loaded {len(loaded_accounts)} account(s).\n")

    print("=== Restored Account Details ===\n")

    for acc in loaded_accounts:
        print(acc)
        print("-" * 40)

    print("\n=== Error Demonstration ===\n")

    try:
        checking.withdraw(1000)   # Exceeds overdraft limit
    except ValueError as e:
        print(f"Operation failed: {e}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()