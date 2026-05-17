from datetime import datetime
from pathlib import Path


def write_execution_log(
    output_folder: str | Path,
    document_type: str,
    pdf_path: str | Path | None,
    generated_files: list[Path],
    budget_data_1: dict,
    budget_data_2: dict,
    budget_data_3: dict,
) -> Path:
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    log_path = output_folder / "log_execucao.txt"

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    lines = [
        "=" * 80,
        f"Execução em: {now}",
        f"Tipo de documento: {document_type}",
    ]

    if pdf_path:
        lines.append(f"PDF processado: {pdf_path}")

    lines.extend(
        [
            "",
            "Dados principais:",
            f"Número da nota: {budget_data_1.get('numero_nota', '')}",
            f"APM/Escola: {budget_data_1.get('apm', {}).get('nome', '')}",
            f"CNPJ da APM: {budget_data_1.get('apm', {}).get('cnpj_formatado', '')}",
            "",
            "Empresas utilizadas:",
            f"Orçamento 1: {budget_data_1.get('empresa_proponente', {}).get('razao_social', '')}",
            f"Orçamento 2: {budget_data_2.get('empresa_proponente', {}).get('razao_social', '')}",
            f"Orçamento 3: {budget_data_3.get('empresa_proponente', {}).get('razao_social', '')}",
            "",
            "Totais:",
            f"Orçamento 1: R$ {budget_data_1.get('orcamento', {}).get('total', '')}",
            f"Orçamento 2: R$ {budget_data_2.get('orcamento', {}).get('total', '')}",
            f"Orçamento 3: R$ {budget_data_3.get('orcamento', {}).get('total', '')}",
            "",
            "Arquivos gerados:",
        ]
    )

    for file_path in generated_files:
        lines.append(f"- {file_path}")

    lines.extend(["", "=" * 80, ""])

    with open(log_path, "a", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return log_path