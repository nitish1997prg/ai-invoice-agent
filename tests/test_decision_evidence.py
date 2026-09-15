from app.services.decision_evidence import build_decision_evidence



def test_invalid_invoice_requires_human_review(
    valid_invoice,
    invalid_validation_result,
):
    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=invalid_validation_result,
    )

    assert evidence["validation_passed"] is False
    assert evidence["requires_human_review"] is True
    assert len(evidence["validation_issues"]) == 1
    assert any(
        "validation" in reason.lower()
        for reason in evidence["reasons"]
    )


def test_unknown_vendor_is_recorded_in_evidence(
    valid_invoice,
    valid_validation_result,
):
    vendor_result = {
        "found": False,
        "vendor_name": "Unknown Vendor Pvt Ltd",
    }

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        vendor_result=vendor_result,
    )

    assert evidence["vendor_verified"] is False
    assert evidence["vendor_status"] is None
    assert any(
        "vendor" in reason.lower()
        for reason in evidence["reasons"]
    )


def test_inactive_vendor_is_recorded_in_evidence(
    valid_invoice,
    valid_validation_result,
):
    vendor_result = {
        "found": True,
        "vendor_name": "ABC Technologies Pvt Ltd",
        "vendor_id": "V-1001",
        "status": "inactive",
    }

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        vendor_result=vendor_result,
    )

    assert evidence["vendor_verified"] is True
    assert evidence["vendor_status"] == "inactive"
    assert any(
        "active" in reason.lower()
        for reason in evidence["reasons"]
    )


def test_unknown_purchase_order_is_recorded_in_evidence(
    valid_invoice,
    valid_validation_result,
):
    po_result = {
        "found": False,
        "po_number": "PO-9999",
    }

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        po_result=po_result,
    )

    assert evidence["purchase_order_verified"] is False
    assert evidence["purchase_order_status"] is None
    assert any(
        "purchase order" in reason.lower()
        for reason in evidence["reasons"]
    )


def test_unapproved_purchase_order_is_recorded_in_evidence(
    valid_invoice,
    valid_validation_result,
):
    po_result = {
        "found": True,
        "po_number": "PO-5001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "status": "pending",
        "total_amount": 100000,
    }

    evidence = build_decision_evidence(
        invoice=valid_invoice,
        validation_result=valid_validation_result,
        po_result=po_result,
    )

    assert evidence["purchase_order_verified"] is True
    assert evidence["purchase_order_status"] == "pending"
    assert any(
        "approved" in reason.lower()
        for reason in evidence["reasons"]
    )