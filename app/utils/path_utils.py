import re
import unicodedata


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def sanitize_filename(text: str) -> str:
    text = remove_accents(text)
    text = text.upper().strip()

    # Remove caracteres inválidos no Windows
    text = re.sub(r'[\\/:*?"<>|]', "", text)

    # Remove espaços duplicados
    text = re.sub(r"\s+", " ", text)

    return text


def get_company_short_name(razao_social: str) -> str:
    razao_social = sanitize_filename(razao_social)
    words = razao_social.split()

    if not words:
        return "EMPRESA"

    first_word = words[0]

    if len(first_word) >= 3:
        return first_word

    if len(words) >= 2:
        return f"{words[0]} {words[1]}"

    return first_word


def format_invoice_number(numero_nota: str) -> str:
    number_without_left_zeros = numero_nota.lstrip("0")

    if not number_without_left_zeros:
        number_without_left_zeros = "0"

    return number_without_left_zeros.zfill(3)


def build_document_base_name(razao_social: str, numero_nota: str) -> str:
    company_name = get_company_short_name(razao_social)
    invoice_number = format_invoice_number(numero_nota)

    return f"{company_name} NFS{invoice_number}"


def build_school_folder_name(apm_nome: str) -> str:
    return sanitize_filename(apm_nome)


def build_budget_1_filename(razao_social: str, numero_nota: str) -> str:
    base_name = build_document_base_name(
        razao_social=razao_social,
        numero_nota=numero_nota,
    )

    return f"{base_name}.docx"


def build_comparative_budget_filename(
    razao_social_comparativa: str,
    numero_nota: str,
    razao_social_orcamento_1: str,
) -> str:
    nome_empresa_comparativa = get_company_short_name(razao_social_comparativa)
    numero_formatado = format_invoice_number(numero_nota)
    nome_orcamento_1 = get_company_short_name(razao_social_orcamento_1)

    return f"{nome_empresa_comparativa} {numero_formatado} {nome_orcamento_1}.docx"


def build_anexo_i_filename(razao_social: str, numero_nota: str) -> str:
    company_name = get_company_short_name(razao_social)
    invoice_number = format_invoice_number(numero_nota)

    return f"ANEXO I {company_name} {invoice_number}.docx"


def build_declaracao_i_filename(razao_social: str, numero_nota: str) -> str:
    company_name = get_company_short_name(razao_social)
    invoice_number = format_invoice_number(numero_nota)

    return f"DECLARAÇÃO I {company_name} {invoice_number}.docx"