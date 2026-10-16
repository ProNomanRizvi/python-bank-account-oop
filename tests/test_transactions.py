import math

import pytest

from account import Account
from checking_account import CheckingAccount
from savings_account import SavingsAccount
from account_factory import AccountFactory
from persistence import load_accounts_from_json, save_accounts_to_json


@pytest.mark.parametrize("amount", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_money_is_rejected_without_mutation(amount):
    with pytest.raises(ValueError):
        Account("Owner", "1", amount)
    account = Account("Owner", "1", 100)
    for operation in (account.deposit, account.withdraw):
        with pytest.raises(ValueError):
            operation(amount)
        assert account.balance == 100
        assert account.transaction_history == []

    checking = CheckingAccount("Owner", "2", 50)
    with pytest.raises(ValueError):
        checking.withdraw(amount)
    assert checking.balance == 0
    assert checking.transaction_history == []


@pytest.mark.parametrize("amount", [-1, float("nan"), float("inf")])
def test_account_options_reject_invalid_values(amount):
    with pytest.raises(ValueError):
        SavingsAccount("Owner", "1", amount)
    with pytest.raises(ValueError):
        CheckingAccount("Owner", "2", amount)


def test_deposit_rejects_overflow_before_changing_balance():
    account = Account("Owner", "1", 1e308)
    with pytest.raises(ValueError, match="finite"):
        account.deposit(1e308)
    assert math.isfinite(account.balance)
    assert account.transaction_history == []


class PartialDeposit(Account):
    def deposit(self, amount):
        super().deposit(amount)
        raise RuntimeError("Deposit failed after mutation")


class PartialWithdraw(Account):
    def withdraw(self, amount):
        super().withdraw(amount)
        raise RuntimeError("Withdraw failed after mutation")


@pytest.mark.parametrize("source_type,destination_type", [
    (Account, PartialDeposit), (PartialWithdraw, Account),
])
def test_failed_transfer_restores_both_balances_and_histories(source_type, destination_type):
    source = source_type("Source", "1", 100)
    destination = destination_type("Destination", "2", 20)
    source.deposit(10)
    if destination_type is Account:
        destination.deposit(5)
    before_source = (source.balance, list(source.transaction_history))
    before_destination = (destination.balance, list(destination.transaction_history))

    with pytest.raises(RuntimeError):
        source.transfer(destination, 30)

    assert (source.balance, source.transaction_history) == before_source
    assert (destination.balance, destination.transaction_history) == before_destination


def test_successful_transfer_records_both_sides():
    source = CheckingAccount("Source", "1", 50)
    destination = SavingsAccount("Destination", "2", 0.05)
    source.deposit(10)
    source.transfer(destination, 30)
    assert source.balance == -20
    assert destination.balance == 30
    assert source.transaction_history[-1]["type"] == "overdraft"
    assert destination.transaction_history[-1]["type"] == "deposit"


def test_deserialization_rejects_nonfinite_balance():
    account = Account("Owner", "1", 10)
    data = account.to_dict()
    data["balance"] = float("nan")
    with pytest.raises(ValueError):
        AccountFactory.create_from_dict(data)


def test_deserialization_allows_valid_checking_overdraft():
    account = CheckingAccount("Owner", "1", 50)
    account.deposit(10)
    account.withdraw(30)
    restored = AccountFactory.create_from_dict(account.to_dict())
    assert restored.balance == -20


def test_failed_json_save_preserves_existing_file(tmp_path):
    path = tmp_path / "accounts.json"
    path.write_text('original data')
    account = Account("Owner", "1", 10)
    account.transaction_history.append({"amount": float("nan")})
    with pytest.raises(ValueError):
        save_accounts_to_json([account], path)
    assert path.read_text() == 'original data'
    assert list(tmp_path.glob(".accounts.json.*.tmp")) == []


def test_json_load_rejects_nonfinite_numbers(tmp_path):
    path = tmp_path / "accounts.json"
    path.write_text('[{"type":"account","owner_name":"Owner","acc_no":"1",'
                    '"balance":NaN,"transaction_history":[]}]')
    with pytest.raises(ValueError, match="non-finite"):
        load_accounts_from_json(path)
