from repositories.company_repository import get_company_by_cnpj
from services.exceptions import CompanyNotRegisteredError
from utils.company_utils import clean_cnpj


def raise_if_main_company_not_registered(extracted_data: dict) -> None:
    prestador = extracted_data.get("prestador", {})

    cnpj = clean_cnpj(prestador.get("cnpj", ""))
    registered_company = get_company_by_cnpj(cnpj)

    if registered_company:
        return

    company_data = {
        "cnpj": cnpj,
        "razao_social": prestador.get("razao_social", ""),
        "endereco": prestador.get("endereco", ""),
        "endereco_completo": prestador.get("endereco", ""),
        "telefone": "",
        "responsavel": "",
        "caminho_imagem": "",
    }

    raise CompanyNotRegisteredError(company_data)