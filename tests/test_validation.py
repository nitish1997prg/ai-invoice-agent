from app.models.invoice import InvoiceItem
from app.services.validation import validate_invoice


def test_valid_invoice_passes(valid_invoice):
    result = validate_invoice(valid_invoice)

    assert result.is_valid is True
    assert result.issues == []


def test_incorrect_line_item_total_fails(invoice_factory):
    invoice = invoice_factory(
        items=[
            InvoiceItem(
                description="Software License",
                quantity=10,
                unit_price=10000,
                total_price=90000,
            )
        ]
    )

    result = validate_invoice(invoice)

    assert result.is_valid is False


def test_incorrect_subtotal_fails(invoice_factory):
    invoice = invoice_factory(
        subtotal=90000,
    )

    result = validate_invoice(invoice)

    assert result.is_valid is False


def test_incorrect_tax_fails(invoice_factory):
    invoice = invoice_factory(
        tax=20000,
    )

    result = validate_invoice(invoice)

    assert result.is_valid is False


def test_incorrect_grand_total_fails(invoice_factory):
    invoice = invoice_factory(
        total=150000,
    )

    result = validate_invoice(invoice)

    assert result.is_valid is False