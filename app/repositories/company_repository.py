from repositories.database import get_connection


def create_company(company: dict) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO empresas (
                cnpj,
                razao_social,
                endereco,
                endereco_completo,
                telefone,
                responsavel,
                caminho_template,
                caminho_imagem,
                ativa
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company["cnpj"],
                company["razao_social"],
                company["endereco"],
                company.get("endereco_completo", company["endereco"]),
                company.get("telefone", ""),
                company.get("responsavel", ""),
                company.get("caminho_template", ""),
                company.get("caminho_imagem", ""),
                company.get("ativa", 1),
            ),
        )

        connection.commit()


def get_company_by_cnpj(cnpj: str) -> dict | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                cnpj,
                razao_social,
                endereco,
                endereco_completo,
                telefone,
                responsavel,
                caminho_template,
                caminho_imagem,
                ativa
            FROM empresas
            WHERE cnpj = ?
            """,
            (cnpj,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)


def list_active_companies() -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                cnpj,
                razao_social,
                endereco,
                endereco_completo,
                telefone,
                responsavel,
                caminho_template,
                caminho_imagem,
                ativa
            FROM empresas
            WHERE ativa = 1
            ORDER BY razao_social
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

  
def deactivate_company(cnpj: str) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE empresas
            SET ativa = 0
            WHERE cnpj = ?
            """,
            (cnpj,),
        )

        connection.commit()


def create_incompatibility(
    empresa_a_cnpj: str,
    empresa_b_cnpj: str,
    motivo: str = "",
) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO empresas_incompativeis (
                empresa_a_cnpj,
                empresa_b_cnpj,
                motivo
            )
            VALUES (?, ?, ?)
            """,
            (empresa_a_cnpj, empresa_b_cnpj, motivo),
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO empresas_incompativeis (
                empresa_a_cnpj,
                empresa_b_cnpj,
                motivo
            )
            VALUES (?, ?, ?)
            """,
            (empresa_b_cnpj, empresa_a_cnpj, motivo),
        )

        connection.commit()


def remove_incompatibility(
    empresa_a_cnpj: str,
    empresa_b_cnpj: str,
) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM empresas_incompativeis
            WHERE
                (empresa_a_cnpj = ? AND empresa_b_cnpj = ?)
                OR
                (empresa_a_cnpj = ? AND empresa_b_cnpj = ?)
            """,
            (
                empresa_a_cnpj,
                empresa_b_cnpj,
                empresa_b_cnpj,
                empresa_a_cnpj,
            ),
        )

        connection.commit()


def list_incompatible_cnpjs(cnpj: str) -> list[str]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT empresa_b_cnpj
            FROM empresas_incompativeis
            WHERE empresa_a_cnpj = ?
            """,
            (cnpj,),
        )

        rows = cursor.fetchall()

        return [row["empresa_b_cnpj"] for row in rows]
    

def list_incompatibilities() -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                ei.empresa_a_cnpj,
                ea.razao_social AS empresa_a_nome,
                ei.empresa_b_cnpj,
                eb.razao_social AS empresa_b_nome,
                ei.motivo
            FROM empresas_incompativeis ei
            LEFT JOIN empresas ea ON ea.cnpj = ei.empresa_a_cnpj
            LEFT JOIN empresas eb ON eb.cnpj = ei.empresa_b_cnpj
            WHERE ei.empresa_a_cnpj < ei.empresa_b_cnpj
            ORDER BY empresa_a_nome, empresa_b_nome
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]
    

def list_inactive_companies() -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                cnpj,
                razao_social,
                endereco,
                endereco_completo,
                telefone,
                responsavel,
                caminho_template,
                caminho_imagem,
                ativa
            FROM empresas
            WHERE ativa = 0
            ORDER BY razao_social
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def activate_company(cnpj: str) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE empresas
            SET ativa = 1
            WHERE cnpj = ?
            """,
            (cnpj,),
        )

        connection.commit()