from app.tools.purchase_order import lookup_purchase_order


def test_lookup_known_purchase_order():
    result = lookup_purchase_order.invoke({
        "po_number": "PO-5001"
    })

    assert result["found"] is True
    assert result["po_number"] == "PO-5001"
    assert result["vendor_name"] == "ABC Technologies Pvt Ltd"
    assert result["status"] == "approved"
    assert result["total_amount"] == 100000


def test_lookup_unknown_purchase_order():
    result = lookup_purchase_order.invoke({
        "po_number": "PO-9999"
    })

    assert result["found"] is False
    assert result["po_number"] == "PO-9999"