"""CLI локальной самопроверки SQL."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab.checker import CheckError, Task, check_task, smoke  # noqa: E402
from lab.reference import DataQualityError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверить локальный SQL на исходных и изменённых данных")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--smoke", action="store_true", help="проверить исходные таблицы и сам стенд")
    action.add_argument("--task", choices=[task.value for task in Task if task is not Task.FINAL])
    action.add_argument("--final", action="store_true", help="проверить итоговый отчёт")
    args = parser.parse_args()
    try:
        if args.smoke:
            smoke()
            sys.stdout.write("OK: исходные таблицы, ключи и независимые расчёты\n")
        else:
            task = Task.FINAL if args.final else Task(args.task)
            check_task(task)
            sys.stdout.write(f"OK: {task.value} — исходные и изменённые данные\n")
    except (CheckError, DataQualityError, OSError, ValueError) as error:
        sys.stderr.write(f"Ошибка проверки: {error}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
