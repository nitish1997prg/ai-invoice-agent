from langchain_core.tools import tool


VENDORS = {
    "ABC Technologies Pvt Ltd": {
        "vendor_id": "V-1001",
        "status": "active",
        "payment_terms": "Net 30",
    },
    "Acme Software Pvt Ltd": {
        "vendor_id": "V-1002",
        "status": "active",
        "payment_terms": "Net 15",
    },
}


@tool
def lookup_vendor(vendor_name: str) -> dict:
    """Look up a vendor and return their registered information."""

    vendor = VENDORS.get(vendor_name)

    if not vendor:
        return {
            "found": False,
            "vendor_name": vendor_name,
        }

    return {
        "found": True,
        "vendor_name": vendor_name,
        **vendor,
    }