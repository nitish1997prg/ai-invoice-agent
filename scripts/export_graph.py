from pathlib import Path
import sys

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.workflows.invoice_workflow import build_invoice_workflow


def main():
    graph = build_invoice_workflow()

    output_path = PROJECT_ROOT / "invoice_workflow.png"

    graph.get_graph().draw_mermaid_png(
        output_file_path=str(output_path)
    )

    print(f"Graph exported to: {output_path}")


if __name__ == "__main__":
    main()