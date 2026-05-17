from pathlib import Path

from services.budget_builder import build_budget_data
from services.company_registration_validator import raise_if_main_company_not_registered
from services.exceptions import CompanyNotRegisteredError
from services.extracted_data_validator import raise_if_invalid_extracted_data
from services.pdf_reader import extract_text_from_pdf
from services.text_parser import parse_text
from services.word_generator import generate_word_from_template
from utils.path_utils import build_school_folder_name
from utils.resource_path import get_resource_path


def normalize_output_base_folder(output_base_folder: str | Path) -> Path:
    output_base_folder = Path(output_base_folder)

    if output_base_folder.name.lower() in ["orçamentos gerados", "propostas geradas"]:
        return output_base_folder.parent

    return output_base_folder


def clean_filename_text(text: str) -> str:
    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        text = text.replace(char, "")

    return " ".join(text.split()).strip()


def build_document_filename(prefix: str, client_name: str, document_number: str) -> str:
    client_name = clean_filename_text(client_name)

    if len(client_name) > 45:
        client_name = client_name[:45].strip()

    document_number = str(document_number).lstrip("0") or "0"
    document_number = document_number.zfill(3)

    return f"{prefix} - {client_name} - DOC {document_number}.docx"


def get_proposal_templates() -> dict:
    templates_folder = get_resource_path("app/templates")

    return {
        "proposta_completa": templates_folder / "proposta_completa.docx",
        "proposta_simples": templates_folder / "proposta_simples.docx",
        "resumo_tecnico": templates_folder / "resumo_tecnico.docx",
        "declaracao_comercial": templates_folder / "declaracao_comercial.docx",
    }


def validate_templates_exist(templates: dict) -> None:
    missing_templates = []

    for name, path in templates.items():
        if not path.exists():
            missing_templates.append(f"{name}: {path}")

    if missing_templates:
        missing_text = "\n".join(missing_templates)
        raise FileNotFoundError(
            "Templates obrigatórios não encontrados:\n"
            f"{missing_text}"
        )


def generate_documents_from_budget_data(
    budget_data_1: dict,
    output_base_folder: str | Path,
    pdf_path: str | Path | None = None,
    budget_template_type: str = "completo",
) -> dict:
    output_base_folder = normalize_output_base_folder(output_base_folder)

    templates = get_proposal_templates()
    validate_templates_exist(templates)

    client_name = budget_data_1["apm"]["nome"]
    document_number = budget_data_1["numero_nota"]

    client_folder_name = build_school_folder_name(client_name)

    output_folder = (
        output_base_folder
        / "propostas geradas"
        / client_folder_name
    )

    output_folder.mkdir(parents=True, exist_ok=True)

    files_to_generate = [
        {
            "template": templates["proposta_completa"],
            "output": output_folder / build_document_filename(
                prefix="Proposta Completa",
                client_name=client_name,
                document_number=document_number,
            ),
            "context": budget_data_1,
        },
        {
            "template": templates["proposta_simples"],
            "output": output_folder / build_document_filename(
                prefix="Proposta Simples",
                client_name=client_name,
                document_number=document_number,
            ),
            "context": budget_data_1,
        },
        {
            "template": templates["resumo_tecnico"],
            "output": output_folder / build_document_filename(
                prefix="Resumo Técnico",
                client_name=client_name,
                document_number=document_number,
            ),
            "context": budget_data_1,
        },
        {
            "template": templates["declaracao_comercial"],
            "output": output_folder / build_document_filename(
                prefix="Declaração Comercial",
                client_name=client_name,
                document_number=document_number,
            ),
            "context": budget_data_1,
        },
    ]

    generated_files = []

    for document in files_to_generate:
        generate_word_from_template(
            template_path=str(document["template"]),
            output_path=str(document["output"]),
            context=document["context"],
        )

        generated_files.append(document["output"])

    return {
        "document_type": budget_data_1.get("tipo_documento"),
        "output_folder": output_folder,
        "execution_log_path": None,
        "generated_files": generated_files,
        "budget_data_1": budget_data_1,
        "budget_data_2": None,
        "budget_data_3": None,
    }


