from copy import deepcopy
from decimal import Decimal, ROUND_DOWN
import random

from services.config_service import get_app_config
from services.date_service import subtract_valid_days_from_budget_date
from utils.money_utils import brl_to_decimal, decimal_to_brl
from utils.company_utils import clean_single_line_text, format_cnpj, format_phone


def increase_unit_value_randomly(
    original_value: str,
    min_percentage: float,
    max_percentage: float,
) -> tuple[str, float]:
    original_decimal = brl_to_decimal(original_value)

    percentage = Decimal(str(random.uniform(min_percentage, max_percentage)))

    increased_value = original_decimal * (Decimal("1") + percentage)

    # Remove os centavos, mantendo valor inteiro em reais.
    integer_value = increased_value.quantize(Decimal("1"), rounding=ROUND_DOWN)

    return decimal_to_brl(integer_value), float(percentage)


def update_items_with_random_increase(items: list[dict]) -> list[dict]:
    config = get_app_config()

    min_percentage = config["comparative_min_percentage"] / 100
    max_percentage = config["comparative_max_percentage"] / 100

    new_items = []

    for item in items:
        new_unit_value, percentage = increase_unit_value_randomly(
            item["valor_unitario"],
            min_percentage=min_percentage,
            max_percentage=max_percentage,
        )

        quantity = brl_to_decimal(item["quantidade"])
        unit_value_decimal = brl_to_decimal(new_unit_value)
        new_total = quantity * unit_value_decimal

        new_items.append(
            {
                "quantidade": item["quantidade"],
                "descricao": item["descricao"],
                "valor_unitario": new_unit_value,
                "valor_total": decimal_to_brl(new_total),
                "percentual_aumento": round(percentage * 100, 2),
            }
        )

    return new_items


def calculate_items_total(items: list[dict]) -> str:
    total = sum(
        brl_to_decimal(item["valor_total"])
        for item in items
    )

    return decimal_to_brl(total)


def prepare_company_data_for_budget(company_data: dict) -> dict:
    endereco = clean_single_line_text(company_data.get("endereco", ""))
    endereco_completo = clean_single_line_text(
        company_data.get("endereco_completo") or endereco
    )

    return {
        "cnpj": company_data.get("cnpj", ""),
        "cnpj_formatado": format_cnpj(company_data.get("cnpj", "")),
        "razao_social": clean_single_line_text(company_data.get("razao_social", "")),
        "endereco": endereco,
        "endereco_orcamento": endereco,
        "endereco_completo": endereco_completo,
        "telefone": format_phone(company_data.get("telefone", "")),
        "responsavel": clean_single_line_text(company_data.get("responsavel", "")),
        "caminho_imagem": company_data.get("caminho_imagem", ""),
    }


def build_comparative_budget(
    base_budget_data: dict,
    company_data: dict,
) -> dict:
    comparative_budget = deepcopy(base_budget_data)

    config = get_app_config()

    new_date_info = subtract_valid_days_from_budget_date(
        comparative_budget["orcamento"]["data_emissao"],
        days_before=config["comparative_budget_days_before"],
    )

    new_items = update_items_with_random_increase(
        comparative_budget["itens"]
    )

    new_total = calculate_items_total(new_items)

    comparative_budget["empresa_proponente"] = prepare_company_data_for_budget(company_data)
    comparative_budget["itens"] = new_items

    comparative_budget["orcamento"]["data_emissao"] = new_date_info["data_orcamento"]
    comparative_budget["orcamento"]["data_emissao_extenso"] = new_date_info["data_orcamento_extenso"]
    comparative_budget["orcamento"]["ano_exercicio"] = new_date_info["ano_exercicio"]
    comparative_budget["orcamento"]["total"] = new_total

    comparative_budget["validacoes"] = {
        "itens": [],
        "total_geral": {},
        "todos_itens_validos": True,
        "total_geral_valido": True,
        "observacao": "Orçamento comparativo gerado a partir de empresa cadastrada/mockada.",
    }

    return comparative_budget