"""Задания с рисунками.

Рисунок описывается простыми фигурами (линии, прямоугольники, круги, подписи), игра рисует его сама.
Файлы-картинки не нужны, поэтому не нужна и модерация изображений в Roblox.
При импорте модуль добавляет свои генераторы в списки предметов из generators.py.
"""

import math
from fractions import Fraction

import facts  # noqa: F401  (сначала таблицы фактов: они создают списки гуманитарных предметов)
import generators
from generators import dec, sub, task


class Fig:
    """Рисунок к заданию. Координаты в пикселях, начало в левом верхнем углу.

    Стили линий и прямоугольников: 0 сетка, 1 основная линия, 2 выделение.
    Стили кругов: 0 тонкая окружность без заливки, 1 белый круг с обводкой, 2 закрашенная точка.
    """

    def __init__(self, width=420, height=260):
        self.width, self.height, self.items = width, height, []

    @staticmethod
    def _n(value):
        return round(float(value), 1)

    def line(self, x1, y1, x2, y2, style=1):
        self.items.append(["line", self._n(x1), self._n(y1), self._n(x2), self._n(y2), style])

    def rect(self, x, y, width, height, style=2):
        self.items.append(["rect", self._n(x), self._n(y), self._n(width), self._n(height), style])

    def circle(self, x, y, radius, style=1):
        self.items.append(["circle", self._n(x), self._n(y), self._n(radius), style])

    def text(self, x, y, string, align="c"):
        self.items.append(["text", self._n(x), self._n(y), str(string), align])

    def data(self):
        return {"w": self.width, "h": self.height, "items": self.items}


def fig_bar_chart(r):
    values = [r.randrange(10, 100, 10) for _ in range(10)]
    fig = Fig()
    left, bottom, top = 44, 232, 12
    scale = (bottom - top) / 100
    for level in range(0, 101, 10):
        y = bottom - level * scale
        fig.line(left, y, 414, y, 0)
        if level % 20 == 0:
            fig.text(left - 6, y, level, "r")
    fig.line(left, top, left, bottom, 1)
    fig.line(left, bottom, 414, bottom, 1)
    for day, value in enumerate(values, start=1):
        x = left + 12 + (day - 1) * 37
        fig.rect(x, bottom - value * scale, 22, value * scale, 2)
        fig.text(x + 11, bottom + 13, day)

    if r.random() < 0.5:
        threshold = r.choice([30, 40, 50, 60])
        count = sum(1 for value in values if value > threshold)
        question = f"Сколько дней число посетителей было больше {threshold} тысяч?"
        answer = count
        how = f"Столбики выше отметки {threshold} стоят в {count} днях."
    else:
        answer = max(values) - min(values)
        question = "На сколько тысяч наибольшее число посетителей за день больше наименьшего?"
        how = f"Наибольшее значение {max(values)}, наименьшее {min(values)}, разность {answer}."
    return task(
        "На диаграмме показано число посетителей сайта (в тысячах) за 10 дней. По горизонтали указаны дни, "
        f"по вертикали число посетителей. {question}",
        dec(answer),
        how,
        fig,
    )


def fig_linear_graph(r):
    k = r.choice([-3, -2, -1, 1, 2, 3])
    b = r.randint(-3, 3)
    fig = Fig()
    cx, cy, cell = 210, 130, 22

    def px(x, y):
        return cx + x * cell, cy - y * cell

    for n in range(-5, 6):
        fig.line(*px(n, -5.5), *px(n, 5.5), 0)
        fig.line(*px(-5.5, n), *px(5.5, n), 0)
    fig.line(*px(-5.7, 0), *px(5.7, 0), 1)
    fig.line(*px(0, -5.7), *px(0, 5.7), 1)
    fig.text(*px(5.4, -0.6), "x")
    fig.text(*px(0.5, 5.3), "y")
    fig.text(*px(-0.4, -0.5), "0")
    fig.text(*px(1, -0.5), "1")
    fig.text(*px(-0.4, 1), "1")

    x_low, x_high = sorted([(-5.5 - b) / k, (5.5 - b) / k])
    x_low, x_high = max(x_low, -5.5), min(x_high, 5.5)
    fig.line(*px(x_low, k * x_low + b), *px(x_high, k * x_high + b), 2)
    marked = [x for x in range(-5, 6) if abs(k * x + b) <= 5][:2]
    for x in marked:
        fig.circle(*px(x, k * x + b), 4, 2)

    kind = r.choice(["k", "b", "value"])
    if kind == "k":
        question, answer = "Найдите k.", k
        how = f"При увеличении x на 1 значение y меняется на {k}, значит k = {k}."
    elif kind == "b":
        question, answer = "Найдите b.", b
        how = f"График пересекает ось y в точке (0; {b}), значит b = {b}."
    else:
        x0 = r.choice([8, 10, 12, -10])
        question, answer = f"Найдите значение функции при x = {x0}.", k * x0 + b
        how = f"По графику k = {k}, b = {b}; y = {k} · ({x0}) + ({b}) = {answer}."
    return task(
        f"На рисунке изображён график функции y = kx + b. {question}",
        dec(answer),
        how,
        fig,
    )


def triangle_area(points):
    (x1, y1), (x2, y2), (x3, y3) = points
    return Fraction(abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)), 2)


def fig_grid_triangle(r):
    while True:
        points = [(r.randint(0, 12), r.randint(0, 7)) for _ in range(3)]
        area = triangle_area(points)
        if area >= 4:
            break
    fig = Fig()
    left, bottom, cell = 30, 235, 30

    def px(x, y):
        return left + x * cell, bottom - y * cell

    for n in range(0, 13):
        fig.line(*px(n, 0), *px(n, 7), 0)
    for n in range(0, 8):
        fig.line(*px(0, n), *px(12, n), 0)
    for index in range(3):
        fig.line(*px(*points[index]), *px(*points[(index + 1) % 3]), 2)
    return task(
        "На клетчатой бумаге с размером клетки 1 × 1 изображён треугольник. Найдите его площадь.",
        dec(area),
        "Площадь можно найти как площадь описанного прямоугольника минус площади лишних прямоугольных треугольников. "
        f"Получается {dec(area)}.",
        fig,
    )


def path_under_graph(times, speeds, last):
    """Площадь под ломаной скорости от начала до узла с номером last."""
    return sum(Fraction(speeds[i] + speeds[i + 1], 2) * (times[i + 1] - times[i]) for i in range(last))


