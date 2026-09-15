def test_valid_invoice_fixture(valid_invoice):
    assert valid_invoice.invoice_number == "INV-10482"
    assert valid_invoice.total == 118000
    assert len(valid_invoice.items) == 1