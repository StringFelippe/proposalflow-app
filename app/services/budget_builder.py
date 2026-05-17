from services.company_service import get_company_data_for_budget
from services.date_service import get_budget_date_info, get_invoice_date_info
from services.validation_service import (
    calculate_grand_total,
    validate_grand_total,
    validate_items_values,
)
from utils.company_utils import clean_cnpj, format_cnpj


def get_proposal_category(document_type: str) -> str:
    if document_type == "NF":
        return "Produto / Product"

    return "Serviço / Service"


def build_budget_data(extracted_data: dict) -> dict:
    date_info = get_budget_date_info(extracted_data["data_emissao"])
    invoice_date_info = get_invoice_date_info(extracted_data["data_emissao"])
    validations = validate_items_values(extracted_data["itens"])
    grand_total = calculate_grand_total(extracted_data["itens"])

    grand_total_validation = validate_grand_total(
        extracted_data["itens"],
        extracted_data["valor_total_servico"],
    )

    empresa_proponente = get_company_data_for_budget(extracted_data["prestador"])

    cliente_cnpj = clean_cnpj(extracted_data["tomador"]["cnpj"])

    return {
        "tipo_documento": extracted_data.get("tipo_documento", "NFS"),
        "numero_nota": extracted_data["numero_nota"],

        # Mantemos a chave "apm" por compatibilidade com os templates antigos.
        # Conceitualmente, no ProposalFlow isso representa o cliente.
        "apm": {
            "cnpj": cliente_cnpj,
            "cnpj_formatado": format_cnpj(cliente_cnpj),
            "nome": extracted_data["tomador"]["razao_social"],
            "endereco": extracted_data["tomador"]["endereco"],
            "municipio": extracted_data["tomador"]["municipio"],
        },

        # Mantemos a chave "empresa_proponente" por compatibilidade.
        # Conceitualmente, no ProposalFlow isso representa o fornecedor.
        "empresa_proponente": empresa_proponente,

        # Mantemos a chave "orcamento" por compatibilidade com docxtpl.
        # Conceitualmente, no ProposalFlow isso representa a proposta.
        "orcamento": {
            "categoria": get_proposal_category(
                extracted_data.get("tipo_documento", "NFS")
            ),
            "ano_exercicio": date_info["ano_exercicio"],
            "data_emissao": date_info["data_orcamento"],
            "data_emissao_extenso": date_info["data_orcamento_extenso"],
            "prazo_validade": "30 dias",
            "condicao_pagamento": "Conforme negociação comercial",
            "total": grand_total,
        },

        "itens": extracted_data["itens"],

        "validacoes": {
            "itens": validations,
            "total_geral": grand_total_validation,
            "todos_itens_validos": all(item["valido"] for item in validations),
            "total_geral_valido": grand_total_validation["valido"],
        },

        # Mantemos a chave "nota_fiscal" por compatibilidade.
        # Conceitualmente, no ProposalFlow isso representa o documento de entrada.
        "nota_fiscal": {
            "numero": extracted_data["numero_nota"],
            "numero_sem_zeros": str(int(extracted_data["numero_nota"])),
            "data": invoice_date_info["data_nota"],
            "data_extenso": invoice_date_info["data_nota_extenso"],
            "ano": invoice_date_info["ano_nota"],
        },
    }