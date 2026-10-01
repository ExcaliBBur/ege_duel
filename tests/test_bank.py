"""Тесты сборки банка. Запуск: python -m unittest discover tests"""

import random
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_bank  # noqa: E402
import generators  # noqa: E402
import figures  # noqa: E402


class DecTest(unittest.TestCase):
    def test_formats_like_ege(self):
        self.assertEqual(generators.dec(5), "5")
        self.assertEqual(generators.dec(Fraction(1, 2)), "0,5")
        self.assertEqual(generators.dec(Fraction(-41, 4)), "-10,25")
        self.assertEqual(generators.dec(Fraction(81, 100)), "0,81")
        self.assertEqual(generators.dec(Fraction(1, 20)), "0,05")

    def test_rejects_infinite_fraction(self):
        with self.assertRaises(ValueError):
            generators.dec(Fraction(1, 3))


class PolyTest(unittest.TestCase):
    def test_signs_and_unit_coefficients(self):
        self.assertEqual(generators.poly([(1, "x²"), (-5, "x"), (6, "")]), "x² - 5x + 6")
        self.assertEqual(generators.poly([(-1, "x³"), (0, "x²"), (1, "x"), (-1, "")]), "-x³ + x - 1")


class GeneratorsTest(unittest.TestCase):
    def test_every_generator_gives_valid_tasks(self):
        rng = random.Random(1)
        for subject, functions in generators.GENERATED.items():
            for function in functions:
                for _ in range(300):
                    made = function(rng)
                    item = {
                        "text": made["text"],
                        "answers": made.get("answers") or [made["answer"]],
                        "points": 1,
                        "kind": "exact" if function.__name__ in generators.EXACT_GENERATORS else "number",
                        "explanation": made["explanation"],
                    }
                    self.assertEqual(build_bank.check(subject, item), [], function.__name__)

    def test_known_answers(self):
        # Ответы пересчитаны независимо от формул генераторов.
        self.assertEqual(generators.dec(Fraction(340, 85)), "4")
        ways = generators.inf_robot(_Fixed([1, 10]))
        self.assertEqual(ways["answer"], "14")  # программ из 1 в 10 командами +1 и *2


class FiguresTest(unittest.TestCase):
    def test_symbols(self):
        self.assertEqual(generators.sup("x + 6"), "ˣ⁺⁶")
        self.assertEqual(generators.sub(12), "₁₂")
        self.assertEqual(generators.chem("H2SO4"), "H₂SO₄")
        self.assertEqual(generators.chem("Ca(OH)2"), "Ca(OH)₂")
        self.assertEqual(generators.chem("2H2O"), "2H₂O")
        self.assertEqual(generators.chem("C2H5OH"), "C₂H₅OH")

    def test_triangle_area(self):
        self.assertEqual(figures.triangle_area([(0, 0), (4, 0), (0, 3)]), 6)
        self.assertEqual(figures.triangle_area([(1, 1), (4, 2), (2, 5)]), Fraction(11, 2))

    def test_path_under_graph(self):
        # Разгон 0 -> 4 за 2 с, затем 4 с с постоянной скоростью 4: 4 + 16 = 20.
        self.assertEqual(figures.path_under_graph([0, 2, 6, 8], [0, 4, 4, 0], 2), 20)

    def test_shortest_path(self):
        roads = {("А", "Б"): 2, ("Б", "Е"): 9, ("А", "В"): 5, ("В", "Е"): 1, ("Б", "В"): 1}
        self.assertEqual(figures.shortest_path(roads, "А", "Е"), 4)  # А-Б-В-Е

    def test_figure_validation(self):
        good = {"w": 100, "h": 100, "items": [["line", 0, 0, 10, 10, 1]]}
        self.assertEqual(build_bank.check_figure(good), [])
        self.assertTrue(build_bank.check_figure({"w": 100, "h": 100, "items": [["line", 0, 0, 10]]}))
        self.assertTrue(build_bank.check_figure({"w": 100, "h": 100, "items": [["line", 500, 0, 10, 10, 1]]}))
        self.assertTrue(build_bank.check_figure({"items": []}))


class _Fixed:
    """Подставляет заранее заданные числа вместо случайных."""

    def __init__(self, values):
        self.values = list(values)

    def randint(self, _a, _b):
        return self.values.pop(0)


class CheckTest(unittest.TestCase):
    def good(self, **changes):
        item = {"text": "Вопрос", "answers": ["12"], "points": 1, "kind": "exact", "explanation": "Потому что."}
        item.update(changes)
        return item

    def test_accepts_good_task(self):
        self.assertEqual(build_bank.check("x", self.good()), [])

    def test_flags_problems(self):
        self.assertTrue(build_bank.check("x", self.good(answers=[])))
        self.assertTrue(build_bank.check("x", self.good(kind="number", answers=["abc"])))
        self.assertTrue(build_bank.check("x", self.good(kind="set", answers=["113"])))
        self.assertTrue(build_bank.check("x", self.good(points=3)))
        self.assertTrue(build_bank.check("x", self.good(kind="number", answers=["0.5"])))
        self.assertTrue(build_bank.check("x", self.good(answers=["очень длинный ответ на задание"])))

    def test_normalize_matches_game_rules(self):
        self.assertEqual(build_bank.normalize(" Спустя  Рукава "), "спустярукава")
        self.assertEqual(build_bank.normalize("Ёж"), "еж")
        self.assertEqual(build_bank.normalize("−3"), "-3")


class AuthoredBankTest(unittest.TestCase):
    def test_all_subjects_have_enough_tasks(self):
        for subject in build_bank.SUBJECTS:
            total = len(build_bank.load_authored(subject)) + 6 * len(generators.GENERATED.get(subject, []))
            self.assertGreaterEqual(total, 20, subject)  # самый длинный матч: 20 заданий

    def test_authored_tasks_are_valid(self):
        for subject in build_bank.SUBJECTS:
            for item in build_bank.load_authored(subject):
                self.assertEqual(build_bank.check(subject, item), [])


if __name__ == "__main__":
    unittest.main()
