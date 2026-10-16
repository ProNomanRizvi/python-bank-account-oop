import json
import os
import tempfile
from pathlib import Path

from account_factory import AccountFactory


def save_accounts_to_json(accounts, filepath):
    """
    Replace the accounts file only after a complete, valid JSON write.
    """
    accounts_data = [account.to_dict() for account in accounts]
    path = Path(filepath)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as file:
            temp_name = file.name
            json.dump(accounts_data, file, indent=4, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)


def _reject_nonfinite_constant(value):
    raise ValueError(f"Accounts file contains a non-finite number: {value}.")


def load_accounts_from_json(filepath):
    """
    Load account objects from a JSON file.
    """
    try:
        with open(filepath, "r") as file:
            accounts_data = json.load(file, parse_constant=_reject_nonfinite_constant)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as e:
        raise ValueError("Accounts file is corrupted.") from e

    return [
        AccountFactory.create_from_dict(account_data)
        for account_data in accounts_data
    ]
