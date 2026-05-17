import sys

from PySide6.QtWidgets import QApplication

from repositories.database import initialize_database
from services.config_service import initialize_default_config
from ui.main_window import MainWindow


def main():
    initialize_database()
    initialize_default_config()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()