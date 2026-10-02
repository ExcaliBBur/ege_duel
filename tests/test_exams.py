"""Тесты предметов, разбитых по номерам ЕГЭ. Запуск: python -m unittest discover tests"""

import random
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_bank  # noqa: E402
import exams  # noqa: E402


def number_of(answer: str) -> Fraction:
    return Fraction(answer.replace(",", "."))


class StructureTest(unittest.TestCase):
    def test_numbers_go_in_order_without_gaps_except_skipped(self):
        for subject, entries in exams.EXAMS.items():
            numbers = [entry.number for entry in entries]
            self.assertEqual(numbers, sorted(set(numbers)), subject)
            skipped = exams.SKIPPED.get(subject, {})
            expected = [n for n in range(1, exams.PART_ONE[subject] + 1) if n not in skipped]
            self.assertEqual(numbers, expected, f"{subject}: номера первой части")

    def test_every_generator_gives_valid_tasks(self):
        rng = random.Random(11)
        for subject, entries in exams.EXAMS.items():
            for entry in entries:
                for generator in entry.generators:
                    for _ in range(150):
                        made = generator(rng)
                        item = {
                            "text": made["text"],
                            "answers": made.get("answers") or [made["answer"]],
                            "points": made.get("points", entry.points),
                            "kind": made.get("kind") or "number",
                            "explanation": made["explanation"],
                        }
                        if "figure" in made:
                            item["figure"] = made["figure"]
                        self.assertEqual(build_bank.check(subject, item), [], f"{subject} №{entry.number} {generator.__name__}")

    def test_every_number_fills_its_quota(self):
        for subject in exams.EXAMS:
            tasks = build_bank.generate_numbered(subject, random.Random(3), 20)
            counts = {}
            for item in tasks:
                counts[item["number"]] = counts.get(item["number"], 0) + 1
            for entry in exams.EXAMS[subject]:
                self.assertEqual(counts.get(entry.number), 20, f"{subject} №{entry.number}")


class MathProfileTest(unittest.TestCase):
    """Независимая проверка ответов: уравнения подстановкой, вероятности перебором."""

    def setUp(self):
        import exam_math_prof
        self.m = exam_math_prof
        self.rng = random.Random(21)

    def test_quadratic_roots_satisfy_equation(self):
        pattern = re.compile(r"уравнение x²(?: ([+-]) (\d*)x)?(?: ([+-]) (\d+))? = 0")
        for _ in range(200):
            made = self.m.e_quadratic(self.rng)
            match = pattern.search(made["text"])
            self.assertIsNotNone(match, made["text"])
            b = int(match.group(2) or 1) * (1 if match.group(1) == "+" else -1) if match.group(1) else 0
            c = int(match.group(4)) * (1 if match.group(3) == "+" else -1) if match.group(3) else 0
            x = number_of(made["answer"])
            self.assertEqual(x * x + b * x + c, 0, made["text"])
            other = -b - x  # второй корень по теореме Виета
            if "меньший" in made["text"]:
                self.assertLessEqual(x, other)
            else:
                self.assertGreaterEqual(x, other)

    def test_rational_equation(self):
        for _ in range(200):
            made = self.m.e_rational(self.rng)
            match = re.search(r"\(x (.) (\d+)\) : \(x (.) (\d+)\) = (-?\d+)", made["text"])
            if not match:
                continue
            b = int(match.group(2)) * (1 if match.group(1) == "+" else -1)
            a = int(match.group(4)) * (1 if match.group(3) == "+" else -1)
            x = number_of(made["answer"])
            self.assertEqual((x + b) / (x + a), int(match.group(5)), made["text"])

    def test_dice_probability_by_enumeration(self):
        for _ in range(60):
            made = self.m.pr_dice(self.rng)
            total = int(re.search(r"выпадет (\d+) очк", made["text"]).group(1))
            count = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == total)
            self.assertAlmostEqual(float(number_of(made["answer"])), count / 36, delta=0.005)

    def test_boat_answer_satisfies_condition(self):
        for _ in range(100):
            made = self.m.w_boat(self.rng)
            numbers = [int(n) for n in re.findall(r"\d+", made["text"])]
            distance, difference, known = numbers[0], numbers[1], numbers[2]
            answer = number_of(made["answer"])
            boat, current = (known, answer) if "скорость течения, если" in made["text"] else (answer, known)
            self.assertEqual(Fraction(distance) / (boat - current) - Fraction(distance) / (boat + current), difference, made["text"])

    def test_ball_stays_above_level_for_the_stated_time(self):
        for _ in range(100):
            made = self.m.a_ball(self.rng)
            match = re.search(r"h\(t\) = ([\d,]+) \+ ([\d,]+)t - 5t².*не менее ([\d,]+) метров", made["text"])
            h0, v, level = (number_of(match.group(i)) for i in (1, 2, 3))
            # h0 + v t - 5t² = level: расстояние между корнями равно √D / 5
            discriminant = v * v + 20 * (h0 - level)
            self.assertAlmostEqual(float(number_of(made["answer"])), float(discriminant) ** 0.5 / 5, places=9)

    def test_expectation_from_table(self):
        for _ in range(100):
            made = self.m.st_table(self.rng)
            items = [shape[3] for shape in made["figure"]["items"] if shape[0] == "text"]
            half = len(items) // 2
            values = [number_of(v) for v in items[1:half]]
            probabilities = [number_of(v) for v in items[half + 1:]]
            self.assertEqual(sum(probabilities), 1)
            self.assertEqual(sum(v * p for v, p in zip(values, probabilities)), number_of(made["answer"]))

    def test_vector_sum_length(self):
        for _ in range(200):
            made = self.m.v_sum_length(self.rng)
            ax, ay, bx, by = (int(n) for n in re.findall(r"-?\d+", made["text"])[:4])
            if "a + b" in made["text"] and "2a" not in made["text"]:
                x, y = ax + bx, ay + by
            elif "a - b" in made["text"]:
                x, y = ax - bx, ay - by
            else:
                x, y = 2 * ax + bx, 2 * ay + by
            self.assertEqual(x * x + y * y, number_of(made["answer"]) ** 2, made["text"])


if __name__ == "__main__":
    unittest.main()
