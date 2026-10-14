import csv

import duckdb
import pytest

from scripts.case import DEFAULT_INPUT, FIELDS, load_orders, read_orders


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(rows)


def test_rerun_does_not_duplicate(tmp_path):
    database = tmp_path / "case.duckdb"
    load_orders(DEFAULT_INPUT, database)
    load_orders(DEFAULT_INPUT, database)
    with duckdb.connect(str(database)) as connection:
        assert connection.execute("select count(*) from raw.orders").fetchone()[0] == 5


@pytest.mark.parametrize("amount", ["-1", "NaN", "Infinity", "1.001", "10000000000"])
def test_reject_invalid_amount(tmp_path, amount):
    path = tmp_path / "orders.csv"
    write_csv(path, [[1, 101, "2026-01-01", amount, "completed"]])
    with pytest.raises(ValueError, match="line 2"):
        read_orders(path)


def test_invalid_import_preserves_existing_data(tmp_path):
    database = tmp_path / "case.duckdb"
    load_orders(DEFAULT_INPUT, database)
    path = tmp_path / "invalid.csv"
    write_csv(path, [[1, 101, "2026-01-01", "5.00", "completed"]] * 2)
    with pytest.raises(ValueError, match="duplicate"):
        load_orders(path, database)
    with duckdb.connect(str(database)) as connection:
        assert connection.execute("select count(*) from raw.orders").fetchone()[0] == 5


@pytest.mark.parametrize("field,value", [(2, "bad-date"), (4, "unknown"), (0, "0")])
def test_reject_invalid_fields(tmp_path, field, value):
    row = [1, 101, "2026-01-01", "5.00", "completed"]
    row[field] = value
    path = tmp_path / "orders.csv"
    write_csv(path, [row])
    with pytest.raises(ValueError, match="line 2"):
        read_orders(path)


def test_reject_empty_file(tmp_path):
    path = tmp_path / "orders.csv"
    write_csv(path, [])
    with pytest.raises(ValueError, match="at least one"):
        read_orders(path)