def fig_velocity_graph(r):
    t1 = r.choice([2, 4])
    t2 = r.choice([t for t in (4, 6) if t > t1])
    times = [0, t1, t2, 8]
    while True:
        speeds = [r.randrange(0, 11, 2) for _ in range(4)]
        if len(set(speeds)) >= 3:
            break
    fig = Fig()
    left, bottom, cell_t, cell_v = 50, 225, 42, 20

    def px(t, v):
        return left + t * cell_t, bottom - v * cell_v

    for t in range(0, 9):
        fig.line(*px(t, 0), *px(t, 10), 0)
        if t % 2 == 0:
            fig.text(px(t, 0)[0], bottom + 13, t)
    for v in range(0, 11):
        fig.line(*px(0, v), *px(8, v), 0)
        if v % 2 == 0 and v > 0:
            fig.text(left - 8, px(0, v)[1], v, "r")
    fig.line(*px(0, 0), *px(8.3, 0), 1)
    fig.line(*px(0, 0), *px(0, 10.5), 1)
    fig.text(left + 30, 12, "v, м/с")
    fig.text(px(8, 0)[0] + 16, bottom + 13, "t, с", "l")
    for index in range(3):
        fig.line(*px(times[index], speeds[index]), *px(times[index + 1], speeds[index + 1]), 2)

    if r.random() < 0.5:
        last = r.choice([1, 2, 3])
        path = path_under_graph(times, speeds, last)
        return task(
            "На рисунке показан график зависимости скорости тела от времени. "
            f"Какой путь прошло тело за первые {times[last]} с? Ответ дайте в метрах.",
            dec(path),
            f"Путь равен площади под графиком скорости от 0 до {times[last]} с: {dec(path)} м.",
            fig,
        )
    index = r.choice([i for i in range(3) if speeds[i] != speeds[i + 1]])
    change = abs(speeds[index + 1] - speeds[index])
    interval = times[index + 1] - times[index]
    acceleration = Fraction(change, interval)
    return task(
        "На рисунке показан график зависимости скорости тела от времени. "
        f"Найдите модуль ускорения тела в интервале от {times[index]} до {times[index + 1]} с. Ответ дайте в м/с².",
        dec(acceleration),
        f"a = Δv : Δt = {change} : {interval} = {dec(acceleration)} м/с².",
        fig,
    )


ROAD_NODES = {"А": (40, 130), "Б": (150, 45), "В": (150, 215), "Г": (280, 45), "Д": (280, 215), "Е": (385, 130)}
ROAD_BASE = [("А", "Б"), ("А", "В"), ("Б", "Г"), ("В", "Д"), ("Г", "Е"), ("Д", "Е")]
ROAD_EXTRA = [("Б", "В"), ("Г", "Д")]
ROAD_DIAGONALS = [("Б", "Д"), ("В", "Г")]


def shortest_path(weights, start, goal):
    """Длина кратчайшего пути по неориентированным дорогам weights = {(a, b): длина}."""
    names = {name for edge in weights for name in edge}
    distance = {name: float("inf") for name in names}
    distance[start] = 0
    for _ in names:
        for (a, b), weight in weights.items():
            distance[b] = min(distance[b], distance[a] + weight)
            distance[a] = min(distance[a], distance[b] + weight)
    return distance[goal]


def fig_roads(r):
    edges = list(ROAD_BASE)
    edges += [edge for edge in ROAD_EXTRA if r.random() < 0.6]
    edges.append(r.choice(ROAD_DIAGONALS))
    weights = {edge: r.randint(1, 9) for edge in edges}
    best = int(shortest_path(weights, "А", "Е"))

    fig = Fig()
    for (a, b), weight in weights.items():
        (x1, y1), (x2, y2) = ROAD_NODES[a], ROAD_NODES[b]
        fig.line(x1, y1, x2, y2, 1)
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        # Подпись длины стоит на трети дороги и сдвинута вбок, чтобы не накладываться на линию.
        mx, my = x1 + (x2 - x1) * 0.35, y1 + (y2 - y1) * 0.35
        fig.text(mx - (y2 - y1) / length * 13, my + (x2 - x1) / length * 13, weight)
    for name, (x, y) in ROAD_NODES.items():
        fig.circle(x, y, 15, 1)
        fig.text(x, y, name)
    return task(
        "На рисунке показана схема дорог между пунктами А, Б, В, Г, Д, Е. Числа обозначают длины дорог в километрах. "
        "Найдите длину кратчайшего пути из пункта А в пункт Е.",
        dec(best),
        f"Перебираем маршруты из А в Е и выбираем самый короткий: {best} км.",
        fig,
    )


# ---------------------------------------------------------------- общие заготовки рисунков


def arrow(fig, x1, y1, x2, y2, style=1, head=9):
    """Отрезок со стрелкой на конце (x2, y2)."""
    fig.line(x1, y1, x2, y2, style)
    angle = math.atan2(y2 - y1, x2 - x1)
    for turn in (2.6, -2.6):
        fig.line(x2, y2, x2 + head * math.cos(angle + turn), y2 + head * math.sin(angle + turn), style)


def outline(fig, x, y, width, height, style=1):
    """Незакрашенный прямоугольник."""
    fig.line(x, y, x + width, y, style)
    fig.line(x + width, y, x + width, y + height, style)
    fig.line(x + width, y + height, x, y + height, style)
    fig.line(x, y + height, x, y, style)


def axes(fig, left, bottom, cell_x, cell_y, max_x, max_y, x_name, y_name, x_step=1, y_step=1, x_scale=1, y_scale=1):
    """Сетка и оси первой четверти. Возвращает функцию перевода координат в пиксели."""

    def px(x, y):
        return left + x * cell_x, bottom - y * cell_y

    for x in range(0, max_x + 1):
        fig.line(*px(x, 0), *px(x, max_y), 0)
        if x % x_step == 0 and x > 0:
            fig.text(px(x, 0)[0], bottom + 13, dec(x * x_scale))
    for y in range(0, max_y + 1):
        fig.line(*px(0, y), *px(max_x, y), 0)
        if y % y_step == 0 and y > 0:
            fig.text(left - 8, px(0, y)[1], dec(y * y_scale), "r")
    fig.line(*px(0, 0), *px(max_x + 0.4, 0), 1)
    fig.line(*px(0, 0), *px(0, max_y + 0.4), 1)
    fig.text(left - 8, bottom + 13, "0", "r")
    fig.text(left + 8, px(0, max_y)[1] - 10, y_name, "l")
    fig.text(min(414, px(max_x, 0)[0] + 26), bottom - 13, x_name, "r")
    return px


# ---------------------------------------------------------------- математика


