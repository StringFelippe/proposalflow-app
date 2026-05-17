from repositories.database import initialize_database, get_connection
from services.config_service import set_config_value


def main():
    initialize_database()

    confirm = input(
        "Isso vai apagar empresas e incompatibilidades do banco demo. Digite SIM para continuar: "
    ).strip()

    if confirm != "SIM":
        print("Operação cancelada.")
        return

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM empresas_incompativeis")
        cursor.execute("DELETE FROM empresas")

        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'empresas_incompativeis'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'empresas'")

        connection.commit()

    set_config_value("dashboard_nfs_generated_count", "0")
    set_config_value("dashboard_nf_generated_count", "0")

    print("Banco demo limpo com sucesso.")
    print("Empresas, incompatibilidades e contadores foram zerados.")


if __name__ == "__main__":
    main()