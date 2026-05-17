from repositories.company_repository import get_company_by_cnpj
from utils.company_utils import (
    clean_cnpj,
    clean_single_line_text,
    format_cnpj,
    format_phone,
)


def get_company_data_for_budget(extracted_company: dict) -> dict:
    extracted_cnpj = clean_cnpj(extracted_company["cnpj"])

    registered_company = get_company_by_cnpj(extracted_cnpj)

    if registered_company:
        endereco = clean_single_line_text(registered_company["endereco"])
        endereco_completo = clean_single_line_text(
            registered_company.get("endereco_completo") or endereco
        )

        return {
            "cnpj": registered_company["cnpj"],
            "cnpj_formatado": format_cnpj(registered_company["cnpj"]),
            "razao_social": clean_single_line_text(registered_company["razao_social"]),
            "endereco": endereco,
            "endereco_orcamento": endereco,
            "endereco_completo": endereco_completo,
            "telefone": format_phone(registered_company.get("telefone", "")),
            "responsavel": clean_single_line_text(registered_company.get("responsavel", "")),
            "caminho_imagem": registered_company.get("caminho_imagem", ""),
        }

    return {
        "cnpj": extracted_cnpj,
        "cnpj_formatado": format_cnpj(extracted_cnpj),
        "razao_social": clean_single_line_text(extracted_company["razao_social"]),
        "endereco": clean_single_line_text(extracted_company["endereco"]),
        "endereco_orcamento": clean_single_line_text(extracted_company["endereco"]),
        "endereco_completo": clean_single_line_text(extracted_company["endereco"]),
        "telefone": "",
        "responsavel": "",
        "caminho_imagem": "",
    }