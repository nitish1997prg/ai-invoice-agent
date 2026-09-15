# AI Invoice Processing and Validation Agent

An AI-powered invoice processing workflow built with Python, LangChain, LangGraph, Ollama, Pydantic, and ChromaDB.

The project extracts structured information from invoice documents, validates invoice data using deterministic business rules, verifies vendors and purchase orders, retrieves relevant company policy using RAG, and produces an approval or human-review decision.

The primary focus is on demonstrating practical AI engineering concepts, workflow orchestration, structured outputs, retrieval-augmented generation, business-rule validation, and human-in-the-loop processing.

---

## Features

- Extract structured invoice data from invoice documents using a local LLM
- Validate extracted data using Pydantic models
- Validate invoice calculations:
  - Line-item totals
  - Subtotal
  - Tax amount
  - Tax rate
  - Grand total
- Validate payment terms against invoice due dates
- Verify vendors against a mock vendor database
- Verify purchase orders against a mock purchase-order database
- Retrieve relevant company policies using RAG
- Use ChromaDB for vector similarity search
- Orchestrate the workflow using LangGraph
- Generate decision evidence from validation and verification results
- Support human-in-the-loop review for invoices requiring manual examination
- Inspect and execute the workflow using LangGraph Studio
- Run unit, integration, and LLM smoke tests using pytest
- Run locally using Ollama without requiring a hosted LLM API

---

## Architecture

The workflow follows this general pipeline:

```text
Invoice Document
       |
       v
LLM-Based Extraction
       |
       v
Structured Invoice Model
       |
       v
Deterministic Validation
       |
       +--------------------+
       |                    |
       v                    v
Vendor Verification   Purchase Order Verification
       |                    |
       +---------+----------+
                 |
                 v
Company Policy Retrieval
       |
       v
Decision Evidence
       |
       v
Policy-Aware Decision
       |
       +--------------------------+
       |                          |
       v                          v
Automatic Decision          Human Review
                                  |
                                  v
                           Final Decision
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| uv | Python project and dependency management |
| Pydantic | Data modelling and structured validation |
| LangChain | LLM and embedding integrations |
| LangGraph | Stateful workflow orchestration |
| Ollama | Local LLM and embedding inference |
| ChromaDB | Vector storage and similarity search |
| pytest | Unit and integration testing |
| LangSmith | Tracing and debugging |
| LangGraph Studio | Workflow visualization and execution |

---

## Project Structure

```text
ai-invoice-agent/
│
├── app/
│   ├── __init__.py
│   ├── cli.py
│   ├── main.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── models/
│   │   ├── invoice.py
│   │   ├── validation.py
│   │   ├── decision.py
│   │   └── policy.py
│   │
│   ├── llm/
│   │   └── ...
│   │
│   ├── services/
│   │   ├── extraction.py
│   │   ├── validation.py
│   │   ├── rag.py
│   │   ├── agent.py
│   │   ├── decision_evidence.py
│   │   ├── invoice_runner.py
│   │   └── policy.py
│   │
│   ├── tools/
│   │   └── ...
│   │
│   ├── workflows/
│   │   ├── invoice_workflow.py
│   │   └── studio_graph.py
│   │
│   └── utils/
│       └── file_loader.py
│
├── invoices/
│   ├── invoice_001.txt
│   ├── invoice_002_invalid_total.txt
│   ├── invoice_003_unknown_vendor.txt
│   ├── invoice_004_missing_po.txt
│   └── invoice_005_low_value.txt
│
├── knowledge/
│   └── invoice_policy.txt
│
├── chroma_db/
│   └── ...
│
├── scripts/
│   └── ...
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_validation.py
│   ├── test_decision_evidence.py
│   ├── test_vendor.py
│   ├── test_purchase_order.py
│   ├── test_integration.py
│   ├── test_invoice_files.py
│   ├── test_llm_smoke.py
│   └── test_policy.py
│
├── .env.example
├── .gitignore
├── langgraph.json
├── pyproject.toml
└── README.md
```

---

## Invoice Processing Workflow

### 1. Invoice Extraction

The invoice document is passed to a local LLM. The LLM extracts fields such as:

- Seller details
- Buyer details
- Invoice number
- Invoice and due dates
- Purchase order number
- Invoice line items
- Subtotal
- Tax
- Tax rate
- Total
- Payment terms

The extracted information is represented using Pydantic models.

Example:

```python
from pydantic import BaseModel


class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float


class Invoice(BaseModel):
    invoice_number: str
    items: list[InvoiceItem]
    subtotal: float
    tax: float
    tax_rate: float | None = None
    total: float
