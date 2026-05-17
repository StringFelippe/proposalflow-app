from repositories.database import get_connection


def delete_company_by_cnpj(cnpj: str):
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM empresas_incompativeis
            WHERE empresa_a_cnpj = ? OR empresa_b_cnpj = ?
            """,
            (cnpj, cnpj),
        )

        cursor.execute(
            """
            DELETE FROM empresas
            WHERE cnpj = ?
            """,
            (cnpj,),
        )

        connection.commit()


def main():
    cnpj = input("Digite o CNPJ da empresa para excluir, somente letras/números: ").strip()

    confirm = input(f"Tem certeza que deseja excluir a empresa {cnpj}? Digite SIM: ").strip()

    if confirm != "SIM":
        print("Operação cancelada.")
        return

    delete_company_by_cnpj(cnpj)

    print("Empresa excluída com sucesso.")


if __name__ == "__main__":
    main()