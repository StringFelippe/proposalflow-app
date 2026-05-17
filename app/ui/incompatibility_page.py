from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from repositories.company_repository import (
    create_incompatibility,
    list_active_companies,
    list_incompatibilities,
    remove_incompatibility,
)


class IncompatibilityPage(QWidget):
    def __init__(self):
        super().__init__()

        self.companies = []

        self.title_label = QLabel("Regras de Combinação")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Defina fornecedores que não devem ser combinados em fluxos comerciais, simulações ou demonstrações."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        self.company_a_combo = QComboBox()
        self.company_b_combo = QComboBox()

        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Motivo opcional")
        self.reason_input.setFixedHeight(90)

        self.add_button = QPushButton("Adicionar regra")
        self.add_button.clicked.connect(self.add_incompatibility)

        self.remove_button = QPushButton("Remover selecionada")
        self.remove_button.clicked.connect(self.remove_selected_incompatibility)

        self.refresh_button = QPushButton("Atualizar lista")
        self.refresh_button.clicked.connect(self.refresh_page)

        self.incompatibilities_list = QListWidget()
        self.incompatibilities_list.setMinimumHeight(320)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)

        content_grid = QGridLayout()
        content_grid.setSpacing(16)
        content_grid.addWidget(self.create_rule_card(), 0, 0)
        content_grid.addWidget(self.create_list_card(), 0, 1)
        content_grid.setColumnStretch(0, 2)
        content_grid.setColumnStretch(1, 3)

        main_layout.addLayout(content_grid)
        main_layout.addWidget(self.create_help_card())

        self.setLayout(main_layout)

        self.load_companies()
        self.load_incompatibilities()

    # =========================
    # UI helpers
    # =========================

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

    def create_rule_card(self) -> QFrame:
        card, layout = self.create_card("Criar regra")

        layout.addLayout(self.create_field("Fornecedor A", self.company_a_combo))
        layout.addLayout(self.create_field("Fornecedor B", self.company_b_combo))
        layout.addLayout(self.create_field("Motivo", self.reason_input))

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.add_button)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        return card

    def create_list_card(self) -> QFrame:
        card, layout = self.create_card("Regras cadastradas")

        helper = QLabel(
            "Selecione uma regra na lista para remover. "
            "Essas regras demonstram como o app pode aplicar restrições comerciais entre fornecedores."
        )
        helper.setObjectName("MutedText")
        helper.setWordWrap(True)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.refresh_button)
        actions_layout.addWidget(self.remove_button)
        actions_layout.addStretch()

        layout.addWidget(helper)
        layout.addLayout(actions_layout)
        layout.addWidget(self.incompatibilities_list)

        return card

    def create_help_card(self) -> QFrame:
        card, layout = self.create_card("Como essa regra funciona")

        text = QLabel(
            "Quando dois fornecedores são marcados como incompatíveis, o sistema registra que eles não devem "
            "ser combinados em fluxos comerciais específicos. Na versão pública do ProposalFlow, essa tela "
            "serve como demonstração de regra de negócio cadastrável e persistida em banco SQLite."
        )
        text.setObjectName("MutedText")
        text.setWordWrap(True)

        layout.addWidget(text)

        return card

    # =========================
    # Lógica
    # =========================

    def refresh_page(self):
        self.load_companies()
        self.load_incompatibilities()

    def load_companies(self):
        self.companies = list_active_companies()

        self.company_a_combo.clear()
        self.company_b_combo.clear()

        for company in self.companies:
            label = f"{company['razao_social']} - {company['cnpj']}"
            self.company_a_combo.addItem(label, company["cnpj"])
            self.company_b_combo.addItem(label, company["cnpj"])

    def load_incompatibilities(self):
        self.incompatibilities_list.clear()

        incompatibilities = list_incompatibilities()

        for item in incompatibilities:
            label = (
                f"{item['empresa_a_nome']} ({item['empresa_a_cnpj']}) "
                f"↔ {item['empresa_b_nome']} ({item['empresa_b_cnpj']})"
            )

            if item.get("motivo"):
                label += f" | Motivo: {item['motivo']}"

            self.incompatibilities_list.addItem(label)

            list_item = self.incompatibilities_list.item(
                self.incompatibilities_list.count() - 1
            )
            list_item.setData(
                1000,
                {
                    "empresa_a_cnpj": item["empresa_a_cnpj"],
                    "empresa_b_cnpj": item["empresa_b_cnpj"],
                },
            )

    def add_incompatibility(self):
        empresa_a_cnpj = self.company_a_combo.currentData()
        empresa_b_cnpj = self.company_b_combo.currentData()
        motivo = self.reason_input.toPlainText().strip()

        if not empresa_a_cnpj or not empresa_b_cnpj:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione dois fornecedores.",
            )
            return

        if empresa_a_cnpj == empresa_b_cnpj:
            QMessageBox.warning(
                self,
                "Atenção",
                "Um fornecedor não pode ser incompatível com ele mesmo.",
            )
            return

        create_incompatibility(
            empresa_a_cnpj=empresa_a_cnpj,
            empresa_b_cnpj=empresa_b_cnpj,
            motivo=motivo,
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Regra cadastrada com sucesso.",
        )

        self.reason_input.clear()
        self.load_incompatibilities()

    def remove_selected_incompatibility(self):
        selected_item = self.incompatibilities_list.currentItem()

        if not selected_item:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione uma regra para remover.",
            )
            return

        data = selected_item.data(1000)

        confirm = QMessageBox.question(
            self,
            "Confirmar remoção",
            "Deseja remover esta regra de combinação?",
        )

        if confirm != QMessageBox.Yes:
            return

        remove_incompatibility(
            empresa_a_cnpj=data["empresa_a_cnpj"],
            empresa_b_cnpj=data["empresa_b_cnpj"],
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Regra removida com sucesso.",
        )

        self.load_incompatibilities()