```

---

### 2. Deterministic Validation

The extracted invoice is validated using normal Python code rather than relying entirely on the LLM.

The validation layer checks:

#### Line-item totals

```text
sum of line-item totals = invoice subtotal
```

#### Tax calculation

```text
subtotal × tax_rate / 100 = invoice tax
```

#### Grand total

```text
subtotal + tax = invoice total
```

#### Payment terms

The invoice payment terms are checked against the due date where applicable.

Using deterministic validation makes the system more reliable for financial calculations and reduces the chance of accepting incorrect LLM-generated values.

---

### 3. Vendor Verification

The workflow checks whether the invoice vendor:

- Exists in the vendor system
- Has an active status

Example vendor result:

```python
{
    "found": True,
    "vendor_name": "ABC Technologies Pvt Ltd",
    "vendor_id": "V-1001",
    "status": "active",
}
```

An unknown or inactive vendor is recorded as an issue and can cause the invoice to be sent for human review.

---

### 4. Purchase Order Verification

The workflow checks whether:

- A purchase order exists
- The purchase order is approved

The project can be extended to perform more detailed matching, including:

- Vendor matching
- Item matching
- Quantity matching
- Unit-price matching
- Total amount matching

---

### 5. Policy Retrieval Using RAG

The company invoice policy is stored in:

```text
knowledge/invoice_policy.txt
```

The policy is split into smaller chunks and converted into embeddings using an Ollama embedding model.

The embeddings are stored in ChromaDB.

```text
Company Policy
      |
      v
Text Splitting
      |
      v
Ollama Embeddings
      |
      v
ChromaDB
```

When the workflow needs policy information, it performs a similarity search using a query related to the invoice.

```text
Workflow Query
      |
      v
Query Embedding
      |
      v
ChromaDB Similarity Search
      |
      v
Relevant Policy Chunks
      |
      v
Decision LLM
```

The decision model uses the retrieved policy context to determine how the invoice should be handled.

The approval threshold is read from the retrieved company policy rather than being hardcoded into the decision-evidence logic.

---

### 6. Decision Evidence

The decision-evidence layer gathers deterministic facts from the workflow, including:

- Invoice total
- Whether validation passed
- Validation issues
- Vendor verification status
- Vendor status
- Purchase-order verification status
- Purchase-order status
- Reasons for potential human review

This evidence is passed to the decision stage along with the relevant policy context.

The evidence layer is responsible for reporting facts. The policy-aware decision stage is responsible for applying the company policy.

---

### 7. Human-in-the-Loop Review

Invoices that contain discrepancies or require additional approval can be paused for human review.

The human reviewer can inspect:

- The invoice
- Validation results
- Vendor information
- Purchase-order information
- Retrieved policy context
- Decision evidence

The workflow can then resume with a human decision such as:

```text
approve
```

or:

```text
reject
```

This demonstrates how LangGraph can support workflows that combine automated processing with human intervention.

---

## RAG and ChromaDB

ChromaDB is used as the project's vector store.

It stores embeddings generated from the company policy and supports semantic similarity search.

The relevant components are:

- `OllamaEmbeddings` — creates vector embeddings
- `Chroma` — stores and searches the embeddings
- `retrieve_policy()` — retrieves relevant policy chunks
- `policy_node()` — incorporates policy retrieval into the LangGraph workflow

The policy vector store should generally be built once during ingestion and then reused during invoice processing.

Example commands may include:

```powershell
uv run python -m app.index_knowledge
```

The exact command depends on the indexing module included in the project.

---

## Installation

### Prerequisites

Install the following:

- Python
- uv
- Ollama
- Git

Verify the installations:

```powershell
python --version
uv --version
ollama --version
```

### Clone the repository

```powershell
git clone <your-repository-url>
cd ai-invoice-agent
```

### Install dependencies

```powershell
uv sync
```

If dependencies have not yet been installed through the project configuration, install the required packages using the project's dependency setup.

---

## Ollama Setup

Start Ollama locally.

Pull the LLM and embedding models configured in your `.env` file.

For example:

```powershell
ollama pull <your-llm-model>
ollama pull <your-embedding-model>
```

The actual model names should match the values configured in your environment.

Confirm that Ollama is running:

```powershell
ollama list
```

---


## Configuration and Secrets

The project separates application configuration from sensitive environment values.

### `app/config/settings.py`

The `settings.py` module defines and loads the application's configuration, such as:

- Ollama base URL
- LLM model name
- Embedding model name
- Policy file path
- ChromaDB storage path
- ChromaDB collection name
- Other application settings

It uses environment variables to load configurable values rather than hardcoding them throughout the application.

Example responsibilities:

```python
from app.config.settings import get_settings

settings = get_settings()

