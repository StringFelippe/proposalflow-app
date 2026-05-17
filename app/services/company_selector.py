import random

from repositories.company_repository import (
    list_active_companies,
    list_incompatible_cnpjs,
)


def get_incompatible_cnpjs(cnpj: str) -> set[str]:
    return set(list_incompatible_cnpjs(cnpj))


def are_companies_compatible(company_a: dict, company_b: dict) -> bool:
    cnpj_a = company_a["cnpj"]
    cnpj_b = company_b["cnpj"]

    incompatible_with_a = get_incompatible_cnpjs(cnpj_a)
    incompatible_with_b = get_incompatible_cnpjs(cnpj_b)

    return cnpj_b not in incompatible_with_a and cnpj_a not in incompatible_with_b


def filter_compatible_companies(
    available_companies: list[dict],
    already_selected_companies: list[dict],
) -> list[dict]:
    compatible_companies = []

    for candidate in available_companies:
        is_same_as_selected = any(
            candidate["cnpj"] == selected["cnpj"]
            for selected in already_selected_companies
        )

        if is_same_as_selected:
            continue

        is_compatible_with_all = all(
            are_companies_compatible(candidate, selected)
            for selected in already_selected_companies
        )

        if is_compatible_with_all:
            compatible_companies.append(candidate)

    return compatible_companies


def select_comparative_companies(
    original_company: dict,
    quantity: int = 2,
) -> list[dict]:
    available_companies = list_active_companies()

    selected_companies = [original_company]
    comparative_companies = []

    for _ in range(quantity):
        compatible_options = filter_compatible_companies(
            available_companies=available_companies,
            already_selected_companies=selected_companies,
        )

        if not compatible_options:
            raise ValueError(
                "Não há empresas compatíveis suficientes para gerar os orçamentos comparativos."
            )

        chosen_company = random.choice(compatible_options)

        comparative_companies.append(chosen_company)
        selected_companies.append(chosen_company)

    return comparative_companies