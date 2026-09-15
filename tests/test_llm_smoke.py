from pathlib import Path

import pytest

from app.services.extraction import extract_invoice


@pytest.mark.llm
def test_llm_invoice_extraction_smoke():
    invoice_path = Path("invoices/invoice_001.txt")
    invoice_text = invoice_path.read_text(encoding="utf-8")

    invoice = extract_invoice(invoice_text)

    assert invoice is not None
    assert invoice.invoice_number
    assert invoice.seller.name
    assert invoice.buyer.name
    assert len(invoice.items) > 0
    assert invoice.subtotal >= 0
    assert invoice.tax >= 0
    assert invoice.total >= 0