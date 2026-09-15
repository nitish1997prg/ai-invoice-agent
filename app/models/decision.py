from typing import Literal

from pydantic import BaseModel


class InvoiceDecision(BaseModel):
    decision: Literal["approve", "reject", "human_review"]
    reason: str