from langgraph.types import Command

from app.cli import parse_args
from app.services.extraction import extract_invoice
from app.utils.file_loader import read_text_file
from app.workflows.invoice_workflow import build_invoice_workflow
from app.services.invoice_runner import run_invoice

def main():
    args = parse_args()

    if not args.invoice.exists():
        raise FileNotFoundError(
            f"Invoice file not found: {args.invoice}"
        )

    invoice, result = run_invoice(args.invoice)

    print("\n" + "=" * 50)
    print("INVOICE PROCESSING RESULT")
    print("=" * 50)
    print(f"Invoice number: {invoice.invoice_number}")
    print(f"Vendor: {invoice.seller.name}")
    print(f"Total: {invoice.total}")
    print(f"Purchase order: {invoice.purchase_order_number}")
    print(invoice.tax_rate)

    print("\nValidation result:")
    print(result.get("validation_result"))

    print("\nVendor result:")
    print(result.get("vendor_result"))

    print("\nPurchase-order result:")
    print(result.get("po_result"))

    print("\nFinal decision:")
    print(result.get("decision"))

    print("=" * 50)


if __name__ == "__main__":
    main()