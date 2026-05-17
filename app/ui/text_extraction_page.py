from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from repositories.settings_repository import get_setting, set_setting
from services.text_extraction_service import extract_text_to_txt, open_file


class TextExtractionPage(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_pdf_path = None
        self.output_folder = None
        self.last_generated_txt_path = None

        last_output_folder = get_setting("last_output_folder")
        if last_output_folder:
            self.output_folder = Path(last_output_folder)

        self.title_label = QLabel("Extração OCR")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Extraia texto de PDFs para apoiar análise, conferência de dados ou preenchimento manual."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        self.select_pdf_button = QPushButton("Selecionar PDF")
        self.select_pdf_button.clicked.connect(self.select_pdf)

        self.pdf_label = QLabel("PDF selecionado: nenhum")
        self.pdf_label.setObjectName("MutedText")
        self.pdf_label.setWordWrap(True)

        self.select_output_button = QPushButton("Selecionar pasta de saída")
        self.select_output_button.clicked.connect(self.select_output_folder)

        if self.output_folder:
            self.output_label = QLabel(f"Pasta de saída: {self.output_folder}")
        else:
            self.output_label = QLabel("Pasta de saída: nenhuma selecionada")

        self.output_label.setObjectName("MutedText")
        self.output_label.setWordWrap(True)

        self.use_ocr_checkbox = QCheckBox("Usar OCR com Tesseract")
        self.use_ocr_checkbox.setChecked(True)

        self.extract_button = QPushButton("Extrair texto")
        self.extract_button.clicked.connect(self.extract_text)

        self.open_txt_button = QPushButton("Abrir último texto extraído")
        self.open_txt_button.clicked.connect(self.open_last_txt)
        self.open_txt_button.setEnabled(False)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMinimumHeight(180)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.create_document_card())
        main_layout.addWidget(self.create_settings_card())
        main_layout.addWidget(self.create_status_card(), stretch=1)

        self.setLayout(main_layout)

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

    def create_document_card(self) -> QFrame:
        card, layout = self.create_card("Documento")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_pdf_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)
        layout.addWidget(self.pdf_label)

        helper = QLabel(
            "Selecione um PDF com texto selecionável ou um documento escaneado. "
            "Para PDFs de imagem, mantenha o OCR ativado."
        )
        helper.setObjectName("MutedText")
        helper.setWordWrap(True)

        layout.addWidget(helper)

        return card

    def create_settings_card(self) -> QFrame:
        card, layout = self.create_card("Configuração da extração")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_output_button)
        buttons_layout.addWidget(self.extract_button)
        buttons_layout.addWidget(self.open_txt_button)
        buttons_layout.addStretch()

        layout.addWidget(self.use_ocr_checkbox)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.output_label)

        helper = QLabel(
            "OCR com Tesseract pode demorar alguns segundos por página. "
            "A extração gera um arquivo .txt de apoio, separado do fluxo de geração de propostas."
        )
        helper.setObjectName("MutedText")
        helper.setWordWrap(True)

        layout.addWidget(helper)

        return card

    def create_status_card(self) -> QFrame:
        card, layout = self.create_card("Status")

        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.logs)

        return card

    # =========================
    # Lógica
    # =========================

    def log(self, message: str):
        self.logs.append(message)

    def select_pdf(self):
        last_pdf_folder = get_setting("last_pdf_folder")
        start_folder = last_pdf_folder if last_pdf_folder else ""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar PDF",
            start_folder,
            "Arquivos PDF (*.pdf)",
        )

        if not file_path:
            return

        self.selected_pdf_path = Path(file_path)
        self.pdf_label.setText(f"PDF selecionado: {self.selected_pdf_path}")

        set_setting("last_pdf_folder", str(self.selected_pdf_path.parent))

        self.log("PDF selecionado.")

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

    def extract_text(self):
        if not self.selected_pdf_path:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um PDF.",
            )
            return

        if not self.output_folder:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione uma pasta de saída.",
            )
            return

        self.extract_button.setEnabled(False)
        self.extract_button.setText("Extraindo...")

        try:
            self.log("=" * 60)
            self.log("Iniciando extração de texto...")

            use_ocr = self.use_ocr_checkbox.isChecked()

            if use_ocr:
                self.log("Modo: OCR com Tesseract.")
            else:
                self.log("Modo: texto selecionável do PDF.")

            txt_path = extract_text_to_txt(
                pdf_path=self.selected_pdf_path,
                output_folder=self.output_folder,
                use_ocr=use_ocr,
            )

            self.last_generated_txt_path = txt_path
            self.open_txt_button.setEnabled(True)

            self.log("Texto extraído com sucesso.")
            self.log(f"Arquivo gerado: {txt_path.name}")
            self.log("Abrindo arquivo gerado...")

            open_file(txt_path)

            QMessageBox.information(
                self,
                "Concluído",
                "Texto extraído com sucesso.",
            )

        except Exception as error:
            self.log(f"Erro: {error}")
            QMessageBox.critical(
                self,
                "Erro",
                f"Ocorreu um erro:\n{error}",
            )

        finally:
            self.extract_button.setEnabled(True)
            self.extract_button.setText("Extrair texto")

    def open_last_txt(self):
        if not self.last_generated_txt_path:
            QMessageBox.warning(
                self,
                "Atenção",
                "Nenhum texto extraído ainda.",
            )
            return

        try:
            open_file(self.last_generated_txt_path)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível abrir o arquivo:\n{error}",
            )