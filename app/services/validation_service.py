from utils.money_utils import brl_to_decimal, decimal_to_brl


def validate_items_values(items: list[dict]) -> list[dict]:
    validations = []

    for index, item in enumerate(items, start=1):
        quantity = brl_to_decimal(item["quantidade"])
        unit_value = brl_to_decimal(item["valor_unitario"])
        informed_total = brl_to_decimal(item["valor_total"])

        calculated_total = quantity * unit_value
        is_valid = calculated_total == informed_total

        validations.append(
            {
                "item": index,
                "quantidade": str(quantity),
                "valor_unitario": decimal_to_brl(unit_value),
                "valor_total_informado": decimal_to_brl(informed_total),
                "valor_total_calculado": decimal_to_brl(calculated_total),
                "valido": is_valid,
            }
        )

    return validations


def calculate_grand_total(items: list[dict]) -> str:
    total = sum(
        brl_to_decimal(item["valor_total"])
        for item in items
    )

    return decimal_to_brl(total)


def validate_grand_total(items: list[dict], informed_grand_total: str) -> dict:
    calculated_grand_total = calculate_grand_total(items)

    calculated = brl_to_decimal(calculated_grand_total)
    informed = brl_to_decimal(informed_grand_total)

    return {
        "valor_total_calculado": calculated_grand_total,
        "valor_total_informado": decimal_to_brl(informed),
        "valido": calculated == informed,
    }