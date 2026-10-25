"""Команды работают без сети и не перезаписывают чужие базы."""

import sqlite3
import subprocess
import sys
from pathlib import Path

from lab.database import APPLICATION_ID, ROOT


def run_script(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts" / name), *arguments],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_init_creates_and_replaces_own_database(tmp_path: Path) -> None:
    target = tmp_path / "shop.sqlite"
    for _ in range(2):
        result = run_script("init_db.py", "--output", str(target))
        assert result.returncode == 0, result.stderr
        with sqlite3.connect(target) as connection:
            assert connection.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID
            assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 12


def test_init_preserves_unrelated_database(tmp_path: Path) -> None:
    target = tmp_path / "other.sqlite"
    with sqlite3.connect(target) as connection:
        connection.execute("CREATE TABLE marker (value TEXT)")
        connection.execute("INSERT INTO marker VALUES ('keep')")
    original = target.read_bytes()
    result = run_script("init_db.py", "--output", str(target))
    assert result.returncode != 0
    assert "не является базой" in result.stderr
    assert target.read_bytes() == original
