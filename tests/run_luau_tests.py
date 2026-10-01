"""Запускает тесты игровой логики в luau.exe.

Модули игры обращаются друг к другу через require(script.Parent.X), чего вне Roblox нет.
Поэтому скрипт склеивает один файл: подделка окружения Roblox, модули игры, тесты.

Запуск:  python tests/run_luau_tests.py
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LUAU = ROOT / "tools" / "bin" / "luau.exe"

# Порядок важен: модуль должен идти после тех, от кого зависит.
MODULES = [
    ("Text", "src/shared/Text.luau"),
    ("Settings", "src/shared/Settings.luau"),
    ("Subjects", "src/shared/Subjects.luau"),
    ("Scoring", "src/shared/Scoring.luau"),
    ("Calculator", "src/shared/Calculator.luau"),
    ("Variant", "src/server/Variant.luau"),
    ("Config", "src/server/Config.luau"),
    ("RealBank", "src/server/Bank.luau"),
    ("Duel", "src/server/Duel.luau"),
]

REQUIRE = re.compile(r"require\((?:Shared|script\.Parent)\.(\w+)\)")


def bundle() -> str:
    parts = [(ROOT / "tests" / "mock_roblox.luau").read_text(encoding="utf-8")]
    parts.append("local M = { Bank = mockBank }")
    for name, path in MODULES:
        source = (ROOT / path).read_text(encoding="utf-8")
        source = REQUIRE.sub(r"M.\1", source)
        parts.append(f"M.{name} = (function()\n{source}\nend)()")
    parts.append((ROOT / "tests" / "logic_test.luau").read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    if not LUAU.exists():
        print(f"Не найден {LUAU}. Скачайте luau-windows.zip со страницы релизов github.com/luau-lang/luau.")
        return 2
    with tempfile.TemporaryDirectory() as folder:
        script = Path(folder) / "bundle.luau"
        script.write_text(bundle(), encoding="utf-8")
        result = subprocess.run([str(LUAU), str(script)], capture_output=True, text=True, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(result.stdout, end="")
    print(result.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
