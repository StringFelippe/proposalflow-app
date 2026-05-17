from services.document_type_detector import detect_document_type
from services.nf_parser import parse_nf_text
from services.nfs_parser import parse_nfs_text


def parse_text(text: str) -> dict:
    document_type = detect_document_type(text)

    if document_type == "NFS":
        return parse_nfs_text(text)

    if document_type == "NF":
        return parse_nf_text(text)

    raise ValueError("Tipo de documento não suportado.")