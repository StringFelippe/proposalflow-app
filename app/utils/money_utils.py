from decimal import Decimal


def brl_to_decimal(value: str) -> Decimal:
    """
    Converte valores brasileiros para Decimal.

    Exemplo:
    '9.504,00' -> Decimal('9504.00')
    '594,00' -> Decimal('594.00')
    """
    cleaned_value = value.replace("R$", "").strip()
    cleaned_value = cleaned_value.replace(".", "")
    cleaned_value = cleaned_value.replace(",", ".")

    return Decimal(cleaned_value)


def decimal_to_brl(value: Decimal) -> str:
    """
    Converte Decimal para formato brasileiro.

    Exemplo:
    Decimal('9504.00') -> '9.504,00'
    """
    formatted = f"{value:,.2f}"

    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def normalize_brl_value(value: str) -> str:
    """
    Normaliza valores monetários brasileiros para o padrão 9.999,99.

    Exemplos:
    'R$ 19.808,40' -> '19.808,40'
    'R$3,174,40' -> '3.174,40'
    '7910,00' -> '7.910,00' dependendo da formatação final
    """
    value = value.replace("R$", "").strip()

    # Caso venha algo como 3,174,40,
    # consideramos a última vírgula como decimal
    # e as anteriores como separador de milhar.
    if value.count(",") > 1:
        parts = value.split(",")
        decimal_part = parts[-1]
        integer_part = "".join(parts[:-1])
        value = f"{integer_part},{decimal_part}"

    decimal_value = brl_to_decimal(value)

    return decimal_to_brl(decimal_value)