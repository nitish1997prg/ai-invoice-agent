import re
import math
from datetime import timedelta

from app.models.invoice import Invoice
from app.models.validation import ValidationIssue, ValidationResult


def validate_payment_terms(invoice: Invoice) -> ValidationIssue | None:
    if not invoice.payment_terms:
        return None

    match = re.fullmatch(
        r"Net\s+(\d+)",
        invoice.payment_terms.strip(),
        re.IGNORECASE,
    )

    if not match:
        return None

    days = int(match.group(1))

    expected_due_date = invoice.invoice_date + timedelta(days=days)

    if invoice.due_date != expected_due_date:
        return ValidationIssue(
            field="due_date",
            message=(
                f"Payment terms are {invoice.payment_terms}, so the expected "
                f"due date is {expected_due_date}, but the invoice says "
                f"{invoice.due_date}."
            ),
            severity="error",
        )

    return None


def validate_invoice(invoice: Invoice) -> ValidationResult:
    issues = []

    # Check line items against subtotal
    calculated_subtotal = sum(
        item.total_price for item in invoice.items
    )

    if not math.isclose(
        calculated_subtotal,
        invoice.subtotal,
        rel_tol=0,
        abs_tol=0.01,
    ):
        issues.append(
            ValidationIssue(
                field="subtotal",
                message=(
                    f"Line items total {calculated_subtotal}, "
                    f"but invoice subtotal is {invoice.subtotal}"
                ),
                severity="error",
            )
        )

    # Check tax against tax rate
    if invoice.tax_rate is not None:
        calculated_tax = invoice.subtotal * (
            invoice.tax_rate / 100
        )

        if not math.isclose(
            calculated_tax,
            invoice.tax,
            rel_tol=0,
            abs_tol=0.01,
        ):
            issues.append(
                ValidationIssue(
                    field="tax",
                    message=(
                        f"Subtotal {invoice.subtotal} at tax rate "
                        f"{invoice.tax_rate}% gives expected tax "
                        f"{calculated_tax:.2f}, but invoice tax is "
                        f"{invoice.tax:.2f}"
                    ),
                    severity="error",
                )
            )

    # Check subtotal + tax against total
    calculated_total = invoice.subtotal + invoice.tax

    if not math.isclose(
        calculated_total,
        invoice.total,
        rel_tol=0,
        abs_tol=0.01,
    ):
        issues.append(
            ValidationIssue(
                field="total",
                message=(
                    f"Subtotal + tax equals {calculated_total}, "
                    f"but invoice total is {invoice.total}"
                ),
                severity="error",
            )
        )

    # Check payment terms against due date
    payment_terms_issue = validate_payment_terms(invoice)

    if payment_terms_issue:
        issues.append(payment_terms_issue)

    return ValidationResult(
        is_valid=len(issues) == 0,
        issues=issues,
    )