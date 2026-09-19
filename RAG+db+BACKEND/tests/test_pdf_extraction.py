from pathlib import Path

from app.services.pdf_service import extract_text_from_pdf


PDF_PATH = Path("data/documents/Refund_policy_v2.pdf")


def test_extract_text_from_pdf():
    assert PDF_PATH.exists(), f"Test PDF not found: {PDF_PATH}"

    pages = extract_text_from_pdf(str(PDF_PATH))

    assert pages is not None
    assert len(pages) > 0

    for page in pages:
        assert "page_number" in page
        assert "text" in page
        assert page["page_number"] >= 1
        assert isinstance(page["text"], str)
        assert page["text"].strip()