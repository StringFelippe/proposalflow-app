import re

from utils.money_utils import normalize_brl_value


def _search(pattern: str, text: str, flags=re.MULTILINE) -> str:
    match = re.search(pattern, text, flags)

    if not match:
        return ""

    return match.group(1).strip()


def parse_nf_text(text: str) -> dict:
    numero_nota = parse_nf_number(text)
    data_emissao = parse_nf_date(text)

    prestador = parse_nf_prestador(text)
    tomador = parse_nf_tomador(text)
    itens = parse_nf_items(text)

    valor_total_servico = normalize_brl_value(
        _search(
            r"VALOR TOTAL DA NOTA\s+([\d.,]+)",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
    )

    return {
        "tipo_documento": "NF",
        "numero_nota": numero_nota,
        "data_emissao": data_emissao,
        "valor_total_servico": valor_total_servico,
        "prestador": prestador,
        "tomador": tomador,
        "itens": itens,
    }


def parse_nf_number(text: str) -> str:
    number = _search(
        r"N[º°]\s*([\d.]+)",
        text,
        flags=re.IGNORECASE,
    )

    return number.replace(".", "")


def parse_nf_date(text: str) -> str:
    date = _search(
        r"DATA DA EMISSÃO\s+.*?(\d{2}/\d{2}/\d{4})",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if date:
        return date

    return _search(
        r"EMISSÃO:\s*(\d{2}/\d{2}/\d{4})",
        text,
        flags=re.IGNORECASE,
    )


def parse_nf_prestador(text: str) -> dict:
    razao_social = _search(
        r"DANFE\s+(.*?)\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not razao_social:
        razao_social = _search(
            r"RECEBEMOS DE\s+(.*?)\s+OS PRODUTOS",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

    endereco = _search(
        r"(Rua .*?-\s*SP)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    cnpj = _search(
        r"INSCRIÇÃO ESTADUAL.*?CNPJ / CPF\s+.*?([\d./-]{18})",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not cnpj:
        cnpj = _search(
            r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
            text,
            flags=re.IGNORECASE,
        )

    return {
        "cnpj": cnpj,
        "razao_social": " ".join(razao_social.split()),
        "endereco": " ".join(endereco.split()),
    }


def parse_nf_tomador(text: str) -> dict:
    section = _search(
        r"DESTINATÁRIO / REMETENTE(.*?)PAGAMENTO",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    razao_social = _search(
        r"NOME / RAZÃO SOCIAL.*?\n\s*(.*?)\s+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
        section,
        flags=re.DOTALL | re.IGNORECASE,
    )

    cnpj = _search(
        r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
        section,
        flags=re.IGNORECASE,
    )

    endereco = _search(
        r"ENDEREÇO.*?\n\s*(.*?)\s{2,}",
        section,
        flags=re.DOTALL | re.IGNORECASE,
    )

    municipio = _search(
        r"MUNICÍPIO.*?\n\s*(.*?)\s+SP",
        section,
        flags=re.DOTALL | re.IGNORECASE,
    )

    return {
        "cnpj": cnpj,
        "razao_social": " ".join(razao_social.split()),
        "endereco": " ".join(endereco.split()),
        "municipio": " ".join(municipio.split()),
    }


def parse_nf_items(text: str) -> list[dict]:
    section = _search(
        r"DADOS DO PRODUTO / SERVIÇOS(.*?)DADOS ADICIONAIS",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not section:
        return []

    lines = [
        " ".join(line.split())
        for line in section.splitlines()
        if line.strip()
    ]

    item_start_pattern = re.compile(r"^\d+\s+")
    item_lines = []

    current_item = ""

    for line in lines:
        if is_header_line(line):
            continue

        if item_start_pattern.match(line):
            if current_item:
                item_lines.append(current_item)

            current_item = line
        else:
            if current_item:
                current_item += " " + line

    if current_item:
        item_lines.append(current_item)

    items = []

    for item_line in item_lines:
        item = parse_nf_item_line(item_line)

        if item:
            items.append(item)

    return items


def is_header_line(line: str) -> bool:
    upper_line = line.upper()

    ignored_terms = [
        "CÓDIGO",
        "/ SERV.",
        "DESCRIÇÃO DO PRODUTO",
        "NCM / SH",
        "CSOSN",
        "CFOP",
        "UNID.",
        "QUANT.",
        "UNITÁRIO",
        "VALORTOTAL",
        "DESCONTO",
        "CÁLC.BASEICMS",
        "ICMSALÍQUOTASIPI",
    ]

    return any(term in upper_line for term in ignored_terms)


def parse_nf_item_line(line: str) -> dict | None:
    pattern = re.compile(
        r"^(?P<codigo>\d+)\s+"
        r"(?P<descricao>.*?)\s+"
        r"(?P<ncm>\d{8})\s+"
        r"(?P<csosn>\d{4})\s+"
        r"(?P<cfop>\d{4})\s+"
        r"(?P<unidade>[A-Z]+)\s+"
        r"(?P<quantidade>[\d.,]+)\s+"
        r"(?P<valor_unitario>[\d.,]+)\s+"
        r"(?P<valor_total>[\d.,]+)",
        re.IGNORECASE,
    )

    match = pattern.search(line)

    if not match:
        return None

    quantidade = normalize_quantity(match.group("quantidade"))
    valor_unitario = normalize_brl_value(match.group("valor_unitario"))
    valor_total = normalize_brl_value(match.group("valor_total"))

    return {
        "quantidade": quantidade,
        "descricao": " ".join(match.group("descricao").split()),
        "valor_unitario": valor_unitario,
        "valor_total": valor_total,
    }


def normalize_quantity(value: str) -> str:
    value = value.strip()

    if "," in value:
        value = value.replace(".", "").replace(",", ".")

    number = float(value)

    if number.is_integer():
        return str(int(number))

    return str(number).replace(".", ",")