def fig_line_chart(r):
    days = 10
    temps = [r.randrange(8, 31, 2) for _ in range(days)]
    fig = Fig()
    # Одна клетка по вертикали соответствует 2 °C.
    px = axes(fig, 46, 228, 34, 13, days, 16, "день", "°C", 1, 2, 1, 2)
    for day in range(1, days):
        fig.line(*px(day, temps[day - 1] / 2), *px(day + 1, temps[day] / 2), 2)
    for day in range(1, days + 1):
        fig.circle(*px(day, temps[day - 1] / 2), 3.5, 2)

    kind = r.choice(["max", "min", "range", "count"])
    if kind == "max":
        question, answer = "Определите наибольшую температуру за этот период.", max(temps)
        how = f"Самая высокая точка графика соответствует {max(temps)} °C."
    elif kind == "min":
        question, answer = "Определите наименьшую температуру за этот период.", min(temps)
        how = f"Самая низкая точка графика соответствует {min(temps)} °C."
    elif kind == "range":
        question, answer = "Найдите разность между наибольшей и наименьшей температурой.", max(temps) - min(temps)
        how = f"{max(temps)} - {min(temps)} = {max(temps) - min(temps)} °C."
    else:
        level = r.choice([14, 18, 22])
        answer = sum(1 for value in temps if value > level)
        question = f"Сколько дней температура была выше {level} °C?"
        how = f"Точки выше отметки {level} стоят в {answer} днях."
    return task(
        "На рисунке точками показана температура воздуха в полдень в течение 10 дней. По горизонтали указаны дни, "
        f"по вертикали температура в градусах Цельсия. {question}",
        dec(answer),
        how,
        fig,
    )


def fig_grid_trapezoid(r):
    while True:
        height = r.randint(2, 6)
        low_left, low_right = sorted(r.sample(range(0, 13), 2))
        top_left, top_right = sorted(r.sample(range(0, 13), 2))
        low, top = low_right - low_left, top_right - top_left
        if low >= 2 and top >= 1 and low != top and (low + top) * height % 2 == 0:
            break
    fig = Fig()
    left, bottom, cell = 30, 235, 30

    def px(x, y):
        return left + x * cell, bottom - y * cell

    for n in range(0, 13):
        fig.line(*px(n, 0), *px(n, 7), 0)
    for n in range(0, 8):
        fig.line(*px(0, n), *px(12, n), 0)
    base = r.randint(0, 7 - height)
    points = [(low_left, base), (low_right, base), (top_right, base + height), (top_left, base + height)]
    for index in range(4):
        fig.line(*px(*points[index]), *px(*points[(index + 1) % 4]), 2)
    area = (low + top) * height // 2
    return task(
        "На клетчатой бумаге с размером клетки 1 × 1 изображена трапеция. Найдите её площадь.",
        dec(area),
        f"Основания равны {low} и {top}, высота {height}. Площадь равна ({low} + {top}) : 2 · {height} = {area}.",
        fig,
    )


def fig_right_triangle(r):
    a, b, c = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (6, 8, 10), (12, 16, 20)])
    k = r.choice([1, 2, 3])
    a, b, c = a * k, b * k, c * k
    fig = Fig()
    # Катеты нарисованы условно: длины подписаны, масштаб не соблюдается.
    fig.line(70, 220, 340, 220, 2)
    fig.line(70, 220, 70, 50, 2)
    fig.line(70, 50, 340, 220, 2)
    outline(fig, 70, 204, 16, 16, 1)
    kind = r.choice(["hypotenuse", "area", "leg"])
    if kind == "leg":
        fig.text(205, 238, "?")
        fig.text(46, 135, a)
        fig.text(225, 118, c)
        question, answer = "Найдите катет, отмеченный знаком вопроса.", b
        how = f"По теореме Пифагора: {c}² - {a}² = {c * c - a * a}, катет равен {b}."
    else:
        fig.text(205, 238, b)
        fig.text(46, 135, a)
        if kind == "hypotenuse":
            fig.text(225, 118, "?")
            question, answer = "Найдите гипотенузу, отмеченную знаком вопроса.", c
            how = f"По теореме Пифагора: {a}² + {b}² = {c * c}, гипотенуза равна {c}."
        else:
            question, answer = "Найдите площадь треугольника.", Fraction(a * b, 2)
            how = f"Площадь равна половине произведения катетов: {a} · {b} : 2 = {dec(Fraction(a * b, 2))}."
    return task(
        f"На рисунке изображён прямоугольный треугольник, длины сторон подписаны. {question}",
        dec(answer),
        how,
        fig,
    )


def fig_parabola(r):
    a = r.choice([1, -1])
    m = r.randint(-3, 3)
    n = r.randint(-4, 1) if a == 1 else r.randint(-1, 4)
    fig = Fig()
    cx, cy, cell = 210, 130, 22

    def px(x, y):
        return cx + x * cell, cy - y * cell

    for value in range(-5, 6):
        fig.line(*px(value, -5.5), *px(value, 5.5), 0)
        fig.line(*px(-5.5, value), *px(5.5, value), 0)
    fig.line(*px(-5.7, 0), *px(5.7, 0), 1)
    fig.line(*px(0, -5.7), *px(0, 5.7), 1)
    fig.text(*px(5.4, -0.6), "x")
    fig.text(*px(0.5, 5.3), "y")
    fig.text(*px(-0.4, -0.5), "0")
    fig.text(*px(1, -0.5), "1")
    fig.text(*px(-0.4, 1), "1")

    def f(x):
        return a * (x - m) ** 2 + n

    steps = [m - 3.2 + index * 0.2 for index in range(33)]
    visible = [x for x in steps if -5.5 <= x <= 5.5 and -5.5 <= f(x) <= 5.5]
    for first, second in zip(visible, visible[1:]):
        if abs(second - first) < 0.25:
            fig.line(*px(first, f(first)), *px(second, f(second)), 2)
    fig.circle(*px(m, n), 4, 2)

    kind = r.choice(["x0", "y0", "c"])
    c = a * m * m + n
    formula = "y = x² + bx + c" if a == 1 else "y = -x² + bx + c"
    if kind == "x0":
        question, answer = "Найдите абсциссу вершины параболы.", m
        how = f"Вершина параболы находится в точке ({m}; {n})."
    elif kind == "y0":
        word = "наименьшее" if a == 1 else "наибольшее"
        question, answer = f"Найдите {word} значение функции.", n
        how = f"Вершина параболы находится в точке ({m}; {n}), значение функции в ней равно {n}."
    else:
        question, answer = "Найдите c.", c
        how = f"Вершина в точке ({m}; {n}), поэтому y = {'' if a == 1 else '-'}(x - ({m}))² + ({n}); при x = 0 получаем c = {c}."
    return task(
        f"На рисунке изображён график функции {formula}. {question}",
        dec(answer),
        how,
        fig,
    )