def generate_documents_from_pdf(
    pdf_path: str | Path,
    output_base_folder: str | Path,
    budget_template_type: str = "completo",
) -> dict:
    pdf_path = Path(pdf_path)
    output_base_folder = normalize_output_base_folder(output_base_folder)

    text = extract_text_from_pdf(str(pdf_path))

    extracted_data = parse_text(text)
    raise_if_invalid_extracted_data(extracted_data)
    raise_if_main_company_not_registered(extracted_data)

    budget_data_1 = build_budget_data(extracted_data)

    result = generate_documents_from_budget_data(
        budget_data_1=budget_data_1,
        output_base_folder=output_base_folder,
        pdf_path=pdf_path,
        budget_template_type=budget_template_type,
    )

    result.update(
        {
            "pdf_path": pdf_path,
            "text_output_path": None,
        }
    )

    return result


def generate_documents_from_multiple_pdfs(
    pdf_paths: list[str | Path],
    output_base_folder: str | Path,
    budget_template_type: str = "completo",
) -> dict:
    output_base_folder = normalize_output_base_folder(output_base_folder)

    results = []
    successful = []
    failed = []

    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)

        try:
            result = generate_documents_from_pdf(
                pdf_path=pdf_path,
                output_base_folder=output_base_folder,
                budget_template_type=budget_template_type,
            )

            success_result = {
                "pdf_path": pdf_path,
                "document_type": result.get("document_type"),
                "status": "success",
                "message": "Documentos gerados com sucesso.",
                "output_folder": result["output_folder"],
                "execution_log_path": result.get("execution_log_path"),
                "generated_files": result["generated_files"],
            }

            results.append(success_result)
            successful.append(success_result)

        except CompanyNotRegisteredError as error:
            error_result = {
                "pdf_path": pdf_path,
                "status": "error",
                "error_type": "company_not_registered",
                "message": str(error),
                "company_data": error.company_data,
                "output_folder": None,
                "execution_log_path": None,
                "generated_files": [],
            }

            results.append(error_result)
            failed.append(error_result)

        except Exception as error:
            error_result = {
                "pdf_path": pdf_path,
                "status": "error",
                "error_type": "general_error",
                "message": str(error),
                "output_folder": None,
                "execution_log_path": None,
                "generated_files": [],
            }

            results.append(error_result)
            failed.append(error_result)

    return {
        "total": len(pdf_paths),
        "success_count": len(successful),
        "error_count": len(failed),
        "results": results,
        "successful": successful,
        "failed": failed,
    }


def generate_documents_from_manual_data(
    manual_data: dict,
    output_base_folder: str | Path,
) -> dict:
    extracted_data = {
        "tipo_documento": manual_data.get("tipo_documento", "NFS"),
        "numero_nota": manual_data["numero_nota"],
        "data_emissao": manual_data["data_emissao"],
        "valor_total_servico": manual_data["valor_total_servico"],
        "prestador": {
            "cnpj": manual_data["prestador"]["cnpj"],
            "razao_social": manual_data["prestador"]["razao_social"],
            "endereco": manual_data["prestador"]["endereco"],
        },
        "tomador": {
            "cnpj": manual_data["tomador"]["cnpj"],
            "razao_social": manual_data["tomador"]["razao_social"],
            "endereco": manual_data["tomador"]["endereco"],
            "municipio": manual_data["tomador"]["municipio"],
        },
        "itens": manual_data["itens"],
    }

    raise_if_invalid_extracted_data(extracted_data)

    budget_data_1 = build_budget_data(extracted_data)

    result = generate_documents_from_budget_data(
        budget_data_1=budget_data_1,
        output_base_folder=output_base_folder,
        pdf_path=None,
        budget_template_type=manual_data.get("budget_template_type", "completo"),
    )

    result.update(
        {
            "mode": "manual",
        }
    )

    return result