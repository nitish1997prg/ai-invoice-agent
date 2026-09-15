from langchain_core.tools import tool


PURCHASE_ORDERS = {
    "PO-5001": {
        "vendor_name": "ABC Technologies Pvt Ltd",
        "status": "approved",
        "items": [
            {
                "description": "Software License",
                "quantity": 10,
                "unit_price": 10000,
                "total_price": 100000,
            }
        ],
        "total_amount": 100000,
    }
}


@tool
def lookup_purchase_order(po_number: str) -> dict:
    """Look up a purchase order by its purchase order number."""

    purchase_order = PURCHASE_ORDERS.get(po_number)

    if not purchase_order:
        return {
            "found": False,
            "po_number": po_number,
        }

    return {
        "found": True,
        "po_number": po_number,
        **purchase_order,
    }