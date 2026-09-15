from typing import TypedDict

from app.models.invoice import Invoice
from app.models.decision import InvoiceDecision
from app.models.validation import ValidationResult


from app.tools.vendor import lookup_vendor
from app.tools.purchase_order import lookup_purchase_order

from app.llm.client import get_llm

from app.services.rag import retrieve_policy
from app.services.validation import validate_invoice
from app.services.decision_evidence import build_decision_evidence
from app.services.agent import run_agent

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END


class InvoiceInputState(TypedDict):
    invoice: Invoice

class InvoiceState(TypedDict,total=False):
    invoice: Invoice
    validation_result: ValidationResult | None
    vendor_result: dict | None
    po_result: dict | None
    policy_context: str | None
    decision_evidence: dict | None
    decision: dict | None
    

def validate_node(state: InvoiceState):
    invoice = state["invoice"]

    if isinstance(invoice, dict):
        invoice = Invoice.model_validate(invoice)

    result = validate_invoice(invoice)

    return {
        "invoice": invoice,
        "validation_result": result,
    }

def vendor_node(state: InvoiceState):
    invoice = state["invoice"]

    result = lookup_vendor.invoke(
        {
            "vendor_name": invoice.seller.name
        }
    )

    return {
        "vendor_result": result
    }

def purchase_order_node(state: InvoiceState):
    invoice = state["invoice"]

    if not invoice.purchase_order_number:
        return {
            "po_result": {
                "found": False,
                "reason": "No purchase order number found."
            }
        }

    result = lookup_purchase_order.invoke(
        {
            "po_number": invoice.purchase_order_number
        }
    )

    return {
        "po_result": result
    }

def policy_node(state: InvoiceState):
    invoice = state["invoice"]

    query = (
        f"Review company policy for invoice {invoice.invoice_number}. "
        f"Determine the relevant rules for approval, vendor verification, "
        f"purchase order matching, payment terms, discrepancies, and human review. "
        f"Invoice total: {invoice.total}. "
        f"Payment terms: {invoice.payment_terms}. "
        f"Purchase order: {invoice.purchase_order_number}."
    )

    policy_context = retrieve_policy(query)

    return {
        "policy_context": policy_context
    }

def decision_evidence_node(state: InvoiceState):
    validation_result = state["validation_result"]

    if validation_result is None:
        raise ValueError(
            "Validation result is required before building decision evidence."
        )

    evidence = build_decision_evidence(
        invoice=state["invoice"],
        validation_result=validation_result,
        vendor_result=state["vendor_result"],
        po_result=state["po_result"],
        policy_context=state["policy_context"],
    )

    return {
        "decision_evidence": evidence
    }

def agent_node(state: InvoiceState):
    decision = run_agent(
        invoice=state["invoice"],
        validation_result=state["validation_result"],
        policy_context=state["policy_context"],
        decision_evidence=state["decision_evidence"],
    )

    return {
        "decision": decision.model_dump()
    }

def approve_node(state: InvoiceState):
    return {
        "decision": {
            **state["decision"],
            "action": "invoice_approved",
        }
    }


def reject_node(state: InvoiceState):
    return {
        "decision": {
            **state["decision"],
            "action": "invoice_rejected",
        }
    }

def route_decision(state: InvoiceState):
    decision = state["decision"]["decision"]

    if decision == "approve":
        return "approve"

    if decision == "reject":
        return "reject"

    return "human_review"

def route_human_decision(state: InvoiceState):
    decision = state["decision"]["human_decision"]

    if decision == "approve":
        return "approve"

    return "reject"

def human_review_node(state: InvoiceState):
    decision = interrupt({
        "message": "This invoice requires human review.",
        "invoice_number": state["invoice"].invoice_number,
        "reason": state["decision"]["reason"],
    })

    return {
        "decision": {
            **state["decision"],
            "human_decision": decision,
        }
    }

    
def build_invoice_workflow(checkpointer=None):

    graph = StateGraph(InvoiceState,input_schema=InvoiceInputState)

    graph.add_node("validate", validate_node)
    graph.add_node("vendor_check", vendor_node)
    graph.add_node("po_check", purchase_order_node)
    graph.add_node("approve", approve_node)
    graph.add_node("reject", reject_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("policy_check", policy_node)
    graph.add_node("decision_evidence",decision_evidence_node)
    graph.add_node("agent",agent_node)


    graph.add_edge(START, "validate")
    graph.add_edge("validate", "vendor_check")
    graph.add_edge("vendor_check", "po_check")
    graph.add_edge("po_check","policy_check")
    graph.add_edge("policy_check", "decision_evidence")
    graph.add_edge("decision_evidence","agent")
    graph.add_conditional_edges(
        "agent",
        route_decision,
        {
            "approve": "approve",
            "reject": "reject",
            "human_review": "human_review",
        },  
    )
    graph.add_edge("approve", END)
    graph.add_edge("reject", END)
     # Human review does NOT go directly to END anymore.
    graph.add_conditional_edges(
        "human_review",
        route_human_decision,
        {
            "approve": "approve",
            "reject": "reject",
        },
    )

    return graph.compile(checkpointer=checkpointer)


   

  