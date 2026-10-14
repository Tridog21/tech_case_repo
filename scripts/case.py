"""Portable entry point. Run from any directory with uv run python scripts/case.py."""

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/sample/orders.csv"
DATABASE = ROOT / "warehouse/case.duckdb"
FIELDS = ["order_id", "customer_id", "order_date", "amount", "status"]


def read_orders(path):
    rows = []
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Expected CSV columns in order: {','.join(FIELDS)}")
        for line, record in enumerate(reader, start=2):
            try:
                if None in record or any(value is None for value in record.values()):
                    raise ValueError("incorrect number of columns")
                order_id = int(record["order_id"])
                customer_id = int(record["customer_id"])
                if not (0 < order_id <= 2**63 - 1 and 0 < customer_id <= 2**63 - 1):
                    raise ValueError("identifiers must be positive 64-bit integers")
                if order_id in seen:
                    raise ValueError(f"duplicate order_id {order_id}")
                order_date = date.fromisoformat(record["order_date"])
                if order_date.isoformat() != record["order_date"]:
                    raise ValueError("date must use YYYY-MM-DD")
                amount = Decimal(record["amount"])
                if not amount.is_finite() or not Decimal("0") <= amount < Decimal("10000000000"):
                    raise ValueError("amount must be finite and between 0 and 9999999999.99")
                if amount != amount.quantize(Decimal("0.01")):
                    raise ValueError("amount must have at most two decimal places")
                status = record["status"]
                if status not in {"completed", "cancelled"}:
                    raise ValueError("status must be completed or cancelled")
                rows.append((order_id, customer_id, order_date, amount, status))
                seen.add(order_id)
            except (ValueError, InvalidOperation, TypeError) as error:
                raise ValueError(f"{path}: line {line}: {error}") from error
    if not rows:
        raise ValueError("CSV must contain at least one order")
    return rows


def load_orders(path, database=DATABASE):
    rows = read_orders(path)  # Validate all rows before replacing existing data.
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as connection:
        connection.execute("begin transaction")
        connection.execute("create schema if not exists raw")
        connection.execute("""create or replace table raw.orders (
            order_id BIGINT, customer_id BIGINT, order_date DATE,
            amount DECIMAL(12,2), status VARCHAR)""")
        connection.executemany("insert into raw.orders values (?, ?, ?, ?, ?)", rows)
        connection.execute("commit")
    print(f"Imported {len(rows)} orders from {path}", flush=True)


def command(args, env=None):
    print("+ " + " ".join(map(str, args)), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


def dbt(action):
    executable = shutil.which("dbt")
    if not executable:
        raise RuntimeError("dbt not found. Run uv sync --locked, then use uv run.")
    env = dict(os.environ, CASE_DB_PATH=DATABASE.as_posix(), DBT_SEND_ANONYMOUS_USAGE_STATS="false")
    command([executable, *action, "--project-dir", "dbt", "--profiles-dir", "dbt"], env)


def check():
    command([sys.executable, "-m", "ruff", "check", "scripts", "tests"])
    command([sys.executable, "-m", "ruff", "format", "--check", "scripts", "tests"])
    command([sys.executable, "-m", "sqlfluff", "lint", "dbt/models", "dbt/tests"])
    command([sys.executable, "-m", "pytest", "-q"])


def export_results(input_path):
    output = ROOT / "reports/generated"
    output.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        rows = connection.execute("""select order_date, completed_orders, revenue
            from analytics.daily_revenue order by order_date""").fetchall()
    with (output / "daily_revenue.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["order_date", "completed_orders", "revenue"])
        writer.writerows(rows)
    manifest = {
        "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        "lock_sha256": hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "duckdb": duckdb.__version__,
        "completed_orders": sum(row[1] for row in rows),
        "total_revenue": str(sum((row[2] for row in rows), Decimal("0.00"))),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    print(f"Results: {output}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["demo", "run", "check", "docs", "doctor"])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    if args.action == "doctor":
        print(f"Python: {sys.version}\nDuckDB: {duckdb.__version__}\nProject: {ROOT}")
        dbt(["debug"])
    elif args.action == "check":
        check()
    elif args.action == "docs":
        dbt(["docs", "generate"])
        dbt(["docs", "serve", "--host", "127.0.0.1"])
    else:
        load_orders(args.input.resolve())
        dbt(["build"])
        export_results(args.input.resolve())
        if args.action == "demo":
            expected = (ROOT / "data/sample/expected_daily_revenue.csv").read_text()
            actual = (ROOT / "reports/generated/daily_revenue.csv").read_text()
            if actual != expected:
                raise ValueError("Demo results differ from expected reference")
            check()
            dbt(["docs", "generate"])
            print("SUCCESS: reference results, quality checks and documentation verified.")


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        RuntimeError,
        OSError,
        duckdb.Error,
        subprocess.CalledProcessError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