def fig_vector(r):
    dx, dy = r.choice([(3, 4), (4, 3), (6, 8), (8, 6), (5, 12), (12, 5), (15, 8), (9, 12), (12, 9)])
    scale = 20 if max(dx, dy) > 9 else 28
    columns, rows = 400 // scale, 240 // scale
    dx, dy = dx * r.choice([1, -1]), dy * r.choice([1, -1])
    start_x = r.randint(max(0, -dx), min(columns, columns - dx))
    start_y = r.randint(max(0, -dy), min(rows, rows - dy))
    fig = Fig()

    def px(x, y):
        return 10 + x * scale, 250 - y * scale

    for value in range(0, columns + 1):
        fig.line(*px(value, 0), *px(value, rows), 0)
    for value in range(0, rows + 1):
        fig.line(*px(0, value), *px(columns, value), 0)
    arrow(fig, *px(start_x, start_y), *px(start_x + dx, start_y + dy), 2, 11)
    length = int(round((dx * dx + dy * dy) ** 0.5))
    return task(
        "На клетчатой бумаге с размером клетки 1 × 1 изображён вектор. Найдите его длину.",
        dec(length),
        f"Вектор смещается на {abs(dx)} клеток по горизонтали и на {abs(dy)} по вертикали. По теореме Пифагора длина равна {length}.",
        fig,
    )


# ---------------------------------------------------------------- физика


def fig_xt_graph(r):
    while True:
        t1 = r.choice([2, 4, 5])
        xs = [r.randrange(0, 21, 4) for _ in range(3)]
        index = r.choice([0, 1])
        times = [0, t1, 8]
        speed = Fraction(abs(xs[index + 1] - xs[index]), times[index + 1] - times[index])
        if xs[0] != xs[1] and xs[1] != xs[2] and speed.denominator in (1, 2, 4, 5):
            break
    fig = Fig()
    px = axes(fig, 50, 225, 42, 10, 8, 20, "t, с", "x, м", 1, 4)
    for step in range(2):
        fig.line(*px(times[step], xs[step]), *px(times[step + 1], xs[step + 1]), 2)
    return task(
        "На рисунке показан график зависимости координаты тела от времени. "
        f"Найдите модуль скорости тела в интервале от {times[index]} до {times[index + 1]} с. Ответ дайте в м/с.",
        dec(speed),
        f"v = Δx : Δt = {abs(xs[index + 1] - xs[index])} : {times[index + 1] - times[index]} = {dec(speed)} м/с.",
        fig,
    )


def resistor(fig, x, y, label):
    """Резистор шириной 70 с центром в точке (x, y) и подписью над ним."""
    outline(fig, x - 35, y - 12, 70, 24, 1)
    fig.text(x, y - 26, label)


def fig_circuit_series(r):
    count = r.choice([2, 3])
    values = [r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20]) for _ in range(count)]
    total = sum(values)
    fig = Fig()
    centers = [120, 300] if count == 2 else [90, 210, 330]
    edge_left, edge_right, top, bottom = 30, 390, 80, 210
    cursor = edge_left
    for index, center in enumerate(centers):
        fig.line(cursor, top, center - 35, top, 1)
        resistor(fig, center, top, f"R{sub(index + 1)} = {values[index]} Ом")
        cursor = center + 35
    fig.line(cursor, top, edge_right, top, 1)
    fig.line(edge_right, top, edge_right, bottom, 1)
    fig.line(edge_left, top, edge_left, bottom, 1)
    # Источник тока: длинная и короткая пластины.
    fig.line(edge_left, bottom, 200, bottom, 1)
    fig.line(220, bottom, edge_right, bottom, 1)
    fig.line(200, bottom - 16, 200, bottom + 16, 1)
    fig.line(220, bottom - 8, 220, bottom + 8, 2)

    if r.random() < 0.5:
        return task(
            "На рисунке показана электрическая цепь из последовательно соединённых резисторов. "
            "Найдите общее сопротивление участка с резисторами. Ответ дайте в омах.",
            dec(total),
            "При последовательном соединении сопротивления складываются: " + " + ".join(str(v) for v in values) + f" = {total} Ом.",
            fig,
        )
    current = Fraction(r.choice([1, 2, 3, 4, 5, 6]), 2)
    voltage = current * total
    fig.text(210, bottom + 30, f"U = {dec(voltage)} В")
    return task(
        "На рисунке показана электрическая цепь из последовательно соединённых резисторов, напряжение источника подписано. "
        "Найдите силу тока в цепи. Сопротивлением источника и проводов пренебрегите. Ответ дайте в амперах.",
        dec(current),
        f"Общее сопротивление {total} Ом, I = U : R = {dec(voltage)} : {total} = {dec(current)} А.",
        fig,
    )


PARALLEL_PAIRS = [
    (6, 3, 2), (4, 4, 2), (12, 6, 4), (10, 15, 6), (20, 5, 4), (12, 4, 3), (30, 6, 5), (8, 8, 4), (6, 6, 3),
    (20, 30, 12), (10, 10, 5), (15, 30, 10), (12, 12, 6), (40, 10, 8), (24, 8, 6), (18, 9, 6), (60, 30, 20),
    (24, 12, 8), (60, 20, 15), (30, 15, 10), (36, 12, 9), (40, 40, 20), (90, 10, 9), (45, 30, 18),
]


def fig_circuit_parallel(r):
    first, second, total = r.choice(PARALLEL_PAIRS)
    if r.random() < 0.5:
        first, second = second, first
    fig = Fig()
    node_left, node_right, upper, lower, middle = 110, 310, 70, 170, 120
    fig.line(40, middle, node_left, middle, 1)
    fig.line(node_right, middle, 380, middle, 1)
    fig.line(node_left, upper, node_left, lower, 1)
    fig.line(node_right, upper, node_right, lower, 1)
    for y, label in ((upper, f"R{sub(1)} = {first} Ом"), (lower, f"R{sub(2)} = {second} Ом")):
        fig.line(node_left, y, 175, y, 1)
        fig.line(245, y, node_right, y, 1)
        resistor(fig, 210, y, label)
    fig.circle(node_left, middle, 4, 2)
    fig.circle(node_right, middle, 4, 2)
    fig.circle(40, middle, 4, 1)
    fig.circle(380, middle, 4, 1)
    return task(
        "На рисунке показан участок цепи из двух параллельно соединённых резисторов. "
        "Найдите общее сопротивление участка. Ответ дайте в омах.",
        dec(total),
        f"R = R₁ · R₂ : (R₁ + R₂) = {first} · {second} : {first + second} = {total} Ом.",
        fig,
    )


