import argparse
import csv
import sys
from pathlib import Path
from collections.abc import Sequence


def inspect_csv(
    path: Path, sample_size: int = 5
) -> tuple[Sequence[str], int, list[dict]]:
    """Read CSV metadata and collect a sample of records.

    Args:
        path (Path): A Path object built from the directory containing the csv
        file.
        sample_size (int): The number of rows from the csv to inspect.
    Returns:
        tuple[Sequence[str], int, list[dict]]: A sequence of the columns, the
        number of rows in the sample, and the actual sample, as a list of rows,
        where each row has a dictionary representation.
    Raises:
        ValueError: If the csv file is empty or has no header (column names).
    """
    # Open for reading in text mode.
    open_mode = "r"
    text_encoding = "utf-8-sig"
    # Don't translate newline characters.
    newline_mode = ""
    with path.open(open_mode, encoding=text_encoding, newline=newline_mode) as file:
        reader = csv.DictReader(file, strict=True)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header.")

        columns = reader.fieldnames
        sample = []
        row_count = 0

        for row in reader:
            row_count += 1

            if len(sample) < sample_size:
                sample.append(row)

        return columns, row_count, sample


def print_table(columns: Sequence[str], rows: list[dict]) -> None:
    """Print records in a simple, aligned table."""
    if not rows:
        print("No records found")
        return

    # Get the widths of each column, as the max between the width of the header
    # and the width of each value.
    widths = {
        column: max(
            len(column),
            *(len(str(row.get(column) or "")) for row in rows),
        )
        for column in columns
    }

    header = " | ".join(column.ljust(widths[column]) for column in columns)
    separator = "-+-".join("-" * widths[column] for column in columns)

    print(header)
    print(separator)

    for row in rows:
        print(
            " | ".join(
                str(row.get(column) or "").ljust(widths[column]) for column in columns
            )
        )
