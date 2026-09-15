from app.tools.vendor import lookup_vendor


def test_lookup_known_vendor():
    result = lookup_vendor.invoke({
        "vendor_name": "ABC Technologies Pvt Ltd"
    })

    assert result["found"] is True
    assert result["vendor_name"] == "ABC Technologies Pvt Ltd"
    assert result["vendor_id"] == "V-1001"
    assert result["status"] == "active"
    assert result["payment_terms"] == "Net 30"


def test_lookup_unknown_vendor():
    result = lookup_vendor.invoke({
        "vendor_name": "Unknown Vendor Pvt Ltd"
    })

    assert result["found"] is False
    assert result["vendor_name"] == "Unknown Vendor Pvt Ltd"