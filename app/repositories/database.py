import sqlite3

from utils.resource_path import get_resource_path


DATA_DIR = get_resource_path("data")
DB_PATH = DATA_DIR / "app.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj TEXT NOT NULL UNIQUE,
                razao_social TEXT NOT NULL,
                endereco TEXT NOT NULL,
                telefone TEXT,
                responsavel TEXT,
                caminho_template TEXT,
                caminho_imagem TEXT,
                ativa INTEGER NOT NULL DEFAULT 1,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS empresas_incompativeis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_a_cnpj TEXT NOT NULL,
                empresa_b_cnpj TEXT NOT NULL,
                motivo TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (empresa_a_cnpj, empresa_b_cnpj)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
            """
        )

        def add_column_if_not_exists(table_name: str, column_name: str, column_definition: str):
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column["name"] for column in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                )


        add_column_if_not_exists(
            table_name="empresas",
            column_name="endereco_completo",
            column_definition="TEXT"
        )

        connection.commit()