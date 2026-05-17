from datetime import datetime, timedelta
from services.config_service import get_app_config

import holidays


MONTHS_PT_BR = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


def parse_br_date(date_text: str) -> datetime:
    return datetime.strptime(date_text, "%d/%m/%Y")


def format_br_date(date: datetime) -> str:
    return date.strftime("%d/%m/%Y")


def format_date_long_pt_br(date: datetime) -> str:
    day = date.day
    month = MONTHS_PT_BR[date.month]
    year = date.year

    return f"{day} de {month} de {year}"


def get_brazil_sp_holidays(year: int):
    national_holidays = holidays.country_holidays("BR", years=year)
    state_holidays = holidays.country_holidays("BR", subdiv="SP", years=year)

    return national_holidays + state_holidays


def is_weekend(date: datetime) -> bool:
    return date.weekday() in [5, 6]


def is_holiday(date: datetime) -> bool:
    br_sp_holidays = get_brazil_sp_holidays(date.year)

    return date.date() in br_sp_holidays


def is_valid_budget_date(date: datetime) -> bool:
    return not is_weekend(date) and not is_holiday(date)


def calculate_budget_date(invoice_date_text: str, days_before: int = 10) -> datetime:
    invoice_date = parse_br_date(invoice_date_text)

    budget_date = invoice_date - timedelta(days=days_before)

    while not is_valid_budget_date(budget_date):
        budget_date = budget_date - timedelta(days=1)

    return budget_date


def get_budget_date_info(invoice_date_text: str) -> dict:
    config = get_app_config()

    budget_date = calculate_budget_date(
        invoice_date_text,
        days_before=config["budget_days_before_invoice"],
    )

    return {
        "data_orcamento": format_br_date(budget_date),
        "data_orcamento_extenso": format_date_long_pt_br(budget_date),
        "ano_exercicio": budget_date.year,
    }

def subtract_valid_days_from_budget_date(date_text: str, days_before: int = 1) -> dict:
    base_date = parse_br_date(date_text)
    new_date = base_date - timedelta(days=days_before)

    while not is_valid_budget_date(new_date):
        new_date = new_date - timedelta(days=1)

    return {
        "data_orcamento": format_br_date(new_date),
        "data_orcamento_extenso": format_date_long_pt_br(new_date),
        "ano_exercicio": new_date.year,
    }


def get_invoice_date_info(invoice_date_text: str) -> dict:
    invoice_date = parse_br_date(invoice_date_text)

    return {
        "data_nota": format_br_date(invoice_date),
        "data_nota_extenso": format_date_long_pt_br(invoice_date),
        "ano_nota": invoice_date.year,
    }