from app.models.validation import ValidationResult
from app.config.settings import get_settings


def build_decision_evidence(
    invoice,
    validation_result: ValidationResult,
    vendor_result: dict | None = None,
    po_result: dict | None = None,
    policy_context: str | None = None,
) -> dict:
    """
    Build a deterministic evidence report for invoice decision-making.

    This function does not ask the LLM to calculate or infer facts.
    It derives decision-relevant facts directly from application data.
    """
    invoice_total = invoice.total
    validation_passed = validation_result.is_valid

    vendor_verified = None
    vendor_status = None

    if vendor_result is not None:
        vendor_verified = vendor_result.get("found")
        vendor_status = vendor_result.get("status")

    purchase_order_verified = None
    purchase_order_status = None

    if po_result is not None:
        purchase_order_verified = po_result.get("found")
        purchase_order_status = po_result.get("status")

    reasons = []

    if not validation_passed:
        reasons.append(
            "The invoice failed one or more deterministic validation checks."
        )

    if vendor_result is not None:
        if not vendor_result.get("found", False):
            reasons.append(
                "The vendor could not be verified in the vendor database."
            )
        elif vendor_result.get("status") != "active":
            reasons.append(
                "The vendor is not active in the vendor database."
            )

    if po_result is not None:
        if not po_result.get("found", False):
            reasons.append(
                "The purchase order could not be found."
            )
        elif po_result.get("status") != "approved":
            reasons.append(
                "The purchase order is not approved."
            )

    requires_human_review = not validation_passed

    return {
        "validation_passed": validation_passed,
        "validation_issues": [
            issue.model_dump()
            for issue in validation_result.issues
        ],
        "vendor_verified": vendor_verified,
        "vendor_status": vendor_status,
        "purchase_order_verified": purchase_order_verified,
        "purchase_order_status": purchase_order_status,
        "invoice_total": invoice_total,
        "requires_human_review": requires_human_review,
        "reasons": reasons,
        "policy_context": policy_context,
    }