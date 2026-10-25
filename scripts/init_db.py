"""Создать локальную SQLite-базу из синтетической fixture."""

import argparse
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab.database import APPLICATION_ID, ROOT, create_database  # noqa: E402


def can_replace(target: Path) -> bool:
    if not target.exists():
        return True
    if not target.is_file():
        return False
    try:
        with closing(sqlite3.connect(target)) as connection:
            result = connection.execute("PRAGMA application_id").fetchone()
            return result is not None and int(result[0]) == APPLICATION_ID
    except sqlite3.Error:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать учебную SQLite-базу")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    if target == ROOT or target == ROOT / "data" or target.suffix != ".sqlite":
        parser.error("Укажите отдельный файл с расширением .sqlite")
    if not can_replace(target):
        parser.error("Существующий файл не является базой этого учебного проекта")
    temporary: Path | None = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix="shop-", suffix=".sqlite", dir=target.parent, delete=False) as file:
            temporary = Path(file.name)
        with closing(sqlite3.connect(temporary)) as connection, connection:
            create_database(connection)
        temporary.replace(target)
    except (sqlite3.Error, OSError, ValueError) as error:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        sys.stderr.write(f"Не удалось создать базу: {error}\n")
        return 1
    sys.stdout.write(f"База создана: {target}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
