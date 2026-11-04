"""
Extract Spark row metadata from a Parquet file and save it as CSV.

Usage:
    python extract_spark_metadata.py <parquet_file> [--output output.csv]
"""

import argparse
import json
import sys


def extract_spark_metadata(parquet_path: str, output_path: str | None = None) -> None:
    parquet_path = Path(parquet_path)

    if not parquet_path.exists():
        print(f"Error: File not found -> {parquet_path}", file=sys.stderr)
        sys.exit(1)

    # Read metadata
    meta = pq.read_metadata(parquet_path)

    key = b"org.apache.spark.sql.parquet.row.metadata"
    raw_value = meta.metadata.get(key) if meta.metadata else None

    if raw_value is None:
        print(
            "Error: Key 'org.apache.spark.sql.parquet.row.metadata' not found in the file.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse JSON
    try:
        schema = json.loads(raw_value.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON -> {e}", file=sys.stderr)
        sys.exit(1)

    fields = schema.get("fields", [])
    if not fields:
        print("Warning: No fields found in the schema.", file=sys.stderr)
        sys.exit(0)

    # Create DataFrame.
    df = pd.DataFrame(fields)

    # Default output name
    if output_path is None:
        output_path = parquet_path.with_suffix(".spark_metadata.csv")

    df.to_csv(output_path, index=False)
    print(f"Saved -> {output_path}")
    print(df.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(
        description="Extract Spark SQL row metadata from a Parquet file and save as CSV"
    )
    parser.add_argument("parquet_file", help="Path to the .parquet file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output CSV path (default: <parquet_file>.spark_metadata.csv)",
    )

    args = parser.parse_args()
    extract_spark_metadata(args.parquet_file, args.output)


if __name__ == "__main__":
    main()
