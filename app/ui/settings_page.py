from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.config_service import get_config_value, set_config_value


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.title_label = QLabel("Configurações")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Ajuste regras de cálculo, datas e aparência dos documentos gerados."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        self.min_percentage_input = QLineEdit()
        self.min_percentage_input.setPlaceholderText("Ex: 18")

        self.max_percentage_input = QLineEdit()
        self.max_percentage_input.setPlaceholderText("Ex: 24")

        self.budget_days_input = QLineEdit()
        self.budget_days_input.setPlaceholderText("Ex: 10")

        self.comparative_days_input = QLineEdit()
        self.comparative_days_input.setPlaceholderText("Ex: 1")

        self.image_width_input = QLineEdit()
        self.image_width_input.setPlaceholderText("Ex: 190")

        self.save_button = QPushButton("Salvar configurações")
        self.save_button.clicked.connect(self.save_settings)

        self.reload_button = QPushButton("Recarregar valores")
        self.reload_button.clicked.connect(self.load_settings)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)

        content_grid = QGridLayout()
        content_grid.setSpacing(16)
        content_grid.addWidget(self.create_value_rules_card(), 0, 0)
        content_grid.addWidget(self.create_documents_card(), 0, 1)
        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 1)

        main_layout.addLayout(content_grid)
        main_layout.addWidget(self.create_help_card())
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.load_settings()

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

    def create_field(self, label_text: str, widget: QWidget, helper_text: str = "") -> QVBoxLayout:
        label = QLabel(label_text)
        label.setObjectName("FieldLabel")

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addWidget(label)
        layout.addWidget(widget)

        if helper_text:
            helper = QLabel(helper_text)
            helper.setObjectName("MutedText")
            helper.setWordWrap(True)
            layout.addWidget(helper)

        return layout

    def create_value_rules_card(self) -> QFrame:
        card, layout = self.create_card("Regras de valor")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addLayout(
            self.create_field(
                "Variação mínima (%)",
                self.min_percentage_input,
                "Parâmetro demonstrativo para regras comerciais de variação de valores.",
            ),
            0,
            0,
        )

        grid.addLayout(
            self.create_field(
                "Variação máxima (%)",
                self.max_percentage_input,
                "Parâmetro demonstrativo para regras comerciais de variação de valores.",
            ),
            0,
            1,
        )

        grid.addLayout(
            self.create_field(
                "Intervalo entre documentos",
                self.comparative_days_input,
                "Quantidade de dias usada em fluxos que exigem documentos relacionados.",
            ),
            1,
            0,
            1,
            2,
        )

        layout.addLayout(grid)

        return card

    def create_documents_card(self) -> QFrame:
        card, layout = self.create_card("Datas e documentos")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addLayout(
            self.create_field(
                "Dias antes do documento de entrada",
                self.budget_days_input,
                "Usado para calcular a data base da proposta gerada.",
            ),
            0,
            0,
            1,
            2,
        )

        grid.addLayout(
            self.create_field(
                "Largura da imagem/logo (mm)",
                self.image_width_input,
                "Controla o tamanho da imagem inserida no topo dos documentos Word.",
            ),
            1,
            0,
            1,
            2,
        )

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.reload_button)
        actions_layout.addStretch()

        layout.addLayout(grid)
        layout.addLayout(actions_layout)

        return card

    def create_help_card(self) -> QFrame:
        card, layout = self.create_card("Observações")

        text = QLabel(
            "Essas configurações são salvas no banco de dados local e passam a valer nas próximas gerações. "
            "Na versão pública do ProposalFlow, algumas configurações funcionam como demonstração de parâmetros "
            "editáveis para regras de negócio, datas e aparência dos documentos."
        )
        text.setObjectName("MutedText")
        text.setWordWrap(True)

        layout.addWidget(text)

        return card

    # =========================
    # Lógica
    # =========================

    def load_settings(self):
        self.min_percentage_input.setText(
            get_config_value("comparative_min_percentage")
        )
        self.max_percentage_input.setText(
            get_config_value("comparative_max_percentage")
        )
        self.budget_days_input.setText(
            get_config_value("budget_days_before_invoice")
        )
        self.comparative_days_input.setText(
            get_config_value("comparative_budget_days_before")
        )
        self.image_width_input.setText(
            get_config_value("header_image_width_mm")
        )

    def validate_settings(self) -> bool:
        try:
            min_percentage = float(self.min_percentage_input.text().replace(",", "."))
            max_percentage = float(self.max_percentage_input.text().replace(",", "."))
            budget_days = int(self.budget_days_input.text())
            comparative_days = int(self.comparative_days_input.text())
            image_width = int(self.image_width_input.text())

            if min_percentage <= 0 or max_percentage <= 0:
                raise ValueError("Percentuais devem ser maiores que zero.")

            if min_percentage > max_percentage:
                raise ValueError("O percentual mínimo não pode ser maior que o máximo.")

            if budget_days < 0:
                raise ValueError("Dias antes do documento não pode ser negativo.")

            if comparative_days < 0:
                raise ValueError("Intervalo entre documentos não pode ser negativo.")

            if image_width <= 0:
                raise ValueError("Largura da imagem deve ser maior que zero.")

            return True

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Configuração inválida",
                str(error),
            )
            return False

    def save_settings(self):
        if not self.validate_settings():
            return

        set_config_value(
            "comparative_min_percentage",
            self.min_percentage_input.text().replace(",", "."),
        )
        set_config_value(
            "comparative_max_percentage",
            self.max_percentage_input.text().replace(",", "."),
        )
        set_config_value(
            "budget_days_before_invoice",
            self.budget_days_input.text(),
        )
        set_config_value(
            "comparative_budget_days_before",
            self.comparative_days_input.text(),
        )
        set_config_value(
            "header_image_width_mm",
            self.image_width_input.text(),
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Configurações salvas com sucesso.",
        )