def fig_forces(r):
    while True:
        mass = r.choice([1, 2, 4, 5, 8, 10])
        left_force, right_force = r.randint(2, 30), r.randint(2, 30)
        if left_force != right_force and (abs(left_force - right_force) * 10) % mass == 0:
            break
    fig = Fig()
    fig.line(30, 190, 390, 190, 1)
    outline(fig, 170, 130, 80, 60, 2)
    fig.text(210, 160, f"{mass} кг")
    arrow(fig, 170, 160, 60, 160, 1, 11)
    arrow(fig, 250, 160, 360, 160, 1, 11)
    fig.text(110, 140, f"F{sub(1)} = {left_force} Н")
    fig.text(310, 140, f"F{sub(2)} = {right_force} Н")
    net = abs(left_force - right_force)
    if r.random() < 0.5:
        return task(
            "На рисунке показаны горизонтальные силы, действующие на тело на гладкой поверхности. "
            "Найдите модуль равнодействующей этих сил. Ответ дайте в ньютонах.",
            dec(net),
            f"Силы направлены в противоположные стороны: {max(left_force, right_force)} - {min(left_force, right_force)} = {net} Н.",
            fig,
        )
    return task(
        "На рисунке показаны горизонтальные силы, действующие на тело на гладкой поверхности, масса тела подписана. "
        "Найдите модуль ускорения тела. Ответ дайте в м/с².",
        dec(Fraction(net, mass)),
        f"Равнодействующая равна {net} Н, a = F : m = {net} : {mass} = {dec(Fraction(net, mass))} м/с².",
        fig,
    )


def fig_pv_work(r):
    pressure = r.randint(1, 5)
    v1, v2 = sorted(r.sample(range(1, 9), 2))
    fig = Fig()
    px = axes(fig, 54, 225, 42, 36, 8, 5, "V, м³", "p, кПа", 1, 1, 1, 100)
    arrow(fig, *px(v1, pressure), *px(v2, pressure), 2, 11)
    fig.circle(*px(v1, pressure), 4, 2)
    fig.text(px(v1, pressure)[0], px(v1, pressure)[1] - 16, "1")
    fig.text(px(v2, pressure)[0], px(v2, pressure)[1] - 16, "2")
    work = pressure * 100 * (v2 - v1)
    return task(
        "На рисунке показан процесс расширения газа из состояния 1 в состояние 2 при постоянном давлении. "
        "Какую работу совершил газ? Ответ дайте в килоджоулях.",
        dec(work),
        f"A = p · ΔV = {pressure * 100} кПа · {v2 - v1} м³ = {work} кДж.",
        fig,
    )


def fig_iu_graph(r):
    # Клетка по горизонтали равна 2 В, по вертикали 0,5 А. Отмеченная точка стоит в узле сетки.
    a = r.randint(1, 8)
    b = r.choice([1, 2, 4, 5, 8, 10])
    voltage, current = 2 * a, Fraction(b, 2)
    resistance = Fraction(voltage) / current
    fig = Fig()
    px = axes(fig, 54, 225, 42, 18, 8, 10, "U, В", "I, А", 1, 2, 2, Fraction(1, 2))
    stretch = min(8 / a, 10 / b)
    fig.line(*px(0, 0), *px(a * stretch, b * stretch), 2)
    fig.circle(*px(a, b), 4, 2)
    return task(
        "На рисунке показан график зависимости силы тока в резисторе от напряжения на нём. "
        "Найдите сопротивление резистора. Ответ дайте в омах.",
        dec(resistance),
        f"В отмеченной точке U = {voltage} В, I = {dec(current)} А; R = U : I = {dec(resistance)} Ом.",
        fig,
    )


# ---------------------------------------------------------------- информатика

DAG_NODES = {"А": (40, 130), "Б": (150, 45), "В": (150, 130), "Г": (150, 215), "Д": (270, 75), "Е": (270, 185), "Ж": (385, 130)}
DAG_REQUIRED = [("А", "Б"), ("А", "В"), ("А", "Г"), ("Д", "Ж"), ("Е", "Ж")]
DAG_OPTIONAL = [("Б", "В"), ("Г", "В"), ("Б", "Д"), ("В", "Д"), ("В", "Е"), ("Г", "Е"), ("Д", "Е"), ("В", "Ж")]
DAG_ORDER = ["А", "Б", "Г", "В", "Д", "Е", "Ж"]


def count_paths(edges, order, start, goal):
    """Число путей в графе без циклов; order задаёт порядок, в котором вершины идут вдоль стрелок."""
    ways = {name: 0 for name in order}
    ways[start] = 1
    for name in order:
        for a, b in edges:
            if a == name:
                ways[b] += ways[name]
    return ways[goal]


def fig_paths(r):
    while True:
        edges = DAG_REQUIRED + [edge for edge in DAG_OPTIONAL if r.random() < 0.6]
        has_into = lambda name: any(b == name for _, b in edges)
        has_from = lambda name: any(a == name for a, _ in edges)
        if all(has_into(name) and has_from(name) for name in "БВГДЕ"):
            break
    fig = Fig()
    for a, b in edges:
        (x1, y1), (x2, y2) = DAG_NODES[a], DAG_NODES[b]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        arrow(fig, x1 + ux * 15, y1 + uy * 15, x2 - ux * 16, y2 - uy * 16, 1, 9)
    for name, (x, y) in DAG_NODES.items():
        fig.circle(x, y, 15, 1)
        fig.text(x, y, name)
    total = count_paths(edges, DAG_ORDER, "А", "Ж")
    return task(
        "На рисунке показана схема дорог между городами А, Б, В, Г, Д, Е, Ж. По каждой дороге можно ехать только "
        "в направлении стрелки. Сколько существует различных путей из города А в город Ж?",
        dec(total),
        f"Для каждого города считаем число путей как сумму путей в города, из которых в него ведут стрелки. В город Ж ведёт {total}.",
        fig,
    )


def fig_spreadsheet(r):
    cells = [[r.randint(1, 20) for _ in range(3)] for _ in range(3)]
    fig = Fig(420, 200)
    left, top, width, height = 40, 20, 90, 40
    for column in range(5):
        fig.line(left + column * width, top, left + column * width, top + 4 * height, 1 if column in (0, 4) else 0)
    for row in range(5):
        fig.line(left, top + row * height, left + 4 * width, top + row * height, 1 if row in (0, 4) else 0)
    for column, name in enumerate("ABC", start=1):
        fig.text(left + column * width + width / 2, top + height / 2, name)
    for row in range(1, 4):
        fig.text(left + width / 2, top + row * height + height / 2, row)
        for column in range(1, 4):
            fig.text(left + column * width + width / 2, top + row * height + height / 2, cells[row - 1][column - 1])

    def cell(name):
        return cells[int(name[1]) - 1]["ABC".index(name[0])]

    kind = r.choice(["sum", "mix", "average", "max"])
    if kind == "sum":
        formula, value = "=СУММ(A1:B2)", cell("A1") + cell("A2") + cell("B1") + cell("B2")
        how = f"Складываем ячейки A1, B1, A2, B2: {value}."
    elif kind == "mix":
        formula, value = "=A1*B2-C3", cell("A1") * cell("B2") - cell("C3")
        how = f"{cell('A1')} · {cell('B2')} - {cell('C3')} = {value}."
    elif kind == "average":
        formula, value = "=СРЗНАЧ(C1:C3)", Fraction(cell("C1") + cell("C2") + cell("C3"), 3)
        if value.denominator != 1:
            formula, value = "=СУММ(C1:C3)", cell("C1") + cell("C2") + cell("C3")
            how = f"Складываем ячейки C1, C2, C3: {value}."
        else:
            how = f"Сумма ячеек C1, C2, C3 равна {value * 3}, среднее равно {value}."
    else:
        formula, value = "=МАКС(A1:C1)+МИН(A3:C3)", max(cells[0]) + min(cells[2])
        how = f"Наибольшее в первой строке {max(cells[0])}, наименьшее в третьей {min(cells[2])}, сумма {value}."
    return task(
        f"На рисунке показан фрагмент электронной таблицы. Чему равно значение формулы {formula}?",
        dec(value),
        how,
        fig,
    )


