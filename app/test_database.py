from pprint import pprint

from repositories.database import initialize_database
from repositories.company_repository import (
    create_company,
    create_incompatibility,
    list_active_companies,
)


def main():
    initialize_database()

    create_company(
        {
            "cnpj": "11111111000111",
            "razao_social": "Tfs Servicos de Zeladoria LTDA",
            "endereco": "RUA EXEMPLO 1, 100",
            "telefone": "11 1111-1111",
            "responsavel": "RESPONSÁVEL EMPRESA 2",
            "caminho_template": "app/templates/orcamento_teste.docx",
            "caminho_imagem": "",
            "ativa": 1,
        }
    )

    create_company(
        {
            "cnpj": "222222220001-2",
            "razao_social": "Mercurio Manutencao Predial LTDA",
            "endereco": "RUA EXEMPLO 2, 200",
            "telefone": "11 2222-2222",
            "responsavel": "RESPONSÁVEL EMPRESA 3",
            "caminho_template": "app/templates/orcamento_teste.docx",
            "caminho_imagem": "",
            "ativa": 1,
        }
    )

    create_company(
        {
            "cnpj": "33333333000133",
            "razao_social": "Alpha Reformas e Manutencao LTDA",
            "endereco": "RUA EXEMPLO 3, 300",
            "telefone": "11 3333-3333",
            "responsavel": "RESPONSÁVEL EMPRESA 4",
            "caminho_template": "app/templates/orcamento_teste.docx",
            "caminho_imagem": "",
            "ativa": 1,
        }
    )

    create_incompatibility(
        empresa_a_cnpj="11111111000111",
        empresa_b_cnpj="22222222000122",
        motivo="Teste de incompatibilidade entre empresas.",
    )

    companies = list_active_companies()

    print("Empresas cadastradas:")
    pprint(companies, width=120)


if __name__ == "__main__":
    main()