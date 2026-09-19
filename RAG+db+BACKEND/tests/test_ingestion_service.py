from pathlib import Path

from app.services.ingestion_service import ingest_document


PDF_PATH = Path("data/documents/Refund_policy_v2.pdf")


def test_ingest_document():
    assert PDF_PATH.exists(), f"Test PDF not found: {PDF_PATH}"

    result = ingest_document(
        file_path=str(PDF_PATH),
        document_id=1,
        document_name="Refund Policy",
        document_type="policy",
        version=2,
        uploaded_by="admin",
    )

    assert result is not None