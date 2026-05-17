import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    document = pymupdf.open(pdf_path)
    pages_text = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text", sort=True)
        pages_text.append(f"\n--- Página {page_number} ---\n{text}")

    document.close()

    return "\n".join(pages_text)