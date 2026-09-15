from app.llm.client import get_llm
from app.models.invoice import Invoice


def extract_invoice(invoice_text: str) -> Invoice:
    llm = get_llm()

    structured_llm = llm.with_structured_output(Invoice)

    return structured_llm.invoke(
        f"""
        Extract the invoice into the provided Invoice schema.

        IMPORTANT:
        The schema contains TWO NESTED OBJECTS:
        
        seller -> Party object
        buyer -> Party object

        The output MUST represent them like this conceptually:

        seller:
            name: "ABC Technologies Pvt Ltd"
            address: "123 MG Road, Bengaluru, Karnataka"

        buyer:
            name: "XYZ Solutions Pvt Ltd"
            address: "Bengaluru, Karnataka"

        DO NOT use flattened field names such as:
        "seller.name"
        "buyer.name"

        Use the nested seller and buyer objects defined by the schema.

        Field mapping:

        seller:
        - seller.name -> name of the company issuing the invoice
        - seller.address -> seller's address

        buyer:
        - buyer.name -> company being billed
        - buyer.address -> buyer's address

        invoice_number:
        - invoice number

        purchase_order_number:
        - purchase order number / PO number
        - return null if not present

        invoice_date:
        - invoice date

        due_date:
        - due date

        subtotal:
        - invoice subtotal

        tax:
        - GST / tax amount

        tax_rate:
        - GST / tax percentage

        total:
        - final invoice total

        payment_terms:
        - payment terms such as Net 30

        items:
        - extract ALL invoice line items

        Each item must contain:
        - description
        - quantity
        - unit_price
        - total_price

        Dates:
        - Invoice dates are written in DD/MM/YYYY format unless the
          invoice explicitly indicates another format.
        - Convert dates to YYYY-MM-DD.

        IMPORTANT:
        Extract subtotal and total directly from the invoice.
        Do not omit them even if they can be calculated.

        Invoice:
        {invoice_text}
        """
    )