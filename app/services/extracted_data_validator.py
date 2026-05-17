def validate_extracted_data(extracted_data: dict) -> list[str]:
    errors = []

    if not extracted_data.get("tipo_documento"):
        errors.append("Tipo do documento não identificado.")

    if not extracted_data.get("numero_nota"):
        errors.append("Número da nota não encontrado.")

    if not extracted_data.get("data_emissao"):
        errors.append("Data de emissão não encontrada.")

    if not extracted_data.get("valor_total_servico"):
        errors.append("Valor total do serviço/nota não encontrado.")

    prestador = extracted_data.get("prestador", {})
    tomador = extracted_data.get("tomador", {})
    itens = extracted_data.get("itens", [])

    if not prestador.get("cnpj"):
        errors.append("CNPJ do prestador/emitente não encontrado.")

    if not prestador.get("razao_social"):
        errors.append("Razão social do prestador/emitente não encontrada.")

    if not prestador.get("endereco"):
        errors.append("Endereço do prestador/emitente não encontrado.")

    if not tomador.get("cnpj"):
        errors.append("CNPJ do tomador/APM não encontrado.")

    if not tomador.get("razao_social"):
        errors.append("Nome/Razão social do tomador/APM não encontrado.")

    if not tomador.get("endereco"):
        errors.append("Endereço do tomador/APM não encontrado.")

    if not tomador.get("municipio"):
        errors.append("Município do tomador/APM não encontrado.")

    if not itens:
        errors.append("Nenhum item foi encontrado no documento.")

    for index, item in enumerate(itens, start=1):
        if not item.get("descricao"):
            errors.append(f"Item {index}: descrição não encontrada.")

        if not item.get("quantidade"):
            errors.append(f"Item {index}: quantidade não encontrada.")

        if not item.get("valor_unitario"):
            errors.append(f"Item {index}: valor unitário não encontrado.")

        if not item.get("valor_total"):
            errors.append(f"Item {index}: valor total não encontrado.")

    return errors


def raise_if_invalid_extracted_data(extracted_data: dict) -> None:
    errors = validate_extracted_data(extracted_data)

    if errors:
        error_message = "Dados obrigatórios não encontrados:\n- " + "\n- ".join(errors)
        raise ValueError(error_message)