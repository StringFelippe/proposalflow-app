from repositories.database import initialize_database, get_connection
from repositories.company_repository import create_company
from services.config_service import set_config_value


DEMO_COMPANIES = [
    {
        "cnpj": "12345678000190",
        "razao_social": "ALPHA SOLUCOES DIGITAIS LTDA",
        "endereco": "Rua das Inovações, 120",
        "endereco_completo": "Rua das Inovações, 120 - Centro - CEP: 01000-000 - São Paulo - SP",
        "telefone": "11999998888",
        "responsavel": "Marcos Almeida",
        "caminho_template": "",
        "caminho_imagem": "",
        "ativa": 1,
    },
    {
        "cnpj": "22345678000190",
        "razao_social": "BETA CONSULTORIA E SERVICOS LTDA",
        "endereco": "Avenida Central, 450",
        "endereco_completo": "Avenida Central, 450 - Centro - CEP: 02000-000 - São Paulo - SP",
        "telefone": "11988887777",
        "responsavel": "Camila Rocha",
        "caminho_template": "",
        "caminho_imagem": "",
        "ativa": 1,
    },
    {
        "cnpj": "32345678000190",
        "razao_social": "GAMMA TECNOLOGIA E SOLUCOES LTDA",
        "endereco": "Rua dos Sistemas, 88",
        "endereco_completo": "Rua dos Sistemas, 88 - Vila Digital - CEP: 03000-000 - São Paulo - SP",
        "telefone": "11977776666",
        "responsavel": "Bruno Martins",
        "caminho_template": "",
        "caminho_imagem": "",
        "ativa": 1,
    },
]


def reset_demo_database():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM empresas_incompativeis")
        cursor.execute("DELETE FROM empresas")

        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'empresas_incompativeis'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'empresas'")

        connection.commit()


def main():
    initialize_database()
    reset_demo_database()

    for company in DEMO_COMPANIES:
        create_company(company)

    set_config_value("dashboard_nfs_generated_count", "0")
    set_config_value("dashboard_nf_generated_count", "0")

    print("Banco demo criado com sucesso.")
    print("Fornecedores fictícios cadastrados:")
    for company in DEMO_COMPANIES:
        print(f"- {company['razao_social']} / {company['cnpj']}")


if __name__ == "__main__":
    main()