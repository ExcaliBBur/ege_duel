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
            minimum = exams.MINIMUM.get(subject, exams.DEFAULT_MINIMUM)
            for entry in exams.EXAMS[subject]:
                self.assertGreaterEqual(counts.get(entry.number, 0), minimum, f"{subject} №{entry.number}")
                self.assertLessEqual(counts.get(entry.number, 0), 20, f"{subject} №{entry.number}")


class PartTwoTest(unittest.TestCase):
    """Вторая часть: расчётные задачи с числом в ответе и развёрнутые ответы с эталоном и критериями."""

    def test_numbers_do_not_clash_with_part_one(self):
        for subject, entries in exams.PART_TWO.items():
            numbers = [entry.number for entry in entries]
            self.assertEqual(numbers, sorted(set(numbers)), subject)
            first = {entry.number for entry in exams.EXAMS[subject]}
            self.assertFalse(first & set(numbers), f"{subject}: номер есть в обеих частях")

    def test_every_generator_gives_valid_tasks(self):
        rng = random.Random(12)
        for subject, entries in exams.PART_TWO.items():
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
                            "part": 2,
                        }
                        if "criteria" in made:
                            item["criteria"] = made["criteria"]
                        self.assertEqual(build_bank.check(subject, item), [], f"{subject} №{entry.number} {generator.__name__}")
                        self.assertLessEqual(len(made["text"]), 2500, f"{subject} №{entry.number}: слишком длинное условие")

    def test_every_number_has_enough_variants(self):
        for subject in exams.PART_TWO:
            tasks = build_bank.generate_numbered(subject, random.Random(3), 20, part=2)
            self.assertTrue(all(item["part"] == 2 for item in tasks))
            counts = {}
            for item in tasks:
                counts[item["number"]] = counts.get(item["number"], 0) + 1
            for entry in exams.PART_TWO[subject]:
                self.assertGreaterEqual(counts.get(entry.number, 0), exams.PART_TWO_MINIMUM, f"{subject} №{entry.number}")

    def test_russian_essay_uses_the_stories_of_part_one(self):
        # Сочинение пишется по тому же тексту, что и задания 23-26: у них общий context.
        first = build_bank.generate_numbered("russian", random.Random(3), 20)
        stories = {item["context"] for item in first if item.get("context", "").startswith("story:")}
        second = {item["context"] for item in build_bank.generate_numbered("russian", random.Random(3), 20, part=2)}
        self.assertEqual(stories, second)

    def test_check_rules_for_essays(self):
        good = {"text": "Вопрос", "answers": ["-"], "points": 6, "kind": "essay", "explanation": "Эталон.", "criteria": ["1 балл: верно."], "part": 2}
        self.assertEqual(build_bank.check("x", good), [])
        self.assertTrue(build_bank.check("x", {**good, "criteria": []}))
        self.assertTrue(build_bank.check("x", {**good, "points": 26}))
        self.assertTrue(build_bank.check("x", {key: value for key, value in good.items() if key != "part"}))
        self.assertTrue(build_bank.check("x", {**good, "kind": "number", "answers": ["5"]}))  # критерии без развёрнутого ответа

    def test_loan_with_equal_payments_is_repaid(self):
        import part2_math
        rng = random.Random(4)
        for _ in range(100):
            made = part2_math.e_equal_payments(rng)
            total, rate = (int(n) for n in re.search(r"сумму (\d+) тыс.*возрастает на (\d+)%", made["text"]).groups())
            payment = number_of(re.search(r"= (\d+) тыс. рублей", made["explanation"]).group(1))
            q = Fraction(100 + rate, 100)
            self.assertEqual((total * q - payment) * q - payment, 0, made["text"])
            expected = 2 * payment - total if "больше суммы кредита" in made["text"] else payment
            self.assertEqual(number_of(made["answer"]), expected)

    def test_decreasing_debt_total_by_direct_sum(self):
        import part2_math
        rng = random.Random(4)
        for _ in range(100):
            made = part2_math.e_decreasing_debt(rng)
            total, months, rate = (int(n) for n in re.search(r"сумму (\d+) тыс. рублей на (\d+) месяц.*возрастает на (\d+)%", made["text"], re.S).groups())
            paid = sum(Fraction(total, months) + Fraction(total * (months - k), months) * rate / 100 for k in range(months))
            self.assertEqual(number_of(made["answer"]), paid, made["text"])

    def test_pyramid_distance(self):
        import part2_math
        rng = random.Random(4)
        for _ in range(60):
            made = part2_math.s_pyramid(rng)
            side, height = (int(n) for n in re.search(r"основания равна (\d+), а высота равна (\d+)", made["text"]).groups())
            # Расстояние от центра до грани: в прямоугольном треугольнике с катетами side/2 и height это высота к гипотенузе.
            distance = (side / 2) * height / ((side / 2) ** 2 + height ** 2) ** 0.5
            factor = 2 if "от вершины A" in made["text"] else 1
            self.assertAlmostEqual(float(number_of(made["answer"])), factor * distance, places=9)

    def test_lens_answers_satisfy_lens_formula(self):
        import part2_physics
        rng = random.Random(4)
        for _ in range(100):
            made = part2_physics.e_lens(rng)
            distance, focus = (number_of(n) for n in re.search(r"расстоянии ([\d,]+) см от.*расстоянием (\d+) см", made["text"]).groups())
            image = 1 / (1 / focus - 1 / distance)
            if "изображение предмета" in made["text"]:
                self.assertEqual(number_of(made["answer"]), image)
            else:
                self.assertAlmostEqual(float(number_of(made["answer"])), float(image / distance), delta=0.005)

    def test_chemistry_mass_fraction(self):
        import part2_chemistry
        rng = random.Random(4)
        for _ in range(100):
            made = part2_chemistry.c_zinc(rng)
            zinc, solution, share = (number_of(n) for n in re.search(r"массой ([\d,]+) г полностью растворили в (\d+) г (\d+)%", made["text"]).groups())
            moles = zinc / 65
            self.assertGreater(solution * share / 100 / Fraction(73, 2), 2 * moles)  # кислоты хватает
            self.assertAlmostEqual(float(number_of(made["answer"])), float(136 * moles / (solution + zinc - 2 * moles) * 100), delta=0.05)

    def test_longitude_matches_time_difference(self):
        import part2_humanities
        rng = random.Random(4)
        for _ in range(100):
            made = part2_humanities.g_longitude(rng)
            hours, minutes = (int(n) for n in re.search(r"меридиане (\d+) ч (\d+) мин", made["text"]).groups())
            # Полдень в Гринвиче в 12:00; каждый градус к востоку приближает местный полдень на 4 минуты.
            self.assertEqual(number_of(made["answer"]), Fraction(12 * 60 - (hours * 60 + minutes), 4))


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


