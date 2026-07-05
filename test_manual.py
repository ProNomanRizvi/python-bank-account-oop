from account import Account
from savings_account import SavingsAccount
from checking_account import CheckingAccount
from account_factory import AccountFactory
from persistence import save_accounts_to_json, load_accounts_from_json
from account_factory import AccountFactory
import os


def run_test(test_name, test_func):
    try:
        test_func()
        print(f"[PASS] {test_name}")
    except AssertionError as e:
        print(f"[FAIL] {test_name} -> {e}")
    except Exception as e:
        print(f"[FAIL] {test_name} -> Unexpected {type(e).__name__}: {e}")


# 1. Normal account + deposit(500)
def test_deposit():
    acc = Account("Ali", "12345")
    acc.deposit(500)
    assert acc.balance == 500, f"Expected balance 500, got {acc.balance}"


# 2. deposit(True) should raise TypeError
def test_deposit_bool():
    acc = Account("Ali", "12345")
    try:
        acc.deposit(True)
        raise AssertionError("TypeError was not raised.")
    except TypeError:
        pass


# 3. withdraw(-100) should raise ValueError
def test_withdraw_negative():
    acc = Account("Ali", "12345", 1000)
    try:
        acc.withdraw(-100)
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass


# 4. Empty owner_name should raise ValueError
def test_empty_owner():
    try:
        Account("", "123")
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass


# 5. balance property should be read-only
def test_balance_read_only():
    acc = Account("Ali", "12345", 1000)
    try:
        acc.balance = 99999
        raise AssertionError("AttributeError was not raised.")
    except AttributeError:
        pass

# 6. add_interest() should increase balance correctly
def test_add_interest():
    acc = SavingsAccount("Ali", "12345", 0.05)
    acc.deposit(1000)

    interest = acc.add_interest()

    assert interest == 50, f"Expected interest 50, got {interest}"
    assert acc.balance == 1050, f"Expected balance 1050, got {acc.balance}"


# 7. add_interest() on zero balance should not crash
def test_add_interest_zero_balance():
    acc = SavingsAccount("Ali", "12345", 0.05)

    interest = acc.add_interest()

    assert interest == 0, f"Expected interest 0, got {interest}"
    assert acc.balance == 0, f"Expected balance 0, got {acc.balance}"


# 8. Last transaction should be recorded as 'interest'
def test_interest_transaction_type():
    acc = SavingsAccount("Ali", "12345", 0.10)
    acc.deposit(1000)
    acc.add_interest()

    last_transaction = acc.transaction_history[-1]
    assert last_transaction["type"] == "interest", (
        f"Expected transaction type 'interest', got {last_transaction['type']}"
    )

# 9. Normal withdraw within available balance
def test_checking_withdraw_normal():
    acc = CheckingAccount("Ali", "12345", 500)
    acc.deposit(1000)

    acc.withdraw(400)

    assert acc.balance == 600, f"Expected balance 600, got {acc.balance}"


# 10. Withdraw using overdraft (should not raise an error)
def test_checking_overdraft_within_limit():
    acc = CheckingAccount("Ali", "12345", 500)
    acc.deposit(100)

    acc.withdraw(400)  # Balance becomes -300

    assert acc.balance == -300, f"Expected balance -300, got {acc.balance}"


# 11. Withdraw exceeding overdraft limit
def test_checking_overdraft_exceeded():
    acc = CheckingAccount("Ali", "12345", 500)
    acc.deposit(100)

    try:
        acc.withdraw(700)  # Available = 100 + 500 = 600
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass

# 12. Only the first crossing into negative balance is tagged as "overdraft"
def test_overdraft_transaction_type():
    acc = CheckingAccount("Ali", "12345", 500)

    acc.deposit(100)

    # First withdrawal crosses into negative balance
    acc.withdraw(200)
    assert acc.transaction_history[-1]["type"] == "overdraft", (
        f"Expected 'overdraft', got {acc.transaction_history[-1]['type']}"
    )

    # Second withdrawal starts from an already-negative balance
    acc.withdraw(50)
    assert acc.transaction_history[-1]["type"] == "withdraw", (
        f"Expected 'withdraw', got {acc.transaction_history[-1]['type']}"
    )

# 13. Normal transfer between accounts
def test_transfer_success():
    acc1 = Account("Ali", "111", 1000)
    acc2 = Account("Ahmed", "222", 500)

    acc1.transfer(acc2, 300)

    assert acc1.balance == 700, f"Expected 700, got {acc1.balance}"
    assert acc2.balance == 800, f"Expected 800, got {acc2.balance}"

# Helper class to simulate deposit failure
class BrokenAccount(Account):
    def deposit(self, amount):
        raise ValueError("Simulated deposit failure")


# 14. Transfer rollback
def test_transfer_rollback():
    source = Account("Ali", "111", 1000)
    destination = BrokenAccount("Ahmed", "222")

    try:
        source.transfer(destination, 300)
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass

    # Money should be restored to the source account.
    assert source.balance == 1000, (
        f"Expected rollback to restore balance to 1000, got {source.balance}"
    )

# 15. Invalid destination object
def test_transfer_invalid_destination():
    source = Account("Ali", "111", 1000)

    try:
        source.transfer("not an account", 100)
        raise AssertionError("TypeError was not raised.")
    except TypeError:
        pass

# 16. Factory creates SavingsAccount
def test_factory_savings():
    acc = AccountFactory.create_account(
        "savings",
        "Ali",
        "111",
        interest_rate=0.05
    )

    assert isinstance(acc, SavingsAccount), (
        f"Expected SavingsAccount, got {type(acc).__name__}"
    )

