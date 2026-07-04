from account import Account
from savings_account import SavingsAccount


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

    print("\n=== Testing Complete ===")