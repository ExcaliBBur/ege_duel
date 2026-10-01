"""Собирает банк заданий в bank/dist.

Источники:
  bank/authored/<предмет>.json  задания, написанные вручную;
  tools/generators.py           задания с вычисляемым ответом.

Запуск:  python tools/build_bank.py [--seed N] [--per-generator N]
Другой seed даёт другие числа в сгенерированных заданиях.
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import generators  # noqa: E402
import facts  # noqa: E402,F401  (добавляет в generators задания по таблицам фактов)
import figures  # noqa: E402,F401  (добавляет в generators задания с рисунками)

ROOT = Path(__file__).resolve().parent.parent
AUTHORED = ROOT / "bank" / "authored"
DIST = ROOT / "bank" / "dist"
EMBEDDED = ROOT / "bank" / "embedded"
CHUNK_CHARS = 60000  # размер одного куска встроенной копии банка

SUBJECTS = [
    "russian", "math_base", "math_prof", "physics", "chemistry", "biology",
    "informatics", "history", "social", "geography", "literature", "english",
]
KINDS = {"exact", "number", "set", "order"}
ANSWER_MAX_CHARS = 17  # как Settings.answerMaxChars в игре


def normalize(text: str) -> str:
    """То же, что Text.normalize в игре: без пробелов, строчными, ё как е, тире как минус."""
    out = []
    for ch in text:
        if ch in " \t\r\n ":
            continue
        if ch in "−–—":
            ch = "-"
        ch = ch.lower()
        if ch == "ё":
            ch = "е"
        out.append(ch)
    return "".join(out)


def check(subject: str, item: dict) -> list[str]:
    """Возвращает список ошибок в задании."""
    errors = []
    text = item.get("text")
    if not isinstance(text, str) or not text.strip():
        errors.append("пустой текст")
    answers = item.get("answers")
    if not isinstance(answers, list) or not answers:
        errors.append("нет ответов")
        answers = []
    kind = item.get("kind")
    if kind not in KINDS:
        errors.append(f"неизвестный вид проверки {kind!r}")
    if item.get("points") not in (1, 2):
        errors.append("баллы должны быть 1 или 2")
    if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
        errors.append("нет пояснения")
    for answer in answers:
        if not isinstance(answer, str) or not normalize(answer):
            errors.append("пустой ответ")
            continue
        norm = normalize(answer)
        if "." in norm:
            errors.append(f"в ответе {answer!r} точка: игра заменяет точки на запятые")
        if len(norm) > ANSWER_MAX_CHARS:
            errors.append(f"ответ {answer!r} длиннее {ANSWER_MAX_CHARS} символов")
        if kind == "number":
            try:
                float(norm.replace(",", "."))
            except ValueError:
                errors.append(f"ответ {answer!r} не число")
        if kind in ("set", "order") and not norm.isdigit():
            errors.append(f"ответ {answer!r} должен состоять из цифр")
        if kind == "set" and len(set(norm)) != len(norm):
            errors.append(f"в ответе {answer!r} повторяются цифры")
    if "figure" in item:
        errors += check_figure(item["figure"])
    return [f"{subject}: {error}: {str(text)[:60]!r}" for error in errors]


FIGURE_ITEMS = {"line": 6, "rect": 6, "circle": 5, "text": 5}  # вид фигуры и число полей
FIGURE_MAX_ITEMS = 150  # как в Bank.luau


def check_figure(figure) -> list[str]:
    if not isinstance(figure, dict) or not isinstance(figure.get("items"), list):
        return ["рисунок должен быть словарём с полем items"]
    errors = []
    width, height = figure.get("w"), figure.get("h")
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        return ["у рисунка нет размеров w и h"]
    if not 0 < len(figure["items"]) <= FIGURE_MAX_ITEMS:
        errors.append(f"в рисунке должно быть от 1 до {FIGURE_MAX_ITEMS} фигур")
    for shape in figure["items"]:
        if not isinstance(shape, list) or not shape or FIGURE_ITEMS.get(shape[0]) != len(shape):
            errors.append(f"неверная фигура в рисунке: {shape!r}")
            continue
        x, y = shape[1], shape[2]
        if not (-5 <= x <= width + 5 and -5 <= y <= height + 5):
            errors.append(f"фигура выходит за границы рисунка: {shape!r}")
    return errors


def load_authored(subject: str) -> list[dict]:
    path = AUTHORED / f"{subject}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = []
    for raw in data["tasks"]:
        answers = raw.get("answers")
        if answers is None:
            answers = [raw["answer"]]
        tasks.append({
            "group": raw.get("group", "общая"),
            "text": raw["text"],
            "answers": answers,
            "points": raw.get("points", 1),
            "kind": raw.get("kind", "exact"),
            "explanation": raw.get("explanation", ""),
        })
        if "figure" in raw:
            tasks[-1]["figure"] = raw["figure"]
    return tasks


def identity(item: dict) -> str:
    """Задания с одинаковым текстом, но разными рисунками считаются разными."""
    return item["text"] + json.dumps(item.get("figure"), sort_keys=True)


def generate(subject: str, rng: random.Random, per_generator: int, taken: set[str]) -> list[dict]:
    """taken: уже имеющиеся задания предмета, такие же генератор не добавляет."""
    tasks = []
    for generator in generators.GENERATED.get(subject, []):
        seen = set()
        attempts = 0
        while len(seen) < per_generator and attempts < per_generator * 30:
            attempts += 1
            made = generator(rng)
            # У заданий по таблицам фактов есть key: каждый факт берётся один раз.
            mark = made.get("key") or identity(made)
            if mark in seen or identity(made) in taken:
                continue
            seen.add(mark)
            name = generator.__name__
            tasks.append({
                "group": name,
                "text": made["text"],
                "answers": made.get("answers") or [made["answer"]],
                "points": made.get("points", 1),
                "kind": made.get("kind") or ("exact" if name in generators.EXACT_GENERATORS else "number"),
                "explanation": made["explanation"],
            })
            if "figure" in made:
                tasks[-1]["figure"] = made["figure"]
    return tasks


def dump_tasks(subject: str, tasks: list[dict]) -> str:
    """JSON предмета: одно задание на строку, чтобы рисунки не раздували файл."""
    lines = [json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in tasks]
    head = json.dumps({"subject": subject}, ensure_ascii=False)[:-1]
    return head + ', "tasks": [\n' + ",\n".join(lines) + "\n]}\n"


def embed(subject: str, text: str) -> None:
    """Встроенная копия банка: JSON предмета, разрезанный на текстовые куски.

    Rojo превращает .txt в StringValue. Хранить банк модулями Luau нельзя: Studio разбирает
    такие большие скрипты и из-за этого сильно теряет частоту кадров.
    """
    folder = EMBEDDED / subject
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.txt"):
        old.unlink()
    for number, start in enumerate(range(0, len(text), CHUNK_CHARS), start=1):
        (folder / f"{number:02d}.txt").write_text(text[start:start + CHUNK_CHARS], encoding="utf-8", newline="")


def build(seed: int, per_generator: int) -> int:
    rng = random.Random(seed)
    DIST.mkdir(parents=True, exist_ok=True)
    index = {"version": seed, "subjects": {}}
    errors = []

    for subject in SUBJECTS:
        authored = load_authored(subject)
        tasks = authored + generate(subject, rng, per_generator, {identity(item) for item in authored})
        seen_texts = set()
        for number, item in enumerate(tasks, start=1):
            item["id"] = f"{subject}-{number:03d}"
            errors += check(subject, item)
            if identity(item) in seen_texts:
                errors.append(f"{subject}: повтор задания: {item['text'][:60]!r}")
            seen_texts.add(identity(item))
        if not tasks:
            errors.append(f"{subject}: в предмете нет заданий")

        ordered = [
            {
                key: item[key]
                for key in ("id", "group", "text", "answers", "points", "kind", "explanation", "figure")
                if key in item
            }
            for item in tasks
        ]
        text = dump_tasks(subject, ordered)
        (DIST / f"{subject}.json").write_text(text, encoding="utf-8")
        embed(subject, text)
        index["subjects"][subject] = {"file": f"{subject}.json", "count": len(tasks)}
        print(f"{subject:12} {len(tasks):4} заданий")

    (DIST / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    for error in errors:
        print("ОШИБКА:", error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сборка банка заданий")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--per-generator", type=int, default=18)
    arguments = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(build(arguments.seed, arguments.per_generator))
