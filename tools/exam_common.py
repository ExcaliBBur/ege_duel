"""Общие заготовки для предметов, разбитых по номерам заданий ЕГЭ."""

import math
from collections import namedtuple
from fractions import Fraction

from figures import Fig
from generators import dec, task

# Один номер экзамена: номер, тема как на «Решу ЕГЭ», первичный балл, генераторы подтипов.
Entry = namedtuple("Entry", "number title points generators")


def round_half_up(value, digits):
    """Округление «как в школе»: 0,125 до сотых даёт 0,13."""
    scale = 10 ** digits
    scaled = Fraction(value) * scale
    whole = math.floor(scaled + Fraction(1, 2))
    return Fraction(whole, scale)


def is_finite_decimal(value) -> bool:
    den = Fraction(value).denominator
    for prime in (2, 5):
        while den % prime == 0:
            den //= prime
    return den == 1


def frac(value) -> str:
    """Число для условия: целое, конечная десятичная дробь или обыкновенная дробь a/b."""
    value = Fraction(value)
    if is_finite_decimal(value):
        return dec(value)
    return f"{value.numerator}/{value.denominator}"


def quotient(value) -> str:
    """Результат деления для пояснения: '= 4,2' или, если дробь бесконечная, '≈ 12,13'."""
    value = Fraction(value)
    rounded = round_half_up(value, 2)
    return f"= {dec(value)}" if rounded == value else f"≈ {dec(rounded)}"


def plural(number, one, few, many) -> str:
    """Число с существительным в нужной форме: plural(22, 'рубль', 'рубля', 'рублей') -> '22 рубля'."""
    tail = abs(number) % 100
    if 11 <= tail <= 14:
        word = many
    elif tail % 10 == 1:
        word = one
    elif 2 <= tail % 10 <= 4:
        word = few
    else:
        word = many
    return f"{number} {word}"


def signed(value) -> str:
    """Слагаемое со знаком: signed(3) -> '+ 3', signed(-2) -> '- 2'."""
    return f"+ {dec(value)}" if value >= 0 else f"- {dec(-value)}"


class Plane:
    """Координатная плоскость на рисунке: сетка, оси, графики, отмеченные точки."""

    def __init__(self, x_min=-10, x_max=10, y_min=-6, y_max=6, cell=20, labels=True):
        self.x_min, self.x_max, self.y_min, self.y_max, self.cell = x_min, x_max, y_min, y_max, cell
        width = (x_max - x_min) * cell + 20
        height = (y_max - y_min) * cell + 20
        self.fig = Fig(width, height)
        for x in range(x_min, x_max + 1):
            self.fig.line(*self.px(x, y_min), *self.px(x, y_max), 0)
        for y in range(y_min, y_max + 1):
            self.fig.line(*self.px(x_min, y), *self.px(x_max, y), 0)
        if x_min <= 0 <= x_max:
            self.fig.line(*self.px(0, y_min), *self.px(0, y_max), 1)
            self.fig.text(self.px(0, y_max)[0] + 9, self.px(0, y_max)[1] + 4, "y")
        if y_min <= 0 <= y_max:
            self.fig.line(*self.px(x_min, 0), *self.px(x_max, 0), 1)
            self.fig.text(self.px(x_max, 0)[0] - 4, self.px(x_max, 0)[1] + 10, "x")
        if labels and x_min <= 0 <= x_max and y_min <= 0 <= y_max:
            self.fig.text(self.px(0, 0)[0] - 7, self.px(0, 0)[1] + 9, "0")
            self.fig.text(self.px(1, 0)[0], self.px(1, 0)[1] + 9, "1")
            self.fig.text(self.px(0, 1)[0] - 7, self.px(0, 1)[1], "1")

    def px(self, x, y):
        return 10 + (x - self.x_min) * self.cell, 10 + (self.y_max - y) * self.cell

    def inside(self, x, y) -> bool:
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

    def curve(self, function, x_from=None, x_to=None, steps=60, style=2):
        """График функции ломаной. Куски за пределами рисунка и точки разрыва пропускаются."""
        x_from = self.x_min if x_from is None else max(x_from, self.x_min)
        x_to = self.x_max if x_to is None else min(x_to, self.x_max)
        previous = None
        for index in range(steps + 1):
            x = x_from + (x_to - x_from) * index / steps
            try:
                y = function(x)
            except (ValueError, ZeroDivisionError, OverflowError):
                previous = None
                continue
            point = (x, y) if self.y_min - 0.01 <= y <= self.y_max + 0.01 else None
            if previous and point and abs(point[1] - previous[1]) < (self.y_max - self.y_min):
                self.fig.line(*self.px(*previous), *self.px(*point), style)
            previous = point

    def segment(self, x1, y1, x2, y2, style=2):
        self.fig.line(*self.px(x1, y1), *self.px(x2, y2), style)

    def line(self, k, b, style=2):
        """Прямая y = kx + b, обрезанная по границам рисунка."""
        points = []
        for x in (self.x_min, self.x_max):
            y = k * x + b
            if self.y_min <= y <= self.y_max:
                points.append((x, y))
        if k != 0:
            for y in (self.y_min, self.y_max):
                x = (y - b) / k
                if self.x_min < x < self.x_max:
                    points.append((x, y))
        points.sort()
        if len(points) >= 2:
            self.segment(*points[0], *points[-1], style)

    def mark(self, x, y, label=None):
        self.fig.circle(*self.px(x, y), 3.5, 2)
        if label:
            self.fig.text(self.px(x, y)[0] + 10, self.px(x, y)[1] - 10, label)

    def tick(self, x, label):
        """Подпись на оси абсцисс."""
        self.fig.line(self.px(x, 0)[0], self.px(x, 0)[1] - 3, self.px(x, 0)[0], self.px(x, 0)[1] + 3, 1)
        self.fig.text(self.px(x, 0)[0], self.px(x, 0)[1] + 11, label)


