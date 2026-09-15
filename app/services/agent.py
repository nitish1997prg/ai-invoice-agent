import re

from app.models.decision import InvoiceDecision

from app.llm.client import get_llm
from app.tools.vendor import lookup_vendor
from app.tools.purchase_order import lookup_purchase_order
from langchain_core.messages import ToolMessage
from app.config.settings import get_settings
from app.models.invoice import Invoice

def parse_decision_response(content: str) -> InvoiceDecision:
    """
    Parse the agent's final two-line response into a validated model.
    """

    decision_match = re.search(
        r"DECISION:\s*(approve|reject|human_review)",
        content,
        re.IGNORECASE,
    )

    reason_match = re.search(
        r"REASON:\s*(.+)",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if not decision_match:
        raise ValueError(
            "Agent response did not contain a valid DECISION."
        )

    if not reason_match:
        raise ValueError(
            "Agent response did not contain a REASON."
        )

    return InvoiceDecision(
        decision=decision_match.group(1).lower(),
        reason=reason_match.group(1).strip(),
    )


def run_agent(
    invoice: Invoice,
    validation_result: dict | None = None,
    policy_context: str | None = None,
    decision_evidence: dict | None = None,
):
    llm = get_llm()
    settings = get_settings()

    tools = [
        lookup_vendor,
        lookup_purchase_order,
    ]

    llm_with_tools = llm.bind_tools(tools)

    messages = [
        (
            "system",
            """
            You are an invoice processing and approval decision agent.

            Your responsibility is to make an evidence-based decision about
            whether an invoice should be approved, rejected, or sent for
            human review.

            Decision rules:
            - Approve only when all important checks pass and no policy
              requires human review.
            - Reject when the invoice is clearly invalid or violates a
              mandatory requirement.
            - Use human_review when discrepancies, missing information,
              approval thresholds, or human judgment are involved.
            - Read the company invoice policy supplied in the context.
            - Use the approval threshold stated in the policy when deciding whether
              manager approval is required. Do not assume, invent, or hardcode a
              different threshold.

            Important:
            - Do not invent vendor, purchase-order, invoice, or policy information.
            - Deterministic validation results are authoritative.
            - The decision evidence is authoritative for derived facts.
            - Tools may be used to verify information when necessary.
            - Explain the decision using concrete evidence.
            - Mention all significant issues.

            Return exactly two lines after all necessary tool calls are complete:

            DECISION: <approve|reject|human_review>
            REASON: <concise evidence-based explanation>
            """,
        ),
        (
            "human",
            f"""
            We are processing an invoice.

            INVOICE:
            {invoice.model_dump()}

            Deterministic Invoice Validation Result:
            {validation_result}

            Business and Decision Evidence:
            {decision_evidence}

            Relevant Company Policy:
            {policy_context}

            Use the provided evidence to make the final decision.

            The final reason should mention relevant details such as:
            - Invoice calculation discrepancies
            - Vendor verification status
            - Purchase-order verification status
            - Purchase-order quantity or amount mismatches
            - Approval threshold requirements
            - Any reason human review is required

            Do not invent information.
            """,
        ),
    ]
    
    max_tool_rounds = settings.max_tool_rounds

    for _ in range(max_tool_rounds):
        response = llm_with_tools.invoke(messages)

        messages.append(response)

        # If the model has no more tool calls, it has produced its final answer.
        if not response.tool_calls:
            return parse_decision_response(response.content)

        # Execute every requested tool call in this round.
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name == "lookup_vendor":
                tool_result = lookup_vendor.invoke(tool_args)

            elif tool_name == "lookup_purchase_order":
                tool_result = lookup_purchase_order.invoke(tool_args)

            else:
                tool_result = f"Unknown tool requested: {tool_name}"

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    raise RuntimeError(
        f"Agent exceeded the maximum of {max_tool_rounds} tool-call rounds."
    )