# 17. Factory normalizes uppercase account type
def test_factory_checking_uppercase():
    acc = AccountFactory.create_account(
        "CHECKING",
        "Ali",
        "222",
        overdraft_limit=500
    )

    assert isinstance(acc, CheckingAccount), (
        f"Expected CheckingAccount, got {type(acc).__name__}"
    )

# 18. Missing interest_rate should raise TypeError
def test_factory_missing_interest_rate():
    try:
        AccountFactory.create_account(
            "savings",
            "Ali",
            "333"
        )
        raise AssertionError("TypeError was not raised.")
    except TypeError:
        pass

# 19. Invalid account type should raise ValueError
def test_factory_invalid_account_type():
    try:
        AccountFactory.create_account(
            "crypto",
            "Ali",
            "444"
        )
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass

# 20. Factory round-trip (object -> dict -> object)
def test_factory_round_trip():
    acc = AccountFactory.create_account(
        "savings",
        "Ali",
        "111",
        interest_rate=0.05
    )

    acc.deposit(1000)
    acc.add_interest()

    data = acc.to_dict()
    restored = AccountFactory.create_from_dict(data)

    assert restored.balance == acc.balance
    assert restored.owner_name == acc.owner_name
    assert restored.acc_no == acc.acc_no
    assert restored.interest_rate == acc.interest_rate
    assert len(restored.transaction_history) == len(acc.transaction_history)

# 21. Save -> Load round-trip
def test_json_persistence_round_trip():
    filepath = "test_accounts.json"

    acc1 = AccountFactory.create_account(
        "savings",
        "Ali",
        "111",
        interest_rate=0.05
    )
    acc1.deposit(1000)
    acc1.add_interest()

    acc2 = AccountFactory.create_account(
        "checking",
        "Ahmed",
        "222",
        overdraft_limit=500
    )
    acc2.deposit(800)
    acc2.withdraw(1000)

    acc3 = AccountFactory.create_account(
        "account",
        "Sara",
        "333"
    )
    acc3.deposit(250)

    original_accounts = [acc1, acc2, acc3]

    save_accounts_to_json(original_accounts, filepath)
    loaded_accounts = load_accounts_from_json(filepath)

    assert len(loaded_accounts) == len(original_accounts)

    for original, loaded in zip(original_accounts, loaded_accounts):
        assert type(loaded) is type(original)
        assert loaded.owner_name == original.owner_name
        assert loaded.acc_no == original.acc_no
        assert loaded.balance == original.balance
        assert loaded.transaction_history == original.transaction_history

        if hasattr(original, "interest_rate"):
            assert loaded.interest_rate == original.interest_rate

        if hasattr(original, "overdraft_limit"):
            assert loaded.overdraft_limit == original.overdraft_limit

    os.remove(filepath)

# 22. Corrupt JSON should raise ValueError
def test_json_corrupt_file():
    filepath = "corrupt_accounts.json"

    with open(filepath, "w") as file:
        file.write("{ invalid json")

    try:
        load_accounts_from_json(filepath)
        raise AssertionError("ValueError was not raised.")
    except ValueError:
        pass
    finally:
        os.remove(filepath)

# 23. Missing JSON file returns empty list
def test_json_missing_file():
    filepath = "file_that_does_not_exist.json"

    if os.path.exists(filepath):
        os.remove(filepath)

    accounts = load_accounts_from_json(filepath)

    assert accounts == [], (
        f"Expected empty list, got {accounts}"
    )

if __name__ == "__main__":
    print("=== Manual Account Tests ===\n")

    run_test("Deposit updates balance", test_deposit)
    run_test("deposit(True) raises TypeError", test_deposit_bool)
    run_test("withdraw(-100) raises ValueError", test_withdraw_negative)
    run_test("Empty owner_name raises ValueError", test_empty_owner)
    run_test("balance property is read-only", test_balance_read_only)
    run_test("add_interest() updates balance", test_add_interest)
    run_test("add_interest() on zero balance returns 0", test_add_interest_zero_balance)
    run_test("Transaction history records 'interest'", test_interest_transaction_type)
    run_test("CheckingAccount normal withdraw", test_checking_withdraw_normal)
    run_test("CheckingAccount overdraft within limit", test_checking_overdraft_within_limit)
    run_test("CheckingAccount overdraft limit exceeded", test_checking_overdraft_exceeded)
    run_test(
    "Only first negative crossing is tagged as overdraft",
    test_overdraft_transaction_type)
    run_test("Transfer updates both balances", test_transfer_success)
    run_test("Transfer rollback restores source balance", test_transfer_rollback)
    run_test("Transfer with invalid destination raises TypeError", test_transfer_invalid_destination)
    run_test("Factory creates SavingsAccount", test_factory_savings)
    run_test("Factory normalizes uppercase input", test_factory_checking_uppercase)
    run_test("Factory missing interest_rate raises TypeError", test_factory_missing_interest_rate)
    run_test("Factory invalid account type raises ValueError", test_factory_invalid_account_type)
    run_test("Factory round-trip serialization", test_factory_round_trip)
    run_test("JSON persistence round-trip", test_json_persistence_round_trip)
    run_test("Corrupt JSON raises ValueError", test_json_corrupt_file)
    run_test("Missing JSON file returns empty list", test_json_missing_file)
    
    print("\n=== Testing Complete ===")