# ---------------------------------------------------------------- химия

ELEMENTS = {
    3: "литий", 4: "бериллий", 5: "бор", 6: "углерод", 7: "азот", 8: "кислород", 9: "фтор", 10: "неон",
    11: "натрий", 12: "магний", 13: "алюминий", 14: "кремний", 15: "фосфор", 16: "сера", 17: "хлор",
    18: "аргон", 19: "калий", 20: "кальций",
}


def shells(number):
    """Распределение электронов по слоям для элементов с номерами до 20."""
    result = []
    for capacity in (2, 8, 8, 2):
        if number <= 0:
            break
        result.append(min(capacity, number))
        number -= result[-1]
    return result


def fig_atom(r):
    number = r.choice(list(ELEMENTS))
    layers = shells(number)
    fig = Fig()
    cx, cy = 210, 130
    for index in reversed(range(len(layers))):
        fig.circle(cx, cy, 36 + index * 27, 1)
    fig.circle(cx, cy, 16, 2)
    for index, count in enumerate(layers):
        radius = 36 + index * 27
        for electron in range(count):
            angle = 2 * math.pi * electron / count + index * 0.4
            fig.circle(cx + radius * math.cos(angle), cy + radius * math.sin(angle), 4, 2)
    kind = r.choice(["number", "outer", "period"])
    if kind == "number":
        question, answer = "Запишите порядковый номер этого элемента.", number
        how = f"Всего электронов {number}, столько же протонов в ядре. Это {ELEMENTS[number]}."
    elif kind == "outer":
        question, answer = "Сколько электронов находится на внешнем электронном слое?", layers[-1]
        how = f"Электроны по слоям: {', '.join(str(n) for n in layers)}. На внешнем слое {layers[-1]}."
    else:
        question, answer = "В каком периоде Периодической системы находится этот элемент? Запишите номер периода.", len(layers)
        how = f"Число электронных слоёв равно номеру периода: {len(layers)}."
    return task(
        "На рисунке показана схема строения атома: в центре ядро, вокруг электронные слои, точками обозначены электроны. "
        + question,
        dec(answer),
        how,
        fig,
    )


