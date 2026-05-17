class CompanyNotRegisteredError(Exception):
    def __init__(self, company_data: dict):
        self.company_data = company_data

        cnpj = company_data.get("cnpj", "")
        razao_social = company_data.get("razao_social", "")

        message = (
            "Empresa prestadora não cadastrada no banco.\n"
            f"CNPJ: {cnpj}\n"
            f"Razão Social: {razao_social}"
        )

        super().__init__(message)