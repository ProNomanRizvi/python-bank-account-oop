import json

from account_factory import AccountFactory


def save_accounts_to_json(accounts, filepath):
    """
    Save a list of account objects to a JSON file.
    """
    accounts_data = [account.to_dict() for account in accounts]

    with open(filepath, "w") as file:
        json.dump(accounts_data, file, indent=4)


def load_accounts_from_json(filepath):
    """
    Load account objects from a JSON file.
    """
    try:
        with open(filepath, "r") as file:
            accounts_data = json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as e:
        raise ValueError("Accounts file is corrupted.") from e

    return [
        AccountFactory.create_from_dict(account_data)
        for account_data in accounts_data
    ]