def fig_skeleton(r):
    carbons = r.randint(3, 8)
    double = r.randrange(carbons - 1) if r.random() < 0.5 else None
    branch = r.randrange(1, carbons - 1) if double is None and r.random() < 0.5 else None
    fig = Fig()
    step = min(48, 340 // (carbons - 1))
    start = 210 - step * (carbons - 1) / 2
    points = [(start + index * step, 150 if index % 2 == 0 else 110) for index in range(carbons)]
    for index in range(carbons - 1):
        (x1, y1), (x2, y2) = points[index], points[index + 1]
        fig.line(x1, y1, x2, y2, 1)
        if double == index:
            fig.line(x1, y1 + 7, x2, y2 + 7, 1)
    total = carbons
    if branch is not None:
        x, y = points[branch]
        up = -1 if y == 110 else 1
        fig.line(x, y, x, y + up * 46, 1)
        fig.circle(x, y + up * 46, 11, 1)
        fig.text(x, y + up * 46, "C")
        total += 1
    for x, y in points:
        fig.circle(x, y, 11, 1)
        fig.text(x, y, "C")
    hydrogens = 2 * total + 2 - (2 if double is not None else 0)
    if r.random() < 0.7:
        question, answer = "Сколько атомов водорода в молекуле этого вещества?", hydrogens
        if double is None:
            how = f"Атомов углерода {total}, двойных связей нет: это алкан, водорода 2 · {total} + 2 = {hydrogens}."
        else:
            how = f"Атомов углерода {total}, есть одна двойная связь: это алкен, водорода 2 · {total} = {hydrogens}."
    else:
        question, answer = "Сколько всего атомов (углерода и водорода) в молекуле этого вещества?", total + hydrogens
        how = f"Углерода {total}, водорода {hydrogens}, всего {total + hydrogens}."
    return task(
        "На рисунке показан углеродный скелет молекулы углеводорода. Двойная линия обозначает двойную связь. "
        "Все остальные валентности углерода заняты атомами водорода. " + question,
        dec(answer),
        how,
        fig,
    )


# ---------------------------------------------------------------- биология


def fig_punnett(r):
    letter = r.choice("ABCDE")
    big, small = letter, letter.lower()
    first, second = r.choice([
        ((big, small), (big, small)), ((big, small), (small, small)), ((big, big), (big, small)),
        ((big, big), (small, small)), ((small, small), (big, small)),
    ])
    fig = Fig(420, 210)
    left, top, width, height = 90, 25, 80, 55
    for column in range(4):
        fig.line(left + column * width, top, left + column * width, top + 3 * height, 1 if column in (0, 3) else 0)
    for row in range(4):
        fig.line(left, top + row * height, left + 3 * width, top + row * height, 1 if row in (0, 3) else 0)
    fig.text(left + width / 2, top + height / 2, "гаметы")
    genotypes = []
    for column, gamete in enumerate(second, start=1):
        fig.text(left + column * width + width / 2, top + height / 2, gamete)
    for row, gamete in enumerate(first, start=1):
        fig.text(left + width / 2, top + row * height + height / 2, gamete)
        for column, other in enumerate(second, start=1):
            genotype = "".join(sorted(gamete + other))  # заглавная буква в коде стоит раньше строчной
            genotypes.append(genotype)
            fig.text(left + column * width + width / 2, top + row * height + height / 2, genotype)

    kind = r.choice(["dominant", "recessive", "hetero", "homo"])
    dominant = sum(1 for g in genotypes if big in g)
    hetero = sum(1 for g in genotypes if g == big + small)
    if kind == "dominant":
        question, count = "проявится доминантный признак", dominant
    elif kind == "recessive":
        question, count = "проявится рецессивный признак", 4 - dominant
    elif kind == "hetero":
        question, count = "будут гетерозиготными", hetero
    else:
        question, count = "будут гомозиготными", 4 - hetero
    return task(
        f"На рисунке показана решётка Пеннета для скрещивания {''.join(first)} × {''.join(second)}, доминирование полное. "
        f"У скольких процентов потомков {question}?",
        dec(count * 25),
        f"Подходят {count} клетки из 4, это {count * 25}%.",
        fig,
    )


def fig_dna(r):
    length = r.randint(6, 10)
    strand = [r.choice("АТГЦ") for _ in range(length)]
    to_rna = r.random() < 0.4
    pairs = {"А": "У" if to_rna else "Т", "Т": "А", "Г": "Ц", "Ц": "Г"}
    answer = "".join(pairs[base] for base in strand)
    fig = Fig(420, 110)
    width = 36
    left = 210 - width * length / 2
    for index, base in enumerate(strand):
        outline(fig, left + index * width, 35, width, 40, 1)
        fig.text(left + index * width + width / 2, 55, base)
    what = "иРНК, которая синтезируется на этой цепи" if to_rna else "второй цепи ДНК"
    made = task(
        f"На рисунке показана последовательность нуклеотидов одной цепи ДНК. Запишите последовательность {what}. "
        "Буквы записывайте подряд, без пробелов.",
        answer,
        "По правилу комплементарности: А соединяется с " + ("У" if to_rna else "Т") + f", Т с А, Г с Ц, Ц с Г. Получается {answer}.",
        fig,
    )
    made["kind"] = "exact"
    return made


# ---------------------------------------------------------------- география

MONTHS = ["Я", "Ф", "М", "А", "М", "И", "И", "А", "С", "О", "Н", "Д"]


def fig_climate(r):
    winter, summer = r.randrange(-24, 1, 2), r.randrange(12, 27, 2)
    temps = []
    for month in range(12):
        share = (1 - math.cos(2 * math.pi * (month - 0.5) / 12)) / 2
        temps.append(int(round((winter + (summer - winter) * share) / 2)) * 2)
    rain = [r.randrange(10, 91, 10) for _ in range(12)]
    wettest = r.randrange(12)
    rain[wettest] = 100
    fig = Fig()
    left, zero, month_width, floor = 46, 116, 29, 236

    def temp_y(value):
        return zero - value * 3.4

    # Столбики осадков стоят на нижней линии, 100 мм соответствуют 90 пикселям.
    for month in range(12):
        x = left + month * month_width
        fig.rect(x + 7, floor - rain[month] * 0.9, 15, rain[month] * 0.9, 0)
        fig.text(x + month_width / 2, floor + 12, month + 1)
    for value in range(-24, 29, 4):
        fig.line(left, temp_y(value), left + 12 * month_width, temp_y(value), 0)
        if value % 8 == 0:
            fig.text(left - 6, temp_y(value), value, "r")
    fig.line(left, temp_y(0), left + 12 * month_width, temp_y(0), 1)
    fig.line(left, 14, left, floor, 1)
    fig.line(left, floor, left + 12 * month_width, floor, 1)
    for month in range(11):
        fig.line(
            left + month * month_width + month_width / 2, temp_y(temps[month]),
            left + (month + 1) * month_width + month_width / 2, temp_y(temps[month + 1]), 2,
        )
    for month in range(12):
        fig.circle(left + month * month_width + month_width / 2, temp_y(temps[month]), 3, 2)
    fig.text(left + 8, 10, "t, °C", "l")

    kind = r.choice(["range", "below", "warmest", "wettest"])
    if kind == "range":
        question = "Определите годовую амплитуду температур: разность между температурой самого тёплого и самого холодного месяца."
        answer = max(temps) - min(temps)
        how = f"{max(temps)} - ({min(temps)}) = {answer} °C."
    elif kind == "below":
        answer = sum(1 for value in temps if value < 0)
        question = "Сколько месяцев в году средняя температура ниже нуля?"
        how = f"Ниже нулевой линии лежат точки {answer} месяцев."
    elif kind == "warmest":
        question, answer = "Определите среднюю температуру самого тёплого месяца.", max(temps)
        how = f"Самая высокая точка линии соответствует {max(temps)} °C."
    else:
        question, answer = "В каком месяце выпало больше всего осадков? Запишите номер месяца.", wettest + 1
        how = f"Самый высокий столбик стоит над месяцем номер {wettest + 1}."
    return task(
        "На рисунке показана климатическая диаграмма: линия с точками показывает среднюю температуру по месяцам, "
        f"светлые столбики показывают количество осадков. По горизонтали указаны номера месяцев. {question}",
        dec(answer),
        how,
        fig,
    )


WINDS = [("С", 0, -1, "северный"), ("СВ", 1, -1, "северо-восточный"), ("В", 1, 0, "восточный"), ("ЮВ", 1, 1, "юго-восточный"),
         ("Ю", 0, 1, "южный"), ("ЮЗ", -1, 1, "юго-западный"), ("З", -1, 0, "западный"), ("СЗ", -1, -1, "северо-западный")]


def fig_wind_rose(r):
    days = [r.randint(1, 5) for _ in WINDS]
    top = r.randrange(8)
    days[top] = 6
    fig = Fig()
    cx, cy, unit = 210, 130, 17
    for ring in range(1, 7):
        fig.circle(cx, cy, ring * unit, 0)
    ends = []
    for (label, dx, dy, _), count in zip(WINDS, days):
        norm = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / norm, dy / norm
        fig.line(cx, cy, cx + ux * 6 * unit, cy + uy * 6 * unit, 0)
        ends.append((cx + ux * count * unit, cy + uy * count * unit))
        fig.text(cx + ux * (6 * unit + 13), cy + uy * (6 * unit + 13), label)
    for index in range(8):
        fig.line(*ends[index], *ends[(index + 1) % 8], 2)
    for x, y in ends:
        fig.circle(x, y, 3, 2)

    asked = r.randrange(8)
    if r.random() < 0.5:
        return task(
            "На рисунке показана роза ветров за месяц. Расстояние между соседними окружностями соответствует одному дню. "
            f"Сколько дней дул {WINDS[asked][3]} ветер?",
            dec(days[asked]),
            f"Точка на луче «{WINDS[asked][0]}» лежит на окружности номер {days[asked]} от центра.",
            fig,
        )
    options = [WINDS[top][3]] + r.sample([name for index, (_, _, _, name) in enumerate(WINDS) if index != top], 3)
    r.shuffle(options)
    lines = "\n".join(f"{number}) {option}" for number, option in enumerate(options, start=1))
    made = task(
        "На рисунке показана роза ветров за месяц. Расстояние между соседними окружностями соответствует одному дню. "
        f"Ветер какого направления дул чаще всего? Запишите номер ответа.\n{lines}",
        str(options.index(WINDS[top][3]) + 1),
        f"Дальше всего от центра точка на луче «{WINDS[top][0]}»: это {WINDS[top][3]} ветер.",
        fig,
    )
    made["kind"] = "exact"
    return made


# ---------------------------------------------------------------- обществознание

POLL_TOPICS = [
    "Читаете ли вы книги каждую неделю?", "Занимаетесь ли вы спортом регулярно?", "Довольны ли вы своей работой?",
    "Планируете ли вы получать высшее образование?", "Участвуете ли вы в выборах?", "Откладываете ли вы часть дохода?",
    "Пользуетесь ли вы общественным транспортом каждый день?", "Следите ли вы за новостями экономики?",
    "Хотели бы вы открыть своё дело?", "Доверяете ли вы рекламе?",
]
POLL_ANSWERS = ["да", "скорее да", "скорее нет", "нет", "не знаю"]


def fig_poll(r):
    while True:
        shares = [r.randrange(5, 50, 5) for _ in range(4)]
        if 5 <= 100 - sum(shares) <= 50:
            shares.append(100 - sum(shares))
            break
    topic = r.choice(POLL_TOPICS)
    fig = Fig()
    left, bottom = 44, 220
    scale = 3.6
    for level in range(0, 51, 10):
        y = bottom - level * scale
        fig.line(left, y, 414, y, 0)
        fig.text(left - 6, y, level, "r")
    fig.line(left, 30, left, bottom, 1)
    fig.line(left, bottom, 414, bottom, 1)
    for index, share in enumerate(shares):
        x = left + 14 + index * 74
        fig.rect(x, bottom - share * scale, 46, share * scale, 2)
        fig.text(x + 23, bottom + 14, POLL_ANSWERS[index])
    kind = r.choice(["positive", "negative", "difference", "single"])
    if kind == "positive":
        question, answer = "Сколько процентов опрошенных ответили «да» или «скорее да»?", shares[0] + shares[1]
        how = f"{shares[0]} + {shares[1]} = {answer}%."
    elif kind == "negative":
        question, answer = "Сколько процентов опрошенных ответили «нет» или «скорее нет»?", shares[2] + shares[3]
        how = f"{shares[2]} + {shares[3]} = {answer}%."
    elif kind == "difference":
        question, answer = "На сколько процентных пунктов самый частый ответ опережает самый редкий?", max(shares) - min(shares)
        how = f"{max(shares)} - {min(shares)} = {answer}."
    else:
        index = r.randrange(5)
        question, answer = f"Сколько процентов опрошенных выбрали ответ «{POLL_ANSWERS[index]}»?", shares[index]
        how = f"Высота столбика «{POLL_ANSWERS[index]}» равна {answer}%."
    return task(
        f"Социологи задали жителям города вопрос: «{topic}» Результаты опроса (в процентах от числа опрошенных) "
        f"показаны на диаграмме. {question}",
        dec(answer),
        how,
        fig,
    )


MARKET_REASONS = {
    ("D", 1): ["рост доходов покупателей", "успешная рекламная кампания товара", "рост цен на товары-заменители", "ожидание покупателями роста цен"],
    ("D", -1): ["снижение доходов покупателей", "товар вышел из моды", "снижение цен на товары-заменители", "уменьшение числа покупателей"],
    ("S", 1): ["снижение цен на сырьё", "внедрение новой производительной технологии", "снижение налогов на производителей", "рост числа продавцов на рынке"],
    ("S", -1): ["рост цен на сырьё", "повышение налогов на производителей", "уход части фирм с рынка", "рост затрат на оплату труда"],
}
MARKET_GOODS = ["яблок", "велосипедов", "смартфонов", "мебели", "спортивной обуви", "молочных продуктов", "автомобилей", "книг", "кофе", "игрушек"]


def fig_market(r):
    curve, direction = r.choice(list(MARKET_REASONS))
    good = r.choice(MARKET_GOODS)
    fig = Fig()
    fig.line(60, 20, 60, 230, 1)
    fig.line(60, 230, 400, 230, 1)
    fig.text(44, 26, "P")
    fig.text(392, 246, "Q")
    shift = 70
    if curve == "D":
        first = (100, 50, 270, 210)
    else:
        first = (100, 210, 270, 50)
    base_x = 0 if direction == 1 else shift
    moved_x = shift if direction == 1 else 0
    x1, y1, x2, y2 = first
    fig.line(x1 + base_x, y1, x2 + base_x, y2, 1)
    fig.line(x1 + moved_x, y1, x2 + moved_x, y2, 2)
    label_y = 40 if curve == "D" else 44
    label_x1 = (x1 if curve == "D" else x2) + base_x
    label_x2 = (x1 if curve == "D" else x2) + moved_x
    fig.text(label_x1, label_y - 10, curve)
    fig.text(label_x2, label_y - 10, curve + sub(1))
    middle_y = 130
    arrow(fig, 185 + base_x, middle_y, 185 + moved_x - (8 if direction == 1 else -8), middle_y, 1, 9)

    correct = r.choice(MARKET_REASONS[(curve, direction)])
    wrong = [reason for key, reasons in MARKET_REASONS.items() if key != (curve, direction) for reason in reasons]
    options = [correct] + r.sample(wrong, 3)
    r.shuffle(options)
    lines = "\n".join(f"{number}) {option}" for number, option in enumerate(options, start=1))
    name = "спроса" if curve == "D" else "предложения"
    change = "увеличение" if direction == 1 else "уменьшение"
    made = task(
        f"На рисунке показано изменение на рынке {good}: линия {name} переместилась из положения {curve} в положение {curve}{sub(1)} "
        f"(P цена товара, Q количество товара). Что могло вызвать такое изменение? Запишите номер ответа.\n{lines}",
        str(options.index(correct) + 1),
        f"Сдвиг линии {'вправо' if direction == 1 else 'влево'} означает {change} {name}. Подходит причина: {correct}.",
        fig,
    )
    made["kind"] = "exact"
    return made


generators.MATH_BASE += [fig_bar_chart, fig_grid_triangle, fig_linear_graph, fig_line_chart, fig_grid_trapezoid, fig_right_triangle]
generators.MATH_PROF += [fig_linear_graph, fig_grid_triangle, fig_grid_trapezoid, fig_right_triangle, fig_parabola, fig_vector]
generators.PHYSICS += [fig_velocity_graph, fig_xt_graph, fig_circuit_series, fig_circuit_parallel, fig_forces, fig_pv_work, fig_iu_graph]
generators.INFORMATICS += [fig_roads, fig_paths, fig_spreadsheet]
generators.CHEMISTRY += [fig_atom, fig_skeleton]
generators.GENERATED["biology"] += [fig_punnett, fig_dna]
generators.GENERATED["geography"] += [fig_climate, fig_wind_rose]
generators.GENERATED["social"] += [fig_poll, fig_market]
