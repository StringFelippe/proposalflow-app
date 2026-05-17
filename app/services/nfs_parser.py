import re
from utils.money_utils import normalize_brl_value


def _search(pattern: str, text: str, flags=re.MULTILINE) -> str:
    match = re.search(pattern, text, flags)

    if not match:
        return ""

    return match.group(1).strip()


def parse_nfs_text(text: str) -> dict:
    numero_nota = _search(
        r"Número da Nota\s+.*?(\d{6,})",
        text,
        flags=re.DOTALL,
    )

    data_emissao = _search(
        r"Data e Hora de Emissão\s+(\d{2}/\d{2}/\d{4})",
        text,
    )

    prestador_cnpj = _search(
        r"PRESTADOR DE SERVIÇOS\s+CPF/CNPJ:\s*([\d./-]+)",
        text,
        flags=re.DOTALL,
    )

    prestador_nome = _search(
        r"Nome/Razão Social:\s*(.*?)\n",
        text,
    )

    prestador_endereco = _search(
        r"Endereço:\s*(.*?)\n\s*Município:",
        text,
        flags=re.DOTALL,
    )

    tomador_nome = _search(
        r"TOMADOR DE SERVIÇOS\s+Nome/Razão Social:\s*(.*?)\n",
        text,
        flags=re.DOTALL,
    )

    tomador_cnpj = _search(
        r"TOMADOR DE SERVIÇOS.*?CPF/CNPJ:\s*([\d./-]+)",
        text,
        flags=re.DOTALL,
    )

    tomador_endereco = _search(
        r"TOMADOR DE SERVIÇOS.*?Endereço:\s*(.*?)\nMunicípio:",
        text,
        flags=re.DOTALL,
    )

    tomador_municipio = _search(
        r"TOMADOR DE SERVIÇOS.*?Município:\s*(.*?)\s+UF:",
        text,
        flags=re.DOTALL,
    )

    item = parse_item(text)

    valor_total_servico = normalize_brl_value(
    _search(
        r"VALOR TOTAL DO SERVIÇO\s*=\s*R\$\s*([\d.,]+)",
        text,
    )
)

    return {
        "tipo_documento": "NFS",
        "numero_nota": numero_nota,
        "data_emissao": data_emissao,
        "valor_total_servico": valor_total_servico,
        "prestador": {
            "cnpj": prestador_cnpj,
            "razao_social": prestador_nome,
            "endereco": prestador_endereco,
        },
        "tomador": {
            "cnpj": tomador_cnpj,
            "razao_social": tomador_nome,
            "endereco": tomador_endereco,
            "municipio": tomador_municipio,
        },
        "itens": item,
    }


def parse_item(text: str) -> list[dict]:
    structured_items = parse_structured_items(text)

    if structured_items:
        return structured_items

    unstructured_items = parse_unstructured_items(text)

    if unstructured_items:
        return unstructured_items

    return parse_single_description_item(text)


def parse_structured_items(text: str) -> list[dict]:
    pattern = re.compile(
        r"QTDE:\s*(?P<quantidade>[\d.,]+)\s+"
        r"DESCRIÇÃO:\s*(?P<descricao>.*?)\s+"
        r"VL[\s.]?UNIT:\s*R\$\s*(?P<valor_unitario>[\d.,]+)\s+"
        r"VL[\s.]?TOTAL:\s*R\$\s*(?P<valor_total>[\d.,]+)",
        re.DOTALL | re.IGNORECASE,
    )

    items = []

    for match in pattern.finditer(text):
        items.append(
            {
                "quantidade": match.group("quantidade").strip(),
                "descricao": " ".join(match.group("descricao").split()),
                "valor_unitario": normalize_brl_value(match.group("valor_unitario")),
                "valor_total": normalize_brl_value(match.group("valor_total")),
            }
        )

    return items


def parse_unstructured_items(text: str) -> list[dict]:
    services_section = _search(
        r"DISCRIMINAÇÃO DE SERVIÇOS\s*(.*?)\s*VALOR TOTAL DO SERVIÇO",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not services_section:
        return []

    pattern = re.compile(
        r"(?P<descricao>.*?)(?:R\$\s*)(?P<valor_total>[\d.,]+)",
        re.DOTALL | re.IGNORECASE,
    )

    items = []

    for match in pattern.finditer(services_section):
        descricao = " ".join(match.group("descricao").split())
        valor_total = normalize_brl_value(match.group("valor_total"))

        if not descricao:
            continue

        items.append(
            {
                "quantidade": "1",
                "descricao": descricao,
                "valor_unitario": valor_total,
                "valor_total": valor_total,
            }
        )

    return items


def parse_single_description_item(text: str) -> list[dict]:
    services_section = _search(
        r"DISCRIMINAÇÃO DE SERVIÇOS\s*(.*?)\s*VALOR TOTAL DO SERVIÇO",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not services_section:
        return []

    descricao = " ".join(services_section.split())

    if not descricao:
        return []

    valor_total = normalize_brl_value(
        _search(
            r"VALOR TOTAL DO SERVIÇO\s*=\s*R\$\s*([\d.,]+)",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
    )

    if not valor_total:
        return []

    return [
        {
            "quantidade": "1",
            "descricao": descricao,
            "valor_unitario": valor_total,
            "valor_total": valor_total,
        }
    ]