print(settings.ollama_model)
print(settings.policy_path)
```

### `.env`

The `.env` file stores environment-specific values and sensitive credentials used by the application.

The current project uses the following variables:

```env
OLLAMA_API_KEY=<your-ollama-api-key>

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your-langsmith-api-key>
LANGSMITH_PROJECT=ai-invoice-agent
```
---

## Build the Policy Vector Store

Before using policy retrieval, build the ChromaDB vector store:

```powershell
uv run python -m app.index_knowledge
```

This reads the policy document, splits it into chunks, generates embeddings, and persists the vector store locally.

The vector store is typically stored under:

```text
chroma_db/
```

---

## Running the Project

Run the application using the project's CLI entry point.

For example:

```powershell
uv run python -m app.cli
```

If the project uses a different entry point, use the command defined in `pyproject.toml`.

The workflow processes an invoice document, validates it, retrieves relevant policy information, and produces a decision or pauses for human review.

---

## Running LangGraph Studio

The project includes a Studio graph configuration in:

```text
langgraph.json
```

Example configuration:

```json
{
  "dependencies": ["."],
  "graphs": {
    "invoice_agent": "./app/workflows/studio_graph.py:graph"
  },
  "env": ".env"
}
```

Install the LangGraph CLI dependency if needed:

```powershell
uv add --dev "langgraph-cli[inmem]"
```

Start the local LangGraph development server:

```powershell
uv run langgraph dev
```

Then open the Studio URL provided by the CLI, commonly:

```text
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

Studio can be used to:

- View the workflow graph
- Provide structured invoice input
- Execute individual workflow runs
- Inspect state transitions
- View intermediate node outputs
- Debug workflow failures
- Observe human-in-the-loop interruptions

When running the graph directly in Studio, provide the invoice using the expected structured input schema.

---

## Testing

The project uses pytest.

Run the complete test suite:

```powershell
uv run pytest -v
```

Run tests without LLM-dependent tests:

```powershell
uv run pytest -m "not llm" -v
```

Run the LLM smoke test separately:

```powershell
uv run pytest tests/test_llm_smoke.py -v -s
```

The test suite covers areas such as:

- Invoice calculation validation
- Tax and tax-rate validation
- Subtotal and total validation
- Payment-term validation
- Vendor verification
- Purchase-order verification
- Decision evidence generation
- Invoice-file processing
- Integration behavior
- Local LLM extraction

LLM smoke tests require a running Ollama instance and the configured model.

---

## Example Test Scenarios

The sample invoice files cover different scenarios:

| Invoice | Scenario |
|---|---|
| `invoice_001.txt` | Valid invoice |
| `invoice_002_invalid_total.txt` | Incorrect invoice total |
| `invoice_003_unknown_vendor.txt` | Unknown vendor |
| `invoice_004_missing_po.txt` | Missing purchase order |
| `invoice_005_low_value.txt` | Lower-value invoice |

These examples help demonstrate how the workflow behaves under both valid and invalid conditions.

---

## Design Decisions

### LLMs are not responsible for all validation

The LLM is used for extracting information and assisting with policy-aware decisions.

Financial calculations and deterministic checks are handled by Python code to improve reliability.

### Policy is retrieved rather than hardcoded into the decision logic

The company policy is stored separately and retrieved through RAG. This makes it easier to update policy without rewriting the decision logic.

### Evidence is separated from decision-making

The evidence layer collects facts and validation results. The decision layer interprets those facts using the retrieved policy.

### Local models are used

Ollama allows the project to run locally without depending on a hosted LLM provider for inference.

### Human review is part of the workflow

Not every invoice should be automatically approved. The workflow supports escalation when discrepancies or policy conditions require human involvement.

---

## Current Scope

This project is a backend-oriented AI workflow prototype.

It intentionally focuses on:

- Document extraction
- Structured data modelling
- Deterministic validation
- Vendor and purchase-order verification
- RAG-based policy retrieval
- LangGraph orchestration
- Human-in-the-loop decision-making
- Testing and observability

The current version does not include:

- A frontend application
- A production REST API
- User authentication
- A persistent business database
- Multi-user support
- Background job queues
- Cloud deployment
- Production-grade infrastructure

These could be added in future versions if required.

---

## Future Improvements

Potential future improvements include:

- Add a FastAPI backend
- Add a web interface for uploading invoices
- Store invoices and decisions in PostgreSQL
- Add asynchronous invoice processing
- Add authentication and role-based access
- Add more comprehensive purchase-order matching
- Add document upload support for PDFs and images
- Add OCR for scanned invoices
- Add retry and failure-recovery mechanisms
- Add production monitoring and structured logging
- Add evaluation datasets for extraction and decision quality
- Deploy the application using Docker
- Add API and end-to-end tests

---

## Learning Objectives Demonstrated

This project demonstrates practical understanding of:

- Python application architecture
- Type-safe data modelling with Pydantic
- LLM integration
- Structured LLM output
- Embeddings and vector search
- Retrieval-augmented generation
- LangChain
- LangGraph stateful workflows
- Conditional execution
- Human-in-the-loop workflows
- Deterministic business validation
- Testing AI applications
- Local model development
- Debugging and tracing with LangSmith

---

