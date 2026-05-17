from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from repositories.company_repository import list_active_companies, list_incompatibilities
from repositories.settings_repository import get_setting, set_setting
from services.config_service import get_int_config_value, increment_config_counter
from services.document_generation_service import generate_documents_from_multiple_pdfs
from services.file_service import open_path
from ui.about_page import AboutPage
from ui.company_register_page import CompanyRegisterPage
from ui.incompatibility_page import IncompatibilityPage
from ui.manual_generation_page import ManualGenerationPage
from ui.settings_page import SettingsPage
from ui.text_extraction_page import TextExtractionPage
from utils.resource_path import get_resource_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.selected_pdf_paths = []
        self.output_folder = None
        self.pending_generation_after_company_registration = False
        self.last_generated_output_folder = None

        last_output_folder = get_setting("last_output_folder")

        if last_output_folder:
            self.output_folder = Path(last_output_folder)

        self.setWindowTitle("ProposalFlow")
        self.setWindowIcon(
            QIcon(str(get_resource_path("app/assets/icons/kit.ico")))
        )
        self.resize(1280, 780)

        self.stack = QStackedWidget()

        self.dashboard_page = self.create_dashboard_page()
        self.pdf_generation_page = self.create_pdf_generation_page()
        self.manual_generation_page = ManualGenerationPage()
        self.text_extraction_page = TextExtractionPage()
        self.company_register_page = CompanyRegisterPage()
        self.incompatibility_page = IncompatibilityPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()

        self.company_register_page.company_saved.connect(
            self.retry_generation_after_company_registration
        )
        self.company_register_page.company_saved.connect(
            self.refresh_after_company_saved
        )

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.pdf_generation_page)
        self.stack.addWidget(self.manual_generation_page)
        self.stack.addWidget(self.text_extraction_page)
        self.stack.addWidget(self.company_register_page)
        self.stack.addWidget(self.incompatibility_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)

        sidebar = self.create_sidebar()

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, stretch=1)

        container = QWidget()
        container.setLayout(root_layout)

        self.setCentralWidget(container)
        self.apply_dark_theme()

    # =========================
    # Layout base
    # =========================

    def create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        title = QLabel("ProposalFlow")
        title.setObjectName("AppTitle")

        subtitle = QLabel("Automação de Propostas e Documentos")
        subtitle.setObjectName("AppSubtitle")

        self.dashboard_button = self.create_nav_button("Dashboard", 0)
        self.pdf_button = self.create_nav_button("Gerar por PDF", 1)
        self.manual_button = self.create_nav_button("Gerar Manualmente", 2)
        self.ocr_button = self.create_nav_button("Extração OCR", 3)
        self.companies_button = self.create_nav_button("Fornecedores", 4)
        self.incompatibilities_button = self.create_nav_button("Regras de Combinação", 5)
        self.settings_button = self.create_nav_button("Configurações", 6)
        self.about_button = self.create_nav_button("Sobre", 7)

        footer = QLabel("● Sistema pronto")
        footer.setObjectName("SidebarFooter")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 24, 18, 18)
        layout.setSpacing(10)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(24)
        layout.addWidget(self.dashboard_button)
        layout.addWidget(self.pdf_button)
        layout.addWidget(self.manual_button)
        layout.addWidget(self.ocr_button)
        layout.addWidget(self.companies_button)
        layout.addWidget(self.incompatibilities_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.about_button)
        layout.addStretch()
        layout.addWidget(footer)

        sidebar.setLayout(layout)

        return sidebar

    def create_nav_button(self, text: str, index: int) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("NavButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.navigate_to(index))
        return button

    def navigate_to(self, index: int):
        if index == 0:
            self.refresh_dashboard()

        if index == 2:
            self.manual_generation_page.load_companies()

        if index == 4:
            self.company_register_page.load_companies()

        if index == 5:
            self.incompatibility_page.refresh_page()

        if index == 6:
            self.settings_page.load_settings()

        self.stack.setCurrentIndex(index)

    # =========================
    # Dashboard
    # =========================

    def create_dashboard_page(self) -> QWidget:
        page = QWidget()

        self.dashboard_title = QLabel("Dashboard")
        self.dashboard_title.setObjectName("PageTitle")

        self.dashboard_subtitle = QLabel("Visão geral do ProposalFlow")
        self.dashboard_subtitle.setObjectName("PageSubtitle")

        self.companies_card_value = QLabel("0")
        self.service_card_value = QLabel("-")
        self.product_card_value = QLabel("-")
        self.rules_card_value = QLabel("0")

        cards_layout = QGridLayout()
        cards_layout.setSpacing(18)

        cards_layout.addWidget(
            self.create_stat_card("Fornecedores ativos", self.companies_card_value),
            0,
            0,
        )
        cards_layout.addWidget(
            self.create_stat_card("Propostas de serviço", self.service_card_value),
            0,
            1,
        )
        cards_layout.addWidget(
            self.create_stat_card("Propostas de produto", self.product_card_value),
            0,
            2,
        )
        cards_layout.addWidget(
            self.create_stat_card("Regras de combinação", self.rules_card_value),
            0,
            3,
        )

        quick_actions = self.create_quick_actions_card()
        system_info = self.create_system_info_card()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(28, 26, 28, 26)
        content_layout.setSpacing(20)
        content_layout.addWidget(self.dashboard_title)
        content_layout.addWidget(self.dashboard_subtitle)
        content_layout.addSpacing(10)
        content_layout.addLayout(cards_layout)
        content_layout.addWidget(quick_actions)
        content_layout.addWidget(system_info)
        content_layout.addStretch()

        page.setLayout(content_layout)

        self.refresh_dashboard()

        return page

    def create_stat_card(self, label_text: str, value_label: QLabel) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(130)

        value_label.setObjectName("CardValue")

        label = QLabel(label_text)
        label.setObjectName("CardLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.addWidget(value_label)
        layout.addWidget(label)
        layout.addStretch()

        card.setLayout(layout)

        return card

    def create_quick_actions_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        title = QLabel("Ações rápidas")
        title.setObjectName("SectionTitle")

        subtitle = QLabel("Escolha uma opção para começar")
        subtitle.setObjectName("MutedText")

        generate_pdf_button = QPushButton("Gerar por PDF")
        generate_pdf_button.clicked.connect(lambda: self.navigate_to(1))

        manual_button = QPushButton("Gerar manualmente")
        manual_button.clicked.connect(lambda: self.navigate_to(2))

        ocr_button = QPushButton("Extrair com OCR")
        ocr_button.clicked.connect(lambda: self.navigate_to(3))

        supplier_button = QPushButton("Gerenciar fornecedores")
        supplier_button.clicked.connect(lambda: self.navigate_to(4))

        for button in [generate_pdf_button, manual_button, ocr_button, supplier_button]:
            button.setObjectName("ActionButton")
            button.setCursor(Qt.PointingHandCursor)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(generate_pdf_button, 0, 0)
        grid.addWidget(manual_button, 0, 1)
        grid.addWidget(ocr_button, 1, 0)
        grid.addWidget(supplier_button, 1, 1)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        layout.addLayout(grid)

        card.setLayout(layout)

        return card

    def create_system_info_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        title = QLabel("Informações do sistema")
        title.setObjectName("SectionTitle")

        info = QLabel(
            "Banco local: SQLite  •  Templates Word: carregados  •  OCR: pronto para uso"
        )
        info.setObjectName("MutedText")

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.addWidget(title)
        layout.addWidget(info)

        card.setLayout(layout)

        return card

    def refresh_dashboard(self):
        try:
            companies_count = len(list_active_companies())
            rules_count = len(list_incompatibilities())

            service_generated_count = get_int_config_value(
                "dashboard_nfs_generated_count",
                0,
            )

            product_generated_count = get_int_config_value(
                "dashboard_nf_generated_count",
                0,
            )

            self.companies_card_value.setText(str(companies_count))
            self.service_card_value.setText(str(service_generated_count))
            self.product_card_value.setText(str(product_generated_count))
            self.rules_card_value.setText(str(rules_count))

        except Exception:
            self.companies_card_value.setText("-")
            self.service_card_value.setText("-")
            self.product_card_value.setText("-")
            self.rules_card_value.setText("-")

    # =========================
    # Página de geração por PDF
    # =========================

    def create_pdf_generation_page(self) -> QWidget:
        page = QWidget()

        title = QLabel("Gerar proposta por PDF")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Selecione PDFs de exemplo para extrair dados e gerar propostas comerciais automaticamente."
        )
        subtitle.setObjectName("PageSubtitle")

        self.budget_template_combo = QComboBox()
        self.budget_template_combo.addItem("Completo", "completo")
        self.budget_template_combo.addItem("Simples", "simples")

        self.select_pdfs_button = QPushButton("Selecionar PDFs")
        self.select_pdfs_button.clicked.connect(self.select_pdfs)

        self.pdf_list = QListWidget()

        self.select_output_button = QPushButton("Selecionar pasta de saída")
        self.select_output_button.clicked.connect(self.select_output_folder)

        if self.output_folder:
            self.output_label = QLabel(f"Pasta de saída: {self.output_folder}")
        else:
            self.output_label = QLabel("Pasta de saída: nenhuma selecionada")

        self.output_label.setObjectName("MutedText")

        self.generate_button = QPushButton("Gerar propostas")
        self.generate_button.clicked.connect(self.generate_documents)

        self.open_output_button = QPushButton("Abrir última pasta gerada")
        self.open_output_button.clicked.connect(self.open_last_generated_output_folder)
        self.open_output_button.setEnabled(False)

        self.pdf_logs = QTextEdit()
        self.pdf_logs.setReadOnly(True)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_pdfs_button)
        buttons_layout.addWidget(self.select_output_button)
        buttons_layout.addWidget(QLabel("Template:"))
        buttons_layout.addWidget(self.budget_template_combo)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.open_output_button)

        files_card = QFrame()
        files_card.setObjectName("Card")

        files_layout = QVBoxLayout()
        files_layout.setContentsMargins(18, 18, 18, 18)
        files_layout.addWidget(QLabel("Arquivos selecionados"))
        files_layout.addWidget(self.pdf_list)
        files_card.setLayout(files_layout)

        logs_card = QFrame()
        logs_card.setObjectName("Card")

        logs_layout = QVBoxLayout()
        logs_layout.setContentsMargins(18, 18, 18, 18)
        logs_layout.addWidget(QLabel("Logs do processo"))
        logs_layout.addWidget(self.pdf_logs)
        logs_card.setLayout(logs_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.output_label)
        layout.addWidget(files_card, stretch=2)
        layout.addWidget(logs_card, stretch=3)

        page.setLayout(layout)

        return page

    def log(self, message: str):
        self.pdf_logs.append(message)

    def select_pdfs(self):
        last_pdf_folder = get_setting("last_pdf_folder")
        start_folder = last_pdf_folder if last_pdf_folder else ""

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar arquivos PDF",
            start_folder,
            "Arquivos PDF (*.pdf)",
        )

        if not files:
            return

        self.selected_pdf_paths = [Path(file) for file in files]

        first_pdf_folder = str(self.selected_pdf_paths[0].parent)
        set_setting("last_pdf_folder", first_pdf_folder)

        self.pdf_list.clear()

        for file in self.selected_pdf_paths:
            self.pdf_list.addItem(str(file))

        self.log(f"{len(self.selected_pdf_paths)} PDF(s) selecionado(s).")

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

        self.log(f"Pasta de saída selecionada: {self.output_folder}")

    def generate_documents(self):
        if not self.selected_pdf_paths:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione pelo menos um PDF.",
            )
            return

        if not self.output_folder:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione uma pasta de saída.",
            )
            return

        self.generate_button.setEnabled(False)
        self.generate_button.setText("Gerando...")

        self.log("=" * 60)
        self.log("Iniciando geração das propostas...")

        try:
            result = generate_documents_from_multiple_pdfs(
                pdf_paths=self.selected_pdf_paths,
                output_base_folder=self.output_folder,
                budget_template_type=self.budget_template_combo.currentData(),
            )

            self.log(f"Total de PDFs: {result['total']}")
            self.log(f"Sucessos: {result['success_count']}")
            self.log(f"Erros: {result['error_count']}")

            for item in result["results"]:
                self.log("-" * 60)

                pdf_name = Path(item["pdf_path"]).name
                self.log(f"Arquivo: {pdf_name}")

                if item.get("document_type"):
                    tipo = "Serviço" if item["document_type"] == "NFS" else "Produto"
                    self.log(f"Tipo detectado: {tipo}")

                if item["status"] == "success":
                    generated_count = len(item["generated_files"])

                    self.log("Status: sucesso")
                    self.log(f"Arquivos gerados: {generated_count}")

                    if item.get("document_type") == "NFS":
                        increment_config_counter("dashboard_nfs_generated_count")

                    if item.get("document_type") == "NF":
                        increment_config_counter("dashboard_nf_generated_count")

                    self.last_generated_output_folder = item["output_folder"]
                    self.open_output_button.setEnabled(True)

                else:
                    self.log("Status: erro")
                    self.log(f"Motivo: {item['message']}")

                if item.get("error_type") == "company_not_registered":
                    self.handle_company_not_registered(item)

            self.log("Processamento finalizado.")

            QMessageBox.information(
                self,
                "Concluído",
                "Processamento finalizado.",
            )

            self.refresh_dashboard()

        except Exception as error:
            self.log(f"Erro inesperado: {error}")

            QMessageBox.critical(
                self,
                "Erro",
                f"Ocorreu um erro inesperado:\n{error}",
            )

        finally:
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Gerar propostas")

    # =========================
    # Fornecedor não cadastrado
    # =========================

    def handle_company_not_registered(self, item: dict):
        company_data = item.get("company_data", {})

        resposta = QMessageBox.question(
            self,
            "Fornecedor não encontrado",
            (
                "O fornecedor identificado neste PDF ainda não está cadastrado.\n\n"
                f"CNPJ/Identificador: {company_data.get('cnpj', '')}\n"
                f"Razão Social: {company_data.get('razao_social', '')}\n\n"
                "Deseja cadastrar esse fornecedor agora?"
            ),
        )

        if resposta != QMessageBox.Yes:
            return

        self.pending_generation_after_company_registration = True

        if hasattr(self.company_register_page, "prefill_company"):
            self.company_register_page.prefill_company(company_data)

        self.navigate_to(4)

    def retry_generation_after_company_registration(self):
        if not self.pending_generation_after_company_registration:
            return

        self.pending_generation_after_company_registration = False

        QMessageBox.information(
            self,
            "Fornecedor cadastrado",
            "Fornecedor cadastrado com sucesso. O app tentará gerar as propostas novamente.",
        )

        self.navigate_to(1)
        self.generate_documents()

    # =========================
    # Pastas
    # =========================

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

    # =========================
    # Tema
    # =========================

    def apply_dark_theme(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0b1118;
            }

            QWidget {
                background-color: #0b1118;
                color: #e5e7eb;
                font-family: Segoe UI;
                font-size: 14px;
            }

            #Sidebar {
                background-color: #101824;
                border-right: 1px solid #1f2937;
            }

            #AppTitle {
                font-size: 24px;
                font-weight: 800;
                color: #60a5fa;
                letter-spacing: 1px;
            }

            #AppSubtitle {
                font-size: 13px;
                color: #9ca3af;
            }

            #SidebarFooter {
                color: #22c55e;
                font-size: 13px;
            }

            #NavButton {
                text-align: left;
                padding: 14px 16px;
                border-radius: 12px;
                background-color: transparent;
                color: #d1d5db;
                border: 1px solid transparent;
            }

            #NavButton:hover {
                background-color: #172033;
                border: 1px solid #2563eb;
                color: #ffffff;
            }

            #PageTitle {
                font-size: 28px;
                font-weight: 700;
                color: #f9fafb;
            }

            #PageSubtitle {
                font-size: 14px;
                color: #9ca3af;
            }

            #SectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #f9fafb;
            }

            #MutedText {
                color: #9ca3af;
            }

            #Card {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 18px;
            }

            #CardValue {
                font-size: 36px;
                font-weight: 800;
                color: #f9fafb;
            }

            #CardLabel {
                font-size: 14px;
                color: #9ca3af;
            }

            QPushButton {
                background-color: #1d4ed8;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #2563eb;
            }

            QPushButton:disabled {
                background-color: #374151;
                color: #9ca3af;
            }

            #ActionButton {
                background-color: #172033;
                border: 1px solid #1f2937;
                padding: 18px;
                text-align: left;
            }

            #ActionButton:hover {
                border: 1px solid #3b82f6;
                background-color: #1e293b;
            }

            QListWidget,
            QTextEdit,
            QLineEdit,
            QComboBox,
            QTableWidget {
                background-color: #0f172a;
                border: 1px solid #263244;
                border-radius: 10px;
                color: #e5e7eb;
                padding: 8px;
            }

            QLabel {
                background: transparent;
            }
            """
        )

    def refresh_after_company_saved(self):
        self.manual_generation_page.load_companies()
        self.company_register_page.load_companies()
        self.refresh_dashboard()