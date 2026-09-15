import pytest

from app.models.invoice import Invoice, InvoiceItem, Party
from app.models.validation import ValidationResult


@pytest.fixture
def invoice_factory():
    def create_invoice(**overrides):
        data = {
            "seller": Party(
                name="ABC Technologies Pvt Ltd",
                address="123 MG Road, Bengaluru, Karnataka",
            ),
            "buyer": Party(
                name="XYZ Solutions Pvt Ltd",
                address="Bengaluru, Karnataka",
            ),
            "invoice_number": "INV-10482",
            "purchase_order_number": "PO-5001",
            "invoice_date": "2026-09-09",
            "due_date": "2026-10-09",
            "items": [
                InvoiceItem(
                    description="Software License",
                    quantity=10,
                    unit_price=10000,
                    total_price=100000,
                )
            ],
            "subtotal": 100000,
            "tax": 18000,
            "tax_rate": 18,
            "total": 118000,
            "payment_terms": "Net 30",
        }

        data.update(overrides)
        return Invoice(**data)

    return create_invoice


@pytest.fixture
def valid_invoice(invoice_factory):
    return invoice_factory()

@pytest.fixture
def invalid_total_invoice(invoice_factory):
    return invoice_factory(total=150000)


@pytest.fixture
def unknown_vendor_invoice(invoice_factory):
    return invoice_factory(
        seller=Party(
            name="Unknown Vendor Pvt Ltd",
            address="Unknown Address",
        )
    )


@pytest.fixture
def missing_po_invoice(invoice_factory):
    return invoice_factory(purchase_order_number=None)


@pytest.fixture
def valid_validation_result():
    return ValidationResult(
        is_valid=True,
        issues=[],
    )


@pytest.fixture
def invalid_validation_result():
    return ValidationResult(
        is_valid=False,
        issues=[
            {
                "field": "total",
                "message": "Invoice total does not match subtotal plus tax.",
                "severity": "error",
            }
        ],
    )