def table_figure(rows, cell_width=62, cell_height=34, first_width=120):
    """Рисунок-таблица. rows: список строк, первая ячейка каждой строки это заголовок строки."""
    columns = max(len(row) for row in rows) - 1
    width = first_width + columns * cell_width + 20
    height = len(rows) * cell_height + 20
    fig = Fig(max(width, 200), height)
    for row_index in range(len(rows) + 1):
        y = 10 + row_index * cell_height
        fig.line(10, y, 10 + first_width + columns * cell_width, y, 1 if row_index in (0, len(rows)) else 0)
    xs = [10, 10 + first_width] + [10 + first_width + (i + 1) * cell_width for i in range(columns)]
    for index, x in enumerate(xs):
        fig.line(x, 10, x, 10 + len(rows) * cell_height, 1 if index in (0, 1, len(xs) - 1) else 0)
    for row_index, row in enumerate(rows):
        y = 10 + row_index * cell_height + cell_height / 2
        fig.text(10 + first_width / 2, y, row[0])
        for column, value in enumerate(row[1:]):
            fig.text(10 + first_width + column * cell_width + cell_width / 2, y, value)
    return fig


# ---------------------------------------------------------------- виды заданий, общие для предметов


def essay(text, solution, criteria):
    """Задание второй части с развёрнутым ответом: его оценивает соперник по эталону и критериям."""
    return {"text": text, "answer": "-", "explanation": solution, "criteria": list(criteria), "kind": "essay"}


def levels(*lines):
    """Критерии по убыванию балла: levels("всё верно", "одна ошибка") -> «2 балла: …», «1 балл: …», «0 баллов: …»."""
    top = len(lines)
    made = []
    for offset, line in enumerate(lines):
        score = top - offset
        word = "балл" if score == 1 else "балла" if score < 5 else "баллов"
        made.append(f"{score} {word}: {line}")
    return made + ["0 баллов: ответ неверный или не по существу задания."]


def essays(name, items):
    """Генератор по готовому списку заданий: каждое задание попадает в банк один раз."""
    def generator(r):
        index = r.randrange(len(items))
        made = dict(items[index])
        made["key"] = f"{name}:{index}"
        return made
    generator.__name__ = name
    return generator


def matching(text, left, right, answer, explanation):
    """Задание на соответствие: левый столбец с буквами, правый с цифрами, ответ это цифры по порядку букв."""
    letters = "АБВГД"
    lines = [f"{letters[i]}) {item}" for i, item in enumerate(left)] + [""] + [f"{i + 1}) {item}" for i, item in enumerate(right)]
    made = task(
        text + " Запишите цифры в порядке букв " + "".join(letters[: len(left)]) + ", без пробелов.\n\n" + "\n".join(lines),
        answer,
        explanation,
    )
    made["kind"] = "order"
    return made


def choose(text, statements, correct, explanation):
    """Выбор всех верных утверждений; ответ это их номера по возрастанию."""
    lines = [f"{i + 1}) {statement}" for i, statement in enumerate(statements)]
    made = task(
        text + " В ответе запишите номера выбранных утверждений без пробелов и запятых.\n\n" + "\n".join(lines),
        "".join(str(i + 1) for i in range(len(statements)) if correct[i]),
        explanation,
    )
    made["kind"] = "set"
    return made


def pick_statements(r, pool, count=5, true_counts=(2, 3)):
    """Выбирает count утверждений из набора так, чтобы верных было 2 или 3.

    Элемент набора: пара (текст, верно ли) или список таких пар, из которого берётся одна
    (так верная и неверная версии одного факта не попадают в задание вместе).
    """
    for _ in range(400):
        items = [r.choice(item) if isinstance(item, list) else item for item in pool]
        picked = r.sample(items, count)
        if sum(1 for _, flag in picked if flag) in true_counts:
            return [text for text, _ in picked], [flag for _, flag in picked]
    raise ValueError("в наборе не хватает верных или неверных утверждений")


def changes(r, scenario, lead, quantities, explanation):
    """Задание на изменение величин: для двух величин выбрать «увеличится», «уменьшится» или «не изменится».

    quantities: словарь «величина -> цифра ответа» (1, 2 или 3); в задание попадают две случайные.
    """
    first, second = r.sample(sorted(quantities), 2)
    made = task(
        f"{scenario} {lead} величины «{first}» и «{second}»?\n\n"
        "Для каждой величины определите характер изменения:\n1) увеличивается\n2) уменьшается\n3) не изменяется\n\n"
        "Запишите в ответ две цифры в том же порядке, в каком названы величины. Цифры могут повторяться.",
        f"{quantities[first]}{quantities[second]}",
        explanation,
    )
    made["kind"] = "order"
    return made


def formulas(r, scenario, pairs, extra=()):
    """Соответствие «физическая величина -> формула»: две величины и четыре формулы."""
    asked = r.sample(pairs, 2)
    others = [formula for _, formula in pairs if formula not in [f for _, f in asked]] + list(extra)
    options = [formula for _, formula in asked] + r.sample(others, 2)
    r.shuffle(options)
    return matching(
        f"{scenario} Установите соответствие между физическими величинами и формулами, по которым их можно рассчитать.",
        [name for name, _ in asked],
        options,
        "".join(str(options.index(formula) + 1) for _, formula in asked),
        "; ".join(f"{name}: {formula}" for name, formula in asked) + ".",
    )
