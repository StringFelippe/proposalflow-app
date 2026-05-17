from pathlib import Path
from pprint import pprint

from repositories.database import initialize_database
from repositories.company_repository import list_active_companies, get_company_by_cnpj
from services.document_generation_service import generate_documents_from_manual_data


BASE_DIR = Path(__file__).resolve().parent.parent


def choose_company() -> dict:
    companies = list_active_companies()

    if not companies:
        raise ValueError("Nenhuma empresa ativa cadastrada.")

    print("=" * 50)
    print("Empresas cadastradas:")
    print("=" * 50)

    for index, company in enumerate(companies, start=1):
        print(f"{index}. {company['razao_social']} - {company['cnpj']}")

    while True:
        choice = input("Escolha o número da empresa principal: ").strip()

        if not choice.isdigit():
            print("Digite um número válido.")
            continue

        choice_index = int(choice) - 1

        if 0 <= choice_index < len(companies):
            return companies[choice_index]

        print("Opção inválida.")


def main():
    initialize_database()

    empresa_principal = choose_company()

    manual_data = {
        "numero_nota": "00000999",
        "data_emissao": "23/01/2026",
        "valor_total_servico": "7.910,00",
        "prestador": {
            "cnpj": empresa_principal["cnpj"],
            "razao_social": empresa_principal["razao_social"],
            "endereco": empresa_principal["endereco"],
        },
        "tomador": {
            "cnpj": "96513809000196",
            "razao_social": "A.P.M.E.E. DEPUTADO PEDRO GERALDO COSTA",
            "endereco": "Rua Francisco Capara 75 - Jardim Fanganiello - CEP: 08450-570",
            "municipio": "São Paulo",
        },
        "itens": [
            {
                "quantidade": "1",
                "descricao": "SERVIÇO DE ROÇAGEM E CAPINAGEM DE MATO NO ENTORNO DA UNIDADE ESCOLAR",
                "valor_unitario": "7.910,00",
                "valor_total": "7.910,00",
            }
        ],
    }

    result = generate_documents_from_manual_data(
        manual_data=manual_data,
        output_base_folder=BASE_DIR / "output",
    )

    print("Geração manual concluída.")
    print(f"Pasta de saída: {result['output_folder']}")

    print("Arquivos gerados:")
    for file_path in result["generated_files"]:
        print(file_path)

    print("=" * 50)
    print("Orçamento 1:")
    pprint(result["budget_data_1"], width=120)


if __name__ == "__main__":
    main()