from app.tools.vendor import lookup_vendor
from app.tools.purchase_order import lookup_purchase_order


def run_business_checks(
    vendor_name: str,
    po_number: str | None = None,
) -> dict:
    """
    Run authoritative vendor and purchase-order checks.
    """

    vendor_result = lookup_vendor.invoke(
        {"vendor_name": vendor_name}
    )

    po_result = None

    if po_number:
        po_result = lookup_purchase_order.invoke(
            {"po_number": po_number}
        )

    return {
        "vendor_result": vendor_result,
        "po_result": po_result,
    }