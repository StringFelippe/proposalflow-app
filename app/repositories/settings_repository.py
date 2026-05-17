from repositories.database import get_connection


def get_setting(key: str, default: str = "") -> str:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = ?
            """,
            (key,),
        )

        row = cursor.fetchone()

        if row is None:
            return default

        return row["valor"]


def set_setting(key: str, value: str) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO configuracoes (
                chave,
                valor
            )
            VALUES (?, ?)
            """,
            (key, value),
        )

        connection.commit()