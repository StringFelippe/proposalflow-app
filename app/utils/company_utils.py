import re


def clean_cnpj(value: str) -> str:
    return re.sub(r"[^0-9A-Z]", "", value.strip().upper())


def is_valid_cnpj_raw(value: str) -> bool:
    value = clean_cnpj(value)

    if len(value) != 14:
        return False

    return value.isalnum()


def format_cnpj(value: str) -> str:
    value = clean_cnpj(value)

    if len(value) != 14:
        return value

    return f"{value[0:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:14]}"


def clean_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_phone(value: str) -> bool:
    value = clean_phone(value)

    return len(value) in [10, 11]


def format_phone(value: str) -> str:
    value = clean_phone(value)

    if len(value) == 10:
        return f"({value[0:2]}) {value[2:6]}-{value[6:10]}"

    if len(value) == 11:
        return f"({value[0:2]}) {value[2:7]}-{value[7:11]}"

    return value


def clean_single_line_text(value: str) -> str:
    """
    Limpa textos que precisam ficar em uma única linha no Word.
    Remove quebras de linha, tabs e espaços duplicados.
    """
    if not value:
        return ""

    value = value.replace("\n", " ")
    value = value.replace("\r", " ")
    value = value.replace("\t", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()