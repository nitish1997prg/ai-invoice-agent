from pathlib import Path

import pytest

from app.services.extraction import extract_invoice
from app.services.validation import validate_invoice


@pytest.mark.parametrize(
    "filename, expected_valid",
    [
        ("invoice_001.txt", True),
        ("invoice_002_invalid_total.txt", False),
        ("invoice_003_unknown_vendor.txt", True),
        ("invoice_004_missing_po.txt", True),
        ("invoice_005_low_value.txt", True),
    ],
)
def test_invoice_file_extraction_and_validation(
    filename,
    expected_valid,
):
    invoice_path = Path("invoices") / filename
    invoice_text = invoice_path.read_text(encoding="utf-8")

    invoice = extract_invoice(invoice_text)
    validation_result = validate_invoice(invoice)

    assert invoice.invoice_number
    assert invoice.seller.name
    assert len(invoice.items) > 0

    assert validation_result.is_valid is expected_valid