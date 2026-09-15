import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process and validate an invoice."
    )

    parser.add_argument(
        "--invoice",
        type=Path,
        required=True,
        help="Path to the invoice text file.",
    )

    return parser.parse_args()