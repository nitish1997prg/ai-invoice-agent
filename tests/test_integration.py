from pathlib import Path

from app.services.business_checks import run_business_checks
from app.services.decision_evidence import build_decision_evidence
from app.services.extraction import extract_invoice
from app.services.validation import validate_invoice


def test_valid_invoice_pipeline():
    invoice_path = Path("invoices/invoice_001.txt")
    invoice_text = invoice_path.read_text(encoding="utf-8")

    invoice = extract_invoice(invoice_text)
    validation_result = validate_invoice(invoice)

    business_checks = run_business_checks(
        vendor_name=invoice.seller.name,
        po_number=invoice.purchase_order_number,
    )

    evidence = build_decision_evidence(
        invoice=invoice,
        validation_result=validation_result,
        vendor_result=business_checks["vendor_result"],
        po_result=business_checks["po_result"],
    )

    assert invoice.invoice_number == "INV-10482"
    assert validation_result.is_valid is True
    assert business_checks["vendor_result"]["found"] is True
    assert business_checks["po_result"]["found"] is True
    assert evidence["validation_passed"] is True


def test_business_checks_are_propagated_to_decision_evidence(
    valid_invoice,
    valid_validation_result,
):
    business_checks = run_business_checks(
        vendor_name=valid_invoice.seller.name,
        po_number=valid_invoice.purchase_order_number,
    )

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        vendor_result=business_checks["vendor_result"],
        po_result=business_checks["po_result"],
    )

    assert business_checks["vendor_result"]["found"] is True
    assert business_checks["po_result"]["found"] is True

    assert evidence["vendor_verified"] is True
    assert evidence["vendor_status"] == "active"
    assert evidence["purchase_order_verified"] is True
    assert evidence["purchase_order_status"] == "approved"


def test_unknown_vendor_is_propagated_to_decision_evidence(
    valid_invoice,
    valid_validation_result,
):
    business_checks = run_business_checks(
        vendor_name="Unknown Vendor Pvt Ltd",
        po_number=valid_invoice.purchase_order_number,
    )

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        vendor_result=business_checks["vendor_result"],
        po_result=business_checks["po_result"],
    )

    assert business_checks["vendor_result"]["found"] is False
    assert evidence["vendor_verified"] is False
    assert any(
        "vendor" in reason.lower()
        for reason in evidence["reasons"]
    )