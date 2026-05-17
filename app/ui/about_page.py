from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()

        self.title_label = QLabel("Sobre o ProposalFlow")
        self.title_label.setObjectName("PageTitle")

        self.subtitle_label = QLabel(
            "Aplicativo desktop para automação de propostas comerciais e documentos administrativos."
        )
        self.subtitle_label.setObjectName("PageSubtitle")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.create_info_card())
        main_layout.addWidget(self.create_features_card())
        main_layout.addWidget(self.create_usage_card())
        main_layout.addStretch()

        self.setLayout(main_layout)

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

    def create_info_card(self) -> QFrame:
        card, layout = self.create_card("Informações do aplicativo")

        text = QLabel(
            "ProposalFlow\n"
            "Versão: 1.0.0\n\n"
            "Aplicativo desktop desenvolvido em Python e PySide6 para automatizar "
            "a geração de propostas comerciais e documentos administrativos a partir "
            "de PDFs, OCR, preenchimento manual, cadastros locais e templates Word."
        )
        text.setObjectName("MutedText")
        text.setWordWrap(True)

        layout.addWidget(text)

        return card

    def create_features_card(self) -> QFrame:
        card, layout = self.create_card("Principais recursos")

        text = QLabel(
            "• Extração de dados a partir de PDFs\n"
            "• Apoio com OCR local usando Tesseract\n"
            "• Geração manual de propostas\n"
            "• Cadastro de fornecedores\n"
            "• Regras de combinação entre fornecedores\n"
            "• Banco de dados local com SQLite\n"
            "• Geração de documentos Word com templates editáveis\n"
            "• Empacotamento desktop com PyInstaller"
        )
        text.setObjectName("MutedText")
        text.setWordWrap(True)

        layout.addWidget(text)

        return card

    def create_usage_card(self) -> QFrame:
        card, layout = self.create_card("Observações de uso")

        text = QLabel(
            "Para funcionamento correto, mantenha a pasta do aplicativo completa. "
            "O executável depende das pastas internas de templates, banco de dados, "
            "assets e ferramentas auxiliares.\n\n"
            "Estrutura esperada na versão empacotada: ProposalFlow.exe, app, data e tools "
            "dentro da mesma pasta."
        )
        text.setObjectName("MutedText")
        text.setWordWrap(True)

        layout.addWidget(text)

        return card