class PhysicsTest(unittest.TestCase):
    def setUp(self):
        import exam_physics
        self.p = exam_physics
        self.rng = random.Random(8)

    def test_lens_data_satisfies_lens_formula(self):
        for distance, image, focus in self.p.LENS + self.p.LENS_CASES:
            self.assertEqual(Fraction(1, distance) + Fraction(1, image), Fraction(1, focus), (distance, image, focus))

    def test_change_tables_use_valid_codes(self):
        for table in (self.p.MECHANICS_CHANGES, self.p.THERMAL_CHANGES, self.p.ELECTRIC_CHANGES, self.p.QUANTUM_CHANGES):
            for scenario, _, quantities, explanation in table:
                self.assertGreaterEqual(len(quantities), 3, scenario)
                self.assertTrue(all(code in (1, 2, 3) for code in quantities.values()), scenario)
                self.assertTrue(explanation)

    def test_reactions_conserve_charge_and_mass(self):
        for left, right in self.p.REACTIONS:
            self.assertGreater(sum(a for a, _, _ in left), sum(a for a, _, _ in right))
            self.assertGreaterEqual(sum(z for _, z, _ in left), sum(z for _, z, _ in right))

    def test_instrument_reading_is_a_whole_number_of_divisions(self):
        for _ in range(200):
            made = self.p.i_reading(self.rng)
            match = re.search(r"\(([\d,]+) ± ([\d,]+)\)", made["explanation"])
            value, division = number_of(match.group(1)), number_of(match.group(2))
            self.assertEqual(made["answer"], match.group(1) + match.group(2))
            self.assertEqual((value / division).denominator, 1, made["explanation"])
            self.assertEqual(len(match.group(1).partition(",")[2]), len(match.group(2).partition(",")[2]))

    def test_experiment_has_exactly_one_suitable_pair(self):
        for _ in range(200):
            made = self.p.x_setups(self.rng)
            cells = [shape[3] for shape in made["figure"]["items"] if shape[0] == "text"]
            rows = [cells[i:i + 4] for i in range(0, len(cells), 4)]
            headers, setups = rows[0][1:], [row[1:] for row in rows[1:]]
            studied = next(i for i, header in enumerate(headers) if header.lower() in made["explanation"])
            good = [f"{i + 1}{j + 1}" for i in range(5) for j in range(i + 1, 5)
                    if [k for k in range(3) if setups[i][k] != setups[j][k]] == [studied]]
            self.assertEqual(good, [made["answer"]], made["text"])

    def test_statement_tasks_have_two_or_three_correct(self):
        for generator in (self.p.a_throw, self.p.a_graph, self.p.a_pendulum, self.p.h_melting_graph, self.p.h_isobaric, self.p.h_cycle,
                          self.p.c_series, self.p.c_lens, self.p.c_graph, self.p.general_statements):
            for _ in range(60):
                made = generator(self.rng)
                self.assertIn(len(made["answer"]), (2, 3), generator.__name__)
                self.assertEqual(made["text"].count("\n") - 1, 5, generator.__name__)


