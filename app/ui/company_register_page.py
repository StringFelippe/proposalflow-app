import shutil
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from repositories.company_repository import (
    activate_company,
    create_company,
    deactivate_company,
    get_company_by_cnpj,
    list_active_companies,
    list_inactive_companies,
)
from utils.company_utils import (
    clean_cnpj,
    clean_phone,
    clean_single_line_text,
    format_cnpj,
    is_valid_cnpj_raw,
    is_valid_phone,
)
from utils.path_utils import get_company_short_name, sanitize_filename
from utils.resource_path import get_base_dir, get_resource_path


BASE_DIR = get_base_dir()
LOGOS_DIR = get_resource_path("app/assets/logos")


class CompanyRegisterPage(QWidget):
    company_saved = Signal()

    def __init__(self, prefill_company_data: dict | None = None):
        super().__init__()

        self.showing_inactive = False

        self.title_label = QLabel("Fornecedores")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Cadastre, edite, desative e reative fornecedores usados na geração das propostas."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        self.notice_label = QLabel("")
        self.notice_label.setObjectName("MutedText")

        self.cnpj_input = QLineEdit()
        self.cnpj_input.setPlaceholderText("14 letras/números, sem pontuação")

        self.razao_social_input = QLineEdit()
        self.razao_social_input.setPlaceholderText("Razão social do fornecedor")

        self.endereco_input = QLineEdit()
        self.endereco_input.setPlaceholderText("Ex: Rua das Inovações, 120")

        self.endereco_completo_input = QLineEdit()
        self.endereco_completo_input.setPlaceholderText(
            "Ex: Rua das Inovações, 120 - Centro - CEP: 01000-000 - São Paulo - SP"
        )

        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("Somente números com DDD")

        self.responsavel_input = QLineEdit()
        self.responsavel_input.setPlaceholderText("Responsável comercial")

        self.imagem_input = QLineEdit()
        self.imagem_input.setPlaceholderText("Caminho da imagem/logo")

        self.select_image_button = QPushButton("Selecionar imagem")
        self.select_image_button.clicked.connect(self.select_image)

        self.save_button = QPushButton("Salvar fornecedor")
        self.save_button.clicked.connect(self.save_company)

        self.clear_button = QPushButton("Limpar formulário")
        self.clear_button.clicked.connect(self.clear_form)

        self.load_selected_button = QPushButton("Carregar selecionado")
        self.load_selected_button.clicked.connect(self.load_selected_company)

        self.deactivate_button = QPushButton("Desativar selecionado")
        self.deactivate_button.clicked.connect(self.deactivate_selected_company)

        self.activate_button = QPushButton("Reativar selecionado")
        self.activate_button.clicked.connect(self.activate_selected_company)

        self.show_inactive_button = QPushButton("Mostrar inativos")
        self.show_inactive_button.clicked.connect(self.load_inactive_companies)

        self.show_active_button = QPushButton("Mostrar ativos")
        self.show_active_button.clicked.connect(self.load_companies)

        self.companies_list = QListWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.notice_label)

        content_grid = QGridLayout()
        content_grid.setSpacing(16)
        content_grid.addWidget(self.create_form_card(), 0, 0)
        content_grid.addWidget(self.create_list_card(), 0, 1)

        content_grid.setColumnStretch(0, 3)
        content_grid.setColumnStretch(1, 2)

        main_layout.addLayout(content_grid)

        self.setLayout(main_layout)

        self.load_companies()

        if prefill_company_data:
            self.prefill_company(prefill_company_data)

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

    def create_form_card(self) -> QFrame:
        card, layout = self.create_card("Cadastro / edição")

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addLayout(self.create_field("CNPJ/Identificador", self.cnpj_input), 0, 0)
        grid.addLayout(self.create_field("Telefone", self.telefone_input), 0, 1)

        grid.addLayout(self.create_field("Razão Social", self.razao_social_input), 1, 0, 1, 2)

        grid.addLayout(
            self.create_field("Endereço para proposta", self.endereco_input),
            2,
            0,
            1,
            2,
        )

        grid.addLayout(
            self.create_field("Endereço completo", self.endereco_completo_input),
            3,
            0,
            1,
            2,
        )

        grid.addLayout(self.create_field("Responsável comercial", self.responsavel_input), 4, 0, 1, 2)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.imagem_input)
        image_layout.addWidget(self.select_image_button)

        image_container = QWidget()
        image_container.setLayout(image_layout)

        grid.addLayout(self.create_field("Imagem / logo", image_container), 5, 0, 1, 2)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.clear_button)
        actions_layout.addStretch()

        layout.addLayout(grid)
        layout.addLayout(actions_layout)

        helper_text = QLabel(
            "Ao selecionar uma imagem, o app copia o arquivo para app/assets/logos "
            "e salva o caminho interno no banco."
        )
        helper_text.setObjectName("MutedText")
        helper_text.setWordWrap(True)

        layout.addWidget(helper_text)

        return card

    def create_list_card(self) -> QFrame:
        card, layout = self.create_card("Fornecedores cadastrados")

        status_text = QLabel(
            "Selecione um fornecedor na lista para carregar, desativar ou reativar."
        )
        status_text.setObjectName("MutedText")
        status_text.setWordWrap(True)

        top_actions = QHBoxLayout()
        top_actions.addWidget(self.show_active_button)
        top_actions.addWidget(self.show_inactive_button)

        selected_actions = QGridLayout()
        selected_actions.setSpacing(10)
        selected_actions.addWidget(self.load_selected_button, 0, 0)
        selected_actions.addWidget(self.deactivate_button, 0, 1)
        selected_actions.addWidget(self.activate_button, 1, 0, 1, 2)

        layout.addWidget(status_text)
        layout.addLayout(top_actions)
        layout.addWidget(self.companies_list)
        layout.addLayout(selected_actions)

        return card

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar imagem/logo",
            "",
            "Imagens (*.png *.jpg *.jpeg)",
        )

        if file_path:
            self.imagem_input.setText(file_path)

    def validate_form(self) -> bool:
        cnpj = self.cnpj_input.text().strip()
        telefone = self.telefone_input.text().strip()

        if not is_valid_cnpj_raw(cnpj):
            QMessageBox.warning(
                self,
                "Identificador inválido",
                "O CNPJ/identificador deve ter exatamente 14 letras/números, sem pontuação.",
            )
            return False

        required_fields = [
            ("Razão Social", self.razao_social_input),
            ("Endereço para proposta", self.endereco_input),
            ("Endereço completo", self.endereco_completo_input),
        ]

        for field_name, field in required_fields:
            if not field.text().strip():
                QMessageBox.warning(
                    self,
                    "Campo obrigatório",
                    f"O campo '{field_name}' é obrigatório.",
                )
                return False

        if telefone and not is_valid_phone(telefone):
            QMessageBox.warning(
                self,
                "Telefone inválido",
                "O telefone deve ter 10 ou 11 dígitos, apenas números.",
            )
            return False

        image_path = self.imagem_input.text().strip()

        if image_path and not Path(image_path).exists():
            QMessageBox.warning(
                self,
                "Imagem não encontrada",
                "O caminho da imagem/logo informado não existe.",
            )
            return False

        return True

    def copy_company_logo_to_assets(self, image_path_text: str, razao_social: str) -> str:
        if not image_path_text:
            return ""

        source_path = Path(image_path_text)

        if not source_path.exists():
            return ""

        LOGOS_DIR.mkdir(parents=True, exist_ok=True)

        company_short_name = get_company_short_name(razao_social)
        company_short_name = sanitize_filename(company_short_name)

        extension = source_path.suffix.lower()

        if not extension:
            extension = ".png"

        destination_filename = f"{company_short_name} logo{extension}"
        destination_path = LOGOS_DIR / destination_filename

        if source_path.resolve() != destination_path.resolve():
            shutil.copy2(source_path, destination_path)

        relative_path = destination_path.relative_to(BASE_DIR)

        return str(relative_path).replace("\\", "/")

    def save_company(self):
        if not self.validate_form():
            return

        razao_social = self.razao_social_input.text().strip()
        image_path = self.copy_company_logo_to_assets(
            image_path_text=self.imagem_input.text().strip(),
            razao_social=razao_social,
        )

        company = {
            "cnpj": clean_cnpj(self.cnpj_input.text()),
            "razao_social": clean_single_line_text(razao_social),
            "endereco": clean_single_line_text(self.endereco_input.text()),
            "endereco_completo": clean_single_line_text(self.endereco_completo_input.text()),
            "telefone": clean_phone(self.telefone_input.text()),
            "responsavel": clean_single_line_text(self.responsavel_input.text()),
            "caminho_template": "",
            "caminho_imagem": image_path,
            "ativa": 1,
        }

        create_company(company)
        self.company_saved.emit()

        QMessageBox.information(
            self,
            "Sucesso",
            "Fornecedor cadastrado/atualizado com sucesso.",
        )

        self.notice_label.setText("")
        self.clear_form()
        self.load_companies()

    def clear_form(self):
        self.cnpj_input.clear()
        self.razao_social_input.clear()
        self.endereco_input.clear()
        self.endereco_completo_input.clear()
        self.telefone_input.clear()
        self.responsavel_input.clear()
        self.imagem_input.clear()

    def load_companies(self):
        self.showing_inactive = False
        self.companies_list.clear()

        companies = list_active_companies()

        for company in companies:
            self.add_company_to_list(company, inactive=False)

    def load_inactive_companies(self):
        self.showing_inactive = True
        self.companies_list.clear()

        companies = list_inactive_companies()

        for company in companies:
            self.add_company_to_list(company, inactive=True)

    def add_company_to_list(self, company: dict, inactive: bool):
        cnpj_formatado = format_cnpj(company["cnpj"])
        razao_social = company["razao_social"]

        status = " [INATIVO]" if inactive else ""

        self.companies_list.addItem(
            f"{razao_social} - {cnpj_formatado}{status}"
        )

        list_item = self.companies_list.item(
            self.companies_list.count() - 1
        )

        list_item.setData(1000, company["cnpj"])

    def load_selected_company(self):
        selected_item = self.companies_list.currentItem()

        if not selected_item:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um fornecedor para carregar.",
            )
            return

        cnpj = selected_item.data(1000)
        company = get_company_by_cnpj(cnpj)

        if not company:
            QMessageBox.warning(
                self,
                "Erro",
                "Fornecedor não encontrado no banco.",
            )
            return

        self.cnpj_input.setText(company["cnpj"])
        self.razao_social_input.setText(company["razao_social"])
        self.endereco_input.setText(company["endereco"])
        self.endereco_completo_input.setText(company.get("endereco_completo") or "")
        self.telefone_input.setText(company.get("telefone") or "")
        self.responsavel_input.setText(company.get("responsavel") or "")
        self.imagem_input.setText(company.get("caminho_imagem") or "")

        self.notice_label.setText("Fornecedor carregado para edição.")

    def deactivate_selected_company(self):
        selected_item = self.companies_list.currentItem()

        if not selected_item:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um fornecedor para desativar.",
            )
            return

        cnpj = selected_item.data(1000)

        confirm = QMessageBox.question(
            self,
            "Confirmar desativação",
            "Deseja desativar este fornecedor? Ele não será usado em novas propostas.",
        )

        if confirm != QMessageBox.Yes:
            return

        deactivate_company(cnpj)

        QMessageBox.information(
            self,
            "Sucesso",
            "Fornecedor desativado com sucesso.",
        )

        self.clear_form()
        self.load_companies()

    def activate_selected_company(self):
        selected_item = self.companies_list.currentItem()

        if not selected_item:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um fornecedor para reativar.",
            )
            return

        cnpj = selected_item.data(1000)

        confirm = QMessageBox.question(
            self,
            "Confirmar reativação",
            "Deseja reativar este fornecedor? Ele voltará a ser usado nas propostas.",
        )

        if confirm != QMessageBox.Yes:
            return

        activate_company(cnpj)

        QMessageBox.information(
            self,
            "Sucesso",
            "Fornecedor reativado com sucesso.",
        )

        self.clear_form()
        self.load_companies()

    def prefill_company(self, company_data: dict):
        self.notice_label.setText(
            "Fornecedor detectado no PDF, mas ainda não cadastrado. Complete os dados e salve."
        )

        self.cnpj_input.setText(company_data.get("cnpj", ""))
        self.razao_social_input.setText(company_data.get("razao_social", ""))
        self.endereco_input.setText(company_data.get("endereco", ""))
        self.endereco_completo_input.setText(
            company_data.get("endereco_completo", company_data.get("endereco", ""))
        )
        self.telefone_input.setText(company_data.get("telefone", ""))
        self.responsavel_input.setText(company_data.get("responsavel", ""))
        self.imagem_input.setText(company_data.get("caminho_imagem", ""))