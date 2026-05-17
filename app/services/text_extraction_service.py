from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from services.file_service import open_path
from services.pdf_reader import extract_text_from_pdf
from utils.resource_path import get_resource_path

BUNDLED_TESSERACT_PATH = get_resource_path("tools/tesseract/tesseract.exe")
SYSTEM_TESSERACT_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


def configure_tesseract():
    if BUNDLED_TESSERACT_PATH.exists():
        pytesseract.pytesseract.tesseract_cmd = str(BUNDLED_TESSERACT_PATH)
        return

    if SYSTEM_TESSERACT_PATH.exists():
        pytesseract.pytesseract.tesseract_cmd = str(SYSTEM_TESSERACT_PATH)
        return

    raise FileNotFoundError(
        "Tesseract não encontrado. Verifique se existe em "
        "'tools/tesseract/tesseract.exe' ou se está instalado em "
        "'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'."
    )


def extract_selectable_text_to_txt(
    pdf_path: str | Path,
    output_folder: str | Path,
) -> Path:
    pdf_path = Path(pdf_path)
    output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    output_txt_path = output_folder / f"{pdf_path.stem}_texto_extraido.txt"

    text = extract_text_from_pdf(str(pdf_path))

    with open(output_txt_path, "w", encoding="utf-8") as file:
        file.write(text)

    return output_txt_path


def extract_ocr_text_to_txt(
    pdf_path: str | Path,
    output_folder: str | Path,
    dpi: int = 200,
    language: str = "por",
) -> Path:
    configure_tesseract()

    tessdata_dir = BUNDLED_TESSERACT_PATH.parent / "tessdata"

    if not tessdata_dir.exists():
        raise FileNotFoundError(
            f"Pasta tessdata não encontrada: {tessdata_dir}"
        )

    for lang in language.split("+"):
        language_file = tessdata_dir / f"{lang}.traineddata"

        if not language_file.exists():
            raise FileNotFoundError(
                f"Arquivo de idioma não encontrado: {language_file}"
            )

    # Caminho em formato mais amigável para o Tesseract no Windows
    tessdata_dir_text = str(tessdata_dir).replace("\\", "/")

    # Não vamos usar TESSDATA_PREFIX aqui para evitar conflito.
    # O --tessdata-dir já aponta diretamente para a pasta correta.
    config = f"--tessdata-dir {tessdata_dir_text}"

    pdf_path = Path(pdf_path)
    output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    output_txt_path = output_folder / f"{pdf_path.stem}_ocr.txt"

    doc = fitz.open(str(pdf_path))

    all_text = []

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    for page_index, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix)
        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples,
        )

        text = pytesseract.image_to_string(
            image,
            lang=language,
            config=config,
        )

        all_text.append(f"--- Página {page_index} ---")
        all_text.append(text)
        all_text.append("")

    final_text = "\n".join(all_text)

    with open(output_txt_path, "w", encoding="utf-8") as file:
        file.write(final_text)

    return output_txt_path


def extract_text_to_txt(
    pdf_path: str | Path,
    output_folder: str | Path,
    use_ocr: bool = False,
) -> Path:
    if use_ocr:
        return extract_ocr_text_to_txt(
            pdf_path=pdf_path,
            output_folder=output_folder,
        )

    return extract_selectable_text_to_txt(
        pdf_path=pdf_path,
        output_folder=output_folder,
    )


def open_file(path: str | Path) -> None:
    open_path(path)