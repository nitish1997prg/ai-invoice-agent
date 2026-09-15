from datetime import date

from pydantic import BaseModel


class Party(BaseModel):
    name: str
    address: str | None = None


class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float


class Invoice(BaseModel):
    seller: Party
    buyer: Party
    invoice_number: str
    invoice_date: date
    due_date: date
    purchase_order_number: str | None = None
    items: list[InvoiceItem]
    subtotal: float
    tax: float
    tax_rate: float | None = None
    total: float
    payment_terms: str | None = None