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


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect CSV files from the terminal.")
    parser.add_argument("file", type=Path, help="CSV file to inspect")
    parser.add_argument(
        "--columns",
        action="store_true",
        help="Display column names",
    )
    parser.add_argument(
        "--sample", type=int, metavar="N", help="Display the first N records"
    )
    parser.add_argument(
        "--count", action="store_true", help="Display the number of data records"
    )

    args = parser.parse_args()

    if args.sample is not None and args.sample < 0:
        parser.error("--sample must be zero or greater")

    if not args.file.is_file():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    try:
        columns, row_count, sample = inspect_csv(
            args.file, sample_size=args.sample if args.sample is not None else 5
        )
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.columns:
        print("\n".join(columns))
        return 0

    if args.count:
        print(row_count)
        return 0

    print(f"File: {args.file}")
    print(f"Columns: {len(columns)}")
    print(f"Rows: {row_count}")

    print("\nColumn names:")
    for column in columns:
        print(f"  - {column}")

    print("\nSample:")
    print_table(columns, sample)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
