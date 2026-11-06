import argparse
import csv
import sys
from typing import Literal
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
