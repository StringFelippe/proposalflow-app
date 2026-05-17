from pathlib import Path

from repositories.database import initialize_database
from repositories.company_repository import create_company, get_company_by_cnpj
from utils.company_utils import (
    clean_cnpj,
    clean_phone,
    format_cnpj,
    format_phone,
    is_valid_cnpj_raw,
    is_valid_phone,
)

BASE_DIR = Path(__file__).resolve().parent.parent

def ask_image_path() -> str:
    while True:
        value = input("Caminho da imagem/logo: ").strip()

        if not value:
            return ""

        path = Path(value)

        if not path.is_absolute():
            path = BASE_DIR / value

        if path.exists():
            return value

        print("Imagem não encontrada. Confira o caminho ou deixe vazio.")
        print(f"Caminho testado: {path}")


def ask_required_field(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"O campo '{label}' é obrigatório.")


def ask_optional_field(label: str) -> str:
    return input(f"{label}: ").strip()


def ask_cnpj() -> str:
    while True:
        value = input("CNPJ, apenas 14 letras/números, sem pontuação: ").strip()

        if is_valid_cnpj_raw(value):
            return clean_cnpj(value)

        print("CNPJ inválido. Use exatamente 14 caracteres, apenas letras e números.")


def ask_phone() -> str:
    while True:
        value = input("Telefone com DDD, apenas números, 10 ou 11 dígitos: ").strip()

        if not value:
            return ""

        if is_valid_phone(value):
            return clean_phone(value)

        print("Telefone inválido. Use 10 ou 11 dígitos, apenas números.")


def main():
    initialize_database()

    print("=" * 50)
    print("Cadastro de empresa")
    print("=" * 50)

    cnpj = ask_cnpj()
    existing_company = get_company_by_cnpj(cnpj)

    if existing_company:
        print("Já existe uma empresa cadastrada com esse CNPJ.")
        print(existing_company)

        confirm = input("Deseja sobrescrever os dados? (s/n): ").strip().lower()

        if confirm != "s":
            print("Cadastro cancelado.")
            return

    phone = ask_phone()

    endereco = ask_required_field("Endereço para orçamento, ex: Rua Odete, 316")
    endereco_completo = ask_required_field(
        "Endereço completo para anexos, ex: Rua Odete, 316 - Vila Pierina - CEP: 03733-060 - São Paulo – SP"
    )
    
    company = {
        "cnpj": cnpj,
        "razao_social": ask_required_field("Razão Social"),
        "endereco": endereco,
        "endereco_completo": endereco_completo,
        "telefone": phone,
        "responsavel": ask_optional_field("Responsável/Sócio"),
        "caminho_template": "",
        "caminho_imagem": ask_image_path(),
        "ativa": 1,
    }

    create_company(company)

    print("=" * 50)
    print("Empresa cadastrada/atualizada com sucesso!")
    print(f"CNPJ: {format_cnpj(company['cnpj'])}")
    print(f"Razão Social: {company['razao_social']}")
    print(f"Endereço: {company['endereco']}")

    if company["telefone"]:
        print(f"Telefone: {format_phone(company['telefone'])}")

    print(f"Responsável: {company['responsavel']}")
    print(f"Imagem/logo: {company['caminho_imagem']}")


if __name__ == "__main__":
    main()