class InformaticsTest(unittest.TestCase):
    def setUp(self):
        import exam_informatics
        self.i = exam_informatics
        self.rng = random.Random(15)

    def test_game_classes_match_independent_search(self):
        def wins(stones, moves_left, add, factor, goal):
            """Ходящий может выиграть не позже чем своим ходом номер moves_left."""
            return any(m >= goal or (moves_left > 1 and loses(m, moves_left - 1, add, factor, goal)) for m in (stones + add, stones * factor))

        def loses(stones, moves_left, add, factor, goal):
            """Соперник ходящего выигрывает не позже чем своим ходом номер moves_left при любой игре ходящего."""
            return all(m < goal and wins(m, moves_left, add, factor, goal) for m in (stones + add, stones * factor))

        for add, factor, goal in [(1, 2, 29), (2, 3, 50), (3, 2, 41), (4, 3, 77), (1, 3, 33)]:
            win1, lose1, win2, lose2 = self.i.game_classes(add, factor, goal)
            positions = range(1, goal)
            self.assertEqual(lose1, {s for s in positions if loses(s, 1, add, factor, goal)})
            self.assertEqual(win2, {s for s in positions if wins(s, 2, add, factor, goal) and not wins(s, 1, add, factor, goal)})
            self.assertEqual(lose2, {s for s in positions if loses(s, 2, add, factor, goal) and not loses(s, 1, add, factor, goal)})

    def test_fano_answer_is_the_shortest_valid_code(self):
        for _ in range(200):
            made = self.i.c_fano(self.rng)
            known = re.findall(r": ([01]+)", made["text"])
            answer = made["answer"]
            self.assertFalse(any(answer.startswith(code) or code.startswith(answer) for code in known), made["text"])
            for length in range(1, len(answer) + 1):
                for number in range(2 ** length):
                    code = format(number, f"0{length}b")
                    if (len(code), code) < (len(answer), answer):
                        self.assertTrue(any(code.startswith(k) or k.startswith(code) for k in known), (made["text"], code))

    def test_programs_count_matches_plain_recursion(self):
        def count(number, goal, forward, required, banned, seen):
            if number == banned or number > goal:
                return 0
            seen = seen or number == required
            if number == goal:
                return 1 if (required is None or seen) else 0
            return sum(count(move(number), goal, forward, required, banned, seen) for move in forward)

        forward = [lambda n: n + 1, lambda n: n * 2]
        _, backward = self.i.COMMANDS[0]
        for start, goal, required, banned in [(1, 20, None, None), (2, 30, 12, None), (1, 25, None, 9), (3, 34, 10, 17), (1, 22, 8, 5)]:
            self.assertEqual(self.i.count_programs(start, goal, backward, required, banned), count(start, goal, forward, required, banned, False))

    def test_truth_table_answer_reproduces_the_rows(self):
        for _ in range(100):
            made = self.i.l_truth_table(self.rng)
            self.assertEqual(sorted(made["answer"]), list("wxyz"))

    def test_inequality_answers_by_brute_force(self):
        for _ in range(40):
            made = self.i.b_inequality(self.rng)
            answer = int(made["answer"])
            match = re.search(r"\(x \+ (\d+)y < A\) ∨ \(y > x\) ∨ \(x > (\d+)\)", made["text"])
            if match:
                factor, bound = int(match.group(1)), int(match.group(2))

                def holds(a):
                    return all(x + factor * y < a or y > x or x > bound for x in range(bound + 3) for y in range(bound + 3))
            else:
                first, second = (int(n) for n in re.search(r"\(x > (\d+)\) ∨ \(y > (\d+)\)", made["text"]).groups())

                def holds(a):
                    return all(x * y < a or x > first or y > second for x in range(first + 3) for y in range(second + 3))
            self.assertTrue(holds(answer), made["text"])
            self.assertFalse(holds(answer - 1), made["text"])


if __name__ == "__main__":
    unittest.main()
