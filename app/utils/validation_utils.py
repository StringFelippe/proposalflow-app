from datetime import datetime
from decimal import Decimal, InvalidOperation

from utils.company_utils import clean_cnpj


def is_valid_br_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False


def is_valid_cnpj_text(value: str) -> bool:
    cleaned = clean_cnpj(value)
    return len(cleaned) == 14 and cleaned.isalnum()


def is_valid_decimal_number(value: str) -> bool:
    try:
        cleaned = value.strip().replace(",", ".")
        number = Decimal(cleaned)
        return number > 0
    except (InvalidOperation, ValueError):
        return False


def is_valid_brl_money(value: str) -> bool:
    try:
        cleaned = value.replace("R$", "").strip()

        if cleaned.count(",") > 1:
            parts = cleaned.split(",")
            decimal_part = parts[-1]
            integer_part = "".join(parts[:-1])
            cleaned = f"{integer_part},{decimal_part}"

        cleaned = cleaned.replace(".", "").replace(",", ".")
        number = Decimal(cleaned)

        return number > 0
    except (InvalidOperation, ValueError):
        return False