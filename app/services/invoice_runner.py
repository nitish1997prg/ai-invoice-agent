from pathlib import Path

from langgraph.types import Command

from app.services.extraction import extract_invoice
from app.utils.file_loader import read_text_file
from app.workflows.invoice_workflow import build_invoice_workflow
from langgraph.checkpoint.memory import InMemorySaver


def run_invoice(invoice_path: str | Path):
    invoice_text = read_text_file(invoice_path)
    invoice = extract_invoice(invoice_text)
    checkpointer = InMemorySaver()

    workflow = build_invoice_workflow(checkpointer=checkpointer)

    config = {
        "configurable": {
            "thread_id": f"invoice-{invoice.invoice_number}"
        }
    }

    initial_state = {
        "invoice": invoice,
        "validation_result": None,
        "vendor_result": None,
        "po_result": None,
        "policy_context": None,
        "decision": None,
    }

    result = workflow.invoke(
        initial_state,
        config=config,
    )

    if "__interrupt__" in result:
        print("\nWorkflow paused for human review.")
        print(f"Invoice: {invoice.invoice_number}")
        print(f"Reason: {result['decision']['reason']}")

        human_decision = input(
            "\nHuman decision (approve/reject): "
        ).strip().lower()

        while human_decision not in {"approve", "reject"}:
            human_decision = input(
                "Please enter 'approve' or 'reject': "
            ).strip().lower()

        result = workflow.invoke(
            Command(resume=human_decision),
            config=config,
        )

    return invoice, result