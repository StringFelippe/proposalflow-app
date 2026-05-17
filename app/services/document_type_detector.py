def detect_document_type(text: str) -> str:
    normalized_text = text.upper()

    if (
        "NOTA FISCAL ELETRÔNICA DE SERVIÇOS" in normalized_text
        or "NFS-E" in normalized_text
        or "PRESTADOR DE SERVIÇOS" in normalized_text
        or "TOMADOR DE SERVIÇOS" in normalized_text
    ):
        return "NFS"

    if (
        "DANFE" in normalized_text
        or "DESTINATÁRIO / REMETENTE" in normalized_text
        or "DADOS DO PRODUTO / SERVIÇOS" in normalized_text
        or "VALOR TOTAL DA NOTA" in normalized_text
    ):
        return "NF"

    raise ValueError("Tipo de documento não identificado. Verifique se é uma NFS-e ou NF-e.")