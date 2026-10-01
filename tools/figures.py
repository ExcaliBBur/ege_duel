"""Задания с рисунками.

Рисунок описывается простыми фигурами (линии, прямоугольники, круги, подписи), игра рисует его сама.
Файлы-картинки не нужны, поэтому не нужна и модерация изображений в Roblox.
При импорте модуль добавляет свои генераторы в списки предметов из generators.py.
"""

from fractions import Fraction

import generators
from generators import dec, task


class Fig:
    """Рисунок к заданию. Координаты в пикселях, начало в левом верхнем углу.

    Стили: 0 сетка, 1 основная линия, 2 выделенная линия или заливка.
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


generators.MATH_BASE += [fig_bar_chart, fig_grid_triangle, fig_linear_graph]
generators.MATH_PROF += [fig_linear_graph, fig_grid_triangle]
generators.PHYSICS += [fig_velocity_graph]
generators.INFORMATICS += [fig_roads]
