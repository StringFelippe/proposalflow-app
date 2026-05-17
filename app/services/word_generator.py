from pathlib import Path

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

from services.config_service import get_app_config
from utils.resource_path import get_base_dir


BASE_DIR = get_base_dir()


def resolve_project_path(path_text: str) -> Path | None:
    if not path_text:
        return None

    path = Path(path_text.strip())

    if path.is_absolute():
        return path

    return BASE_DIR / path


def generate_word_from_template(
    template_path: str,
    output_path: str,
    context: dict,
) -> None:
    doc = DocxTemplate(template_path)

    context = context.copy()

    image_path_text = context.get("empresa_proponente", {}).get("caminho_imagem", "")
    image_path = resolve_project_path(image_path_text)

    if image_path and image_path.exists():
        context["imagem_empresa"] = InlineImage(
            doc,
            str(image_path),
            width=Mm(get_app_config()["header_image_width_mm"]),
        )
    else:
        context["imagem_empresa"] = ""

    doc.render(context)
    doc.save(output_path)