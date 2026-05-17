from repositories.database import initialize_database
from services.config_service import set_config_value


def main():
    initialize_database()

    set_config_value("dashboard_nfs_generated_count", "0")
    set_config_value("dashboard_nf_generated_count", "0")

    print("Contadores do dashboard zerados com sucesso.")


if __name__ == "__main__":
    main()