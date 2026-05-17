from decimal import Decimal
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from repositories.company_repository import list_active_companies
from repositories.settings_repository import get_setting, set_setting
from services.config_service import increment_config_counter
from services.document_generation_service import generate_documents_from_manual_data
from services.file_service import open_path
from utils.company_utils import clean_cnpj
from utils.money_utils import normalize_brl_value
from utils.validation_utils import (
    is_valid_br_date,
    is_valid_brl_money,
    is_valid_cnpj_text,
    is_valid_decimal_number,
)


class ManualGenerationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.last_generated_output_folder = None
        self.output_folder = None
        self.companies = []

        last_output_folder = get_setting("last_output_folder")
        if last_output_folder:
            self.output_folder = Path(last_output_folder)

        self.title_label = QLabel("Geração Manual de Propostas")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Preencha os dados do cliente, selecione um fornecedor e gere documentos comerciais automaticamente."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        self.company_combo = QComboBox()

        self.document_type_combo = QComboBox()
        self.document_type_combo.addItem("Serviço / Service", "NFS")
        self.document_type_combo.addItem("Produto / Product", "NF")

        self.numero_nota_input = QLineEdit()
        self.numero_nota_input.setPlaceholderText("Ex: 00000999")

        self.data_emissao_input = QLineEdit()
        self.data_emissao_input.setPlaceholderText("Ex: 23/01/2026")

        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Ex: Cliente Demonstração Ltda")

        self.client_cnpj_input = QLineEdit()
        self.client_cnpj_input.setPlaceholderText("Somente números/letras")

        self.client_address_input = QLineEdit()
        self.client_address_input.setPlaceholderText("Endereço do cliente")

        self.client_city_input = QLineEdit()
        self.client_city_input.setPlaceholderText("Ex: São Paulo")

        self.item_description_input = QTextEdit()
        self.item_description_input.setPlaceholderText("Descrição do serviço/produto")
        self.item_description_input.setFixedHeight(90)

        self.item_quantity_input = QLineEdit()
        self.item_quantity_input.setText("1")

        self.item_unit_value_input = QLineEdit()
        self.item_unit_value_input.setPlaceholderText("Ex: 7.910,00")

        self.add_item_button = QPushButton("Adicionar item")
        self.add_item_button.clicked.connect(self.add_item)

        self.remove_item_button = QPushButton("Remover item selecionado")
        self.remove_item_button.clicked.connect(self.remove_selected_item)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(
            ["Descrição", "Quantidade", "Valor unitário", "Valor total"]
        )
        self.items_table.setMinimumHeight(220)
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setColumnWidth(0, 480)
        self.items_table.setColumnWidth(1, 120)
        self.items_table.setColumnWidth(2, 140)
        self.items_table.setColumnWidth(3, 140)

        self.select_output_button = QPushButton("Selecionar pasta de saída")
        self.select_output_button.clicked.connect(self.select_output_folder)

        if self.output_folder:
            self.output_label = QLabel(f"Pasta de saída: {self.output_folder}")
        else:
            self.output_label = QLabel("Pasta de saída: nenhuma selecionada")
        self.output_label.setObjectName("MutedText")

        self.generate_button = QPushButton("Gerar documentos")
        self.generate_button.clicked.connect(self.generate_documents)

        self.open_output_button = QPushButton("Abrir última pasta gerada")
        self.open_output_button.clicked.connect(self.open_last_generated_output_folder)
        self.open_output_button.setEnabled(False)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMinimumHeight(150)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)

        top_grid = QGridLayout()
        top_grid.setSpacing(16)
        top_grid.addWidget(self.create_main_data_card(), 0, 0)
        top_grid.addWidget(self.create_client_card(), 0, 1)

        main_layout.addLayout(top_grid)
        main_layout.addWidget(self.create_items_card(), stretch=3)
        main_layout.addWidget(self.create_actions_card(), stretch=2)

        self.setLayout(main_layout)

        self.load_companies()

    def create_card(self, title_text: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("Card")

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        layout.addWidget(title)

        card.setLayout(layout)

        return card, layout

    def create_field(self, label_text: str, widget: QWidget) -> QVBoxLayout:
        label = QLabel(label_text)
        label.setObjectName("FieldLabel")

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addWidget(label)
        layout.addWidget(widget)

        return layout

    def create_main_data_card(self) -> QFrame:
        card, layout = self.create_card("Dados principais")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addLayout(self.create_field("Fornecedor", self.company_combo), 0, 0, 1, 2)
        grid.addLayout(self.create_field("Tipo de proposta", self.document_type_combo), 1, 0, 1, 2)
        grid.addLayout(self.create_field("Número do documento", self.numero_nota_input), 2, 0)
        grid.addLayout(self.create_field("Data", self.data_emissao_input), 2, 1)

        layout.addLayout(grid)

        return card

    def create_client_card(self) -> QFrame:
        card, layout = self.create_card("Dados do cliente")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addLayout(self.create_field("Nome do cliente", self.client_name_input), 0, 0, 1, 2)
        grid.addLayout(self.create_field("CNPJ/Identificador", self.client_cnpj_input), 1, 0)
        grid.addLayout(self.create_field("Município", self.client_city_input), 1, 1)
        grid.addLayout(self.create_field("Endereço", self.client_address_input), 2, 0, 1, 2)

        layout.addLayout(grid)

        return card

    def create_items_card(self) -> QFrame:
        card, layout = self.create_card("Itens da proposta")

        item_grid = QGridLayout()
        item_grid.setSpacing(12)

        item_grid.addLayout(self.create_field("Descrição", self.item_description_input), 0, 0, 2, 1)
        item_grid.addLayout(self.create_field("Quantidade", self.item_quantity_input), 0, 1)
        item_grid.addLayout(self.create_field("Valor unitário", self.item_unit_value_input), 1, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_item_button)
        buttons_layout.addWidget(self.remove_item_button)
        buttons_layout.addStretch()

        layout.addLayout(item_grid)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.items_table)

        return card

    def create_actions_card(self) -> QFrame:
        card, layout = self.create_card("Ações e status")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_output_button)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.open_output_button)

        layout.addLayout(buttons_layout)
        layout.addWidget(self.output_label)
        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.logs)

        return card

    def log(self, message: str):
        self.logs.append(message)

    def load_companies(self):
        self.company_combo.clear()
        self.companies = list_active_companies()

        for company in self.companies:
            label = f"{company['razao_social']} - {company['cnpj']}"
            self.company_combo.addItem(label, company)

    def select_output_folder(self):
        start_folder = str(self.output_folder) if self.output_folder else ""

        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta de saída",
            start_folder,
        )

        if not folder:
            return

        self.output_folder = Path(folder)
        self.output_label.setText(f"Pasta de saída: {self.output_folder}")

        set_setting("last_output_folder", str(self.output_folder))

        self.log("Pasta de saída selecionada.")

    def validate_form(self) -> bool:
        required_fields = [
            ("Número do documento", self.numero_nota_input),
            ("Data", self.data_emissao_input),
            ("Nome do cliente", self.client_name_input),
            ("CNPJ/Identificador do cliente", self.client_cnpj_input),
            ("Endereço do cliente", self.client_address_input),
            ("Município do cliente", self.client_city_input),
        ]

        for field_name, field in required_fields:
            if not field.text().strip():
                QMessageBox.warning(
                    self,
                    "Campo obrigatório",
                    f"O campo '{field_name}' é obrigatório.",
                )
                return False

        if not is_valid_br_date(self.data_emissao_input.text()):
            QMessageBox.warning(
                self,
                "Data inválida",
                "A data deve estar no formato dd/mm/aaaa. Exemplo: 23/01/2026.",
            )
            return False

        if not is_valid_cnpj_text(self.client_cnpj_input.text()):
            QMessageBox.warning(
                self,
                "Identificador inválido",
                "O CNPJ/identificador do cliente deve ter exatamente 14 letras/números.",
            )
            return False

        if not self.output_folder:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione uma pasta de saída.",
            )
            return False

        if self.company_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Atenção",
                "Cadastre ou selecione um fornecedor.",
            )
            return False

        if self.items_table.rowCount() == 0:
            QMessageBox.warning(
                self,
                "Atenção",
                "Adicione pelo menos um item antes de gerar os documentos.",
            )
            return False

        return True

    def calculate_item_total(self, quantidade: str, valor_unitario: str) -> str:
        quantidade_decimal = Decimal(quantidade.replace(",", "."))
        valor_unitario_decimal = Decimal(
            normalize_brl_value(valor_unitario).replace(".", "").replace(",", ".")
        )

        valor_total = quantidade_decimal * valor_unitario_decimal

        return normalize_brl_value(str(valor_total).replace(".", ","))

    def add_item(self):
        descricao = " ".join(self.item_description_input.toPlainText().split())
        quantidade = self.item_quantity_input.text().strip()
        valor_unitario = self.item_unit_value_input.text().strip()

        if not descricao:
            QMessageBox.warning(
                self,
                "Campo obrigatório",
                "Informe a descrição do item.",
            )
            return

        if not quantidade:
            QMessageBox.warning(
                self,
                "Campo obrigatório",
                "Informe a quantidade.",
            )
            return

        if not valor_unitario:
            QMessageBox.warning(
                self,
                "Campo obrigatório",
                "Informe o valor unitário.",
            )
            return

        if not is_valid_decimal_number(quantidade):
            QMessageBox.warning(
                self,
                "Quantidade inválida",
                "A quantidade deve ser um número maior que zero. Exemplo: 1, 2 ou 1,5.",
            )
            return

        if not is_valid_brl_money(valor_unitario):
            QMessageBox.warning(
                self,
                "Valor inválido",
                "O valor unitário deve ser maior que zero. Exemplo: 7.910,00.",
            )
            return

        try:
            valor_unitario_normalizado = normalize_brl_value(valor_unitario)
            valor_total = self.calculate_item_total(
                quantidade=quantidade,
                valor_unitario=valor_unitario_normalizado,
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Valor inválido",
                f"Confira a quantidade e o valor unitário.\nErro: {error}",
            )
            return

        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        self.items_table.setItem(row, 0, QTableWidgetItem(descricao))
        self.items_table.setItem(row, 1, QTableWidgetItem(quantidade))
        self.items_table.setItem(row, 2, QTableWidgetItem(valor_unitario_normalizado))
        self.items_table.setItem(row, 3, QTableWidgetItem(valor_total))

        self.item_description_input.clear()
        self.item_quantity_input.setText("1")
        self.item_unit_value_input.clear()

        self.log(f"Item adicionado. Total do item: R$ {valor_total}")

    def remove_selected_item(self):
        selected_row = self.items_table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um item para remover.",
            )
            return

        self.items_table.removeRow(selected_row)
        self.log("Item removido.")

    def build_manual_data(self) -> dict:
        fornecedor = self.company_combo.currentData()

        itens = []

        for row in range(self.items_table.rowCount()):
            descricao = self.items_table.item(row, 0).text()
            quantidade = self.items_table.item(row, 1).text()
            valor_unitario = self.items_table.item(row, 2).text()
            valor_total = self.items_table.item(row, 3).text()

            itens.append(
                {
                    "quantidade": quantidade,
                    "descricao": descricao,
                    "valor_unitario": valor_unitario,
                    "valor_total": valor_total,
                }
            )

        total_decimal = Decimal("0")

        for item in itens:
            total_decimal += Decimal(
                item["valor_total"].replace(".", "").replace(",", ".")
            )

        valor_total_servico = normalize_brl_value(
            str(total_decimal).replace(".", ",")
        )

        return {
            "tipo_documento": self.document_type_combo.currentData(),
            "numero_nota": self.numero_nota_input.text().strip(),
            "data_emissao": self.data_emissao_input.text().strip(),
            "valor_total_servico": valor_total_servico,
            "prestador": {
                "cnpj": fornecedor["cnpj"],
                "razao_social": fornecedor["razao_social"],
                "endereco": fornecedor["endereco"],
            },
            "tomador": {
                "cnpj": clean_cnpj(self.client_cnpj_input.text()),
                "razao_social": self.client_name_input.text().strip(),
                "endereco": self.client_address_input.text().strip(),
                "municipio": self.client_city_input.text().strip(),
            },
            "itens": itens,
        }

    def generate_documents(self):
        if not self.validate_form():
            return

        self.generate_button.setEnabled(False)
        self.generate_button.setText("Gerando...")

        try:
            self.log("=" * 60)
            self.log("Iniciando geração manual...")

            manual_data = self.build_manual_data()

            tipo = "Serviço" if manual_data["tipo_documento"] == "NFS" else "Produto"
            self.log(f"Tipo selecionado: {tipo}")

            result = generate_documents_from_manual_data(
                manual_data=manual_data,
                output_base_folder=self.output_folder,
            )

            self.last_generated_output_folder = result["output_folder"]
            self.open_output_button.setEnabled(True)

            self.log(f"Arquivos gerados: {len(result['generated_files'])}")
            self.log("Geração manual concluída com sucesso.")

            if manual_data["tipo_documento"] == "NFS":
                increment_config_counter("dashboard_nfs_generated_count")

            if manual_data["tipo_documento"] == "NF":
                increment_config_counter("dashboard_nf_generated_count")

            QMessageBox.information(
                self,
                "Concluído",
                "Documentos gerados com sucesso.",
            )

        except Exception as error:
            self.log(f"Erro: {error}")
            QMessageBox.critical(
                self,
                "Erro",
                f"Ocorreu um erro:\n{error}",
            )

        finally:
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Gerar documentos")

    def open_last_generated_output_folder(self):
        if not self.last_generated_output_folder:
            QMessageBox.warning(
                self,
                "Atenção",
                "Nenhuma pasta gerada ainda.",
            )
            return

        try:
            open_path(self.last_generated_output_folder)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível abrir a pasta:\n{error}",
            )