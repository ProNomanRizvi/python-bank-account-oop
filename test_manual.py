from account import Account
from savings_account import SavingsAccount
from checking_account import CheckingAccount


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
    
    print("\n=== Testing Complete ===")