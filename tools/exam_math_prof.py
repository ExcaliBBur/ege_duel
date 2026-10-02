"""Математика, профильный уровень: первая часть, задания №1-12 по структуре ЕГЭ 2026.

Каждый номер отвечает за свою тему, как на экзамене. У номера несколько подтипов заданий,
числа в условии случайные, ответ вычисляет программа.
"""

import math
from fractions import Fraction

from exam_common import Entry, Plane, frac, is_finite_decimal, round_half_up, signed, table_figure
from generators import dec, poly, sub, sup, task

TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (12, 35, 37), (11, 60, 61)]
DECIMAL_TRIPLES = [(3, 4, 5), (7, 24, 25), (6, 8, 10), (15, 20, 25), (9, 12, 15), (12, 16, 20), (14, 48, 50), (18, 24, 30)]


# ---------------------------------------------------------------- №1 Планиметрия


def p1_right_triangle(r):
    a, b, c = r.choice(DECIMAL_TRIPLES)
    if r.random() < 0.5:
        a, b = b, a
    kind = r.choice(["sin", "cos", "tg", "find_sin"])
    if kind == "sin":
        return task(
            f"В треугольнике ABC угол C равен 90°, AB = {c}, sin A = {frac(Fraction(a, c))}. Найдите BC.",
            dec(a),
            f"BC = AB · sin A = {c} · {frac(Fraction(a, c))} = {a}.",
        )
    if kind == "cos":
        return task(
            f"В треугольнике ABC угол C равен 90°, AB = {c}, cos A = {frac(Fraction(b, c))}. Найдите BC.",
            dec(a),
            f"AC = AB · cos A = {b}. По теореме Пифагора BC = √({c}² - {b}²) = {a}.",
        )
    if kind == "tg":
        return task(
            f"В треугольнике ABC угол C равен 90°, AC = {b}, tg A = {frac(Fraction(a, b))}. Найдите AB.",
            dec(c),
            f"BC = AC · tg A = {a}. По теореме Пифагора AB = √({b}² + {a}²) = {c}.",
        )
    return task(
        f"В треугольнике ABC угол C равен 90°, AC = {b}, BC = {a}. Найдите sin A.",
        dec(Fraction(a, c)),
        f"AB = √({b}² + {a}²) = {c}, sin A = BC : AB = {dec(Fraction(a, c))}.",
    )


def p1_isosceles(r):
    kind = r.choice(["angle", "height", "tangent", "exterior"])
    if kind == "angle":
        vertex = r.randrange(20, 161, 4)
        return task(
            f"В треугольнике ABC стороны AC и BC равны, угол C равен {vertex}°. Найдите угол A. Ответ дайте в градусах.",
            dec(Fraction(180 - vertex, 2)),
            f"Углы при основании равны: (180° - {vertex}°) : 2 = {dec(Fraction(180 - vertex, 2))}°.",
        )
    if kind == "exterior":
        vertex = r.randrange(20, 161, 4)
        base = Fraction(180 - vertex, 2)
        return task(
            f"В треугольнике ABC стороны AC и BC равны, угол C равен {vertex}°. Найдите внешний угол при вершине B. Ответ дайте в градусах.",
            dec(180 - base),
            f"Угол B равен {dec(base)}°, внешний угол равен 180° - {dec(base)}° = {dec(180 - base)}°.",
        )
    if kind == "height":
        half, height, side = r.choice(TRIPLES)
        k = r.choice([1, 2])
        half, height, side = half * k, height * k, side * k
        return task(
            f"В треугольнике ABC AC = BC = {side}, AB = {2 * half}. Найдите высоту CH.",
            dec(height),
            f"Высота к основанию делит его пополам: AH = {half}. CH = √({side}² - {half}²) = {height}.",
        )
    # Тангенс должен записываться конечной десятичной дробью.
    half, height, _ = r.choice([t for t in TRIPLES + [(4, 3, 5), (12, 5, 13), (24, 7, 25), (15, 8, 17)] if is_finite_decimal(Fraction(t[1], t[0]))])
    return task(
        f"В треугольнике ABC AC = BC, высота CH равна {height}, AB = {2 * half}. Найдите тангенс угла A.",
        dec(Fraction(height, half)),
        f"AH = {half}, tg A = CH : AH = {height} : {half} = {dec(Fraction(height, half))}.",
    )


def p1_parallelogram(r):
    kind = r.choice(["height", "angle", "perimeter"])
    if kind == "height":
        a, b = sorted(r.sample(range(4, 25), 2))
        big_height = r.randint(2, b - 1)
        area = a * big_height
        return task(
            f"Площадь параллелограмма равна {area}, две его стороны равны {a} и {b}. Найдите большую высоту этого параллелограмма.",
            dec(big_height),
            f"Большая высота проведена к меньшей стороне: {area} : {a} = {big_height}.",
        )
    if kind == "angle":
        difference = r.randrange(10, 121, 10)
        return task(
            f"Один из углов параллелограмма на {difference}° больше другого. Найдите больший угол параллелограмма. Ответ дайте в градусах.",
            dec(Fraction(180 + difference, 2)),
            f"Сумма соседних углов равна 180°, больший угол равен (180° + {difference}°) : 2 = {dec(Fraction(180 + difference, 2))}°.",
        )
    ratio_a, ratio_b = r.choice([(1, 2), (2, 3), (3, 4), (1, 3), (2, 5), (3, 7)])
    unit = r.randint(2, 9)
    return task(
        f"Периметр параллелограмма равен {2 * unit * (ratio_a + ratio_b)}. Одна сторона параллелограмма относится к другой как {ratio_a} : {ratio_b}. "
        "Найдите большую сторону параллелограмма.",
        dec(unit * ratio_b),
        f"Полупериметр равен {unit * (ratio_a + ratio_b)}, на одну часть приходится {unit}, большая сторона равна {unit * ratio_b}.",
    )


def p1_trapezoid(r):
    kind = r.choice(["midline_part", "height", "midline", "area"])
    if kind == "midline_part":
        a, b = sorted(r.sample(range(4, 60, 2), 2))
        return task(
            f"Основания трапеции равны {a} и {b}. Найдите больший из отрезков, на которые делит среднюю линию этой трапеции одна из её диагоналей.",
            dec(Fraction(b, 2)),
            f"Диагональ делит среднюю линию на средние линии двух треугольников: {dec(Fraction(a, 2))} и {dec(Fraction(b, 2))}.",
        )
    if kind == "height":
        leg, height, side = r.choice(TRIPLES)
        top = r.randint(3, 20)
        return task(
            f"Основания равнобедренной трапеции равны {top} и {top + 2 * leg}, боковая сторона равна {side}. Найдите высоту трапеции.",
            dec(height),
            f"Проекция боковой стороны на основание равна ({top + 2 * leg} - {top}) : 2 = {leg}. Высота равна √({side}² - {leg}²) = {height}.",
        )
    if kind == "midline":
        a = r.randint(3, 30)
        midline = a + r.randint(2, 15)
        return task(
            f"Средняя линия трапеции равна {midline}, а меньшее основание равно {a}. Найдите большее основание трапеции.",
            dec(2 * midline - a),
            f"Сумма оснований равна {2 * midline}, большее основание равно {2 * midline} - {a} = {2 * midline - a}.",
        )
    a, b = sorted(r.sample(range(3, 30), 2))
    height = r.randint(2, 14)
    if (a + b) * height % 2:
        height += 1
    return task(
        f"Основания трапеции равны {a} и {b}, а высота равна {height}. Найдите площадь трапеции.",
        dec(Fraction((a + b) * height, 2)),
        f"S = ({a} + {b}) : 2 · {height} = {dec(Fraction((a + b) * height, 2))}.",
    )


def p1_circle_angles(r):
    kind = r.choice(["central_more", "arc_part", "tangent_chord", "diameter"])
    if kind == "central_more":
        x = r.randrange(15, 86, 1)
        return task(
            f"Центральный угол на {x}° больше острого вписанного угла, опирающегося на ту же дугу окружности. Найдите вписанный угол. Ответ дайте в градусах.",
            dec(x),
            f"Центральный угол вдвое больше вписанного: 2x - x = {x}, вписанный угол равен {x}°.",
        )
    if kind == "arc_part":
        part = r.choice([5, 6, 8, 9, 10, 12, 15, 18, 20])
        return task(
            f"Найдите вписанный угол, опирающийся на дугу, длина которой равна 1/{part} длины окружности. Ответ дайте в градусах.",
            dec(Fraction(180, part)),
            f"Дуга содержит 360° : {part} = {dec(Fraction(360, part))}°, вписанный угол равен её половине.",
        )
    if kind == "tangent_chord":
        arc = r.randrange(20, 171, 2)
        return task(
            f"Хорда AB стягивает дугу окружности в {arc}°. Найдите угол между этой хордой и касательной к окружности, проведённой через точку B. Ответ дайте в градусах.",
            dec(Fraction(arc, 2)),
            f"Угол между касательной и хордой равен половине дуги, заключённой между ними: {arc}° : 2 = {dec(Fraction(arc, 2))}°.",
        )
    angle = r.randrange(10, 81, 1)
    return task(
        f"Сторона AB треугольника ABC является диаметром описанной около него окружности, угол A равен {angle}°. Найдите угол B. Ответ дайте в градусах.",
        dec(90 - angle),
        f"Угол C опирается на диаметр и равен 90°, поэтому угол B равен 90° - {angle}° = {90 - angle}°.",
    )


def p1_incircle(r):
    kind = r.choice(["right", "equilateral", "square", "area"])
    if kind == "right":
        a, b, c = r.choice([t for t in TRIPLES if (t[0] + t[1] - t[2]) % 2 == 0])
        k = r.choice([1, 2, 3])
        return task(
            f"Катеты прямоугольного треугольника равны {a * k} и {b * k}. Найдите радиус окружности, вписанной в этот треугольник.",
            dec(Fraction((a + b - c) * k, 2)),
            f"Гипотенуза равна {c * k}. r = (a + b - c) : 2 = ({a * k} + {b * k} - {c * k}) : 2 = {dec(Fraction((a + b - c) * k, 2))}.",
        )
    if kind == "equilateral":
        radius = r.randint(2, 30)
        return task(
            f"Радиус окружности, вписанной в правильный треугольник, равен {radius}. Найдите высоту этого треугольника.",
            dec(3 * radius),
            f"Центр вписанной окружности делит высоту в отношении 2 : 1, считая от вершины, поэтому высота равна 3r = {3 * radius}.",
        )
    if kind == "square":
        radius = r.randint(2, 40)
        return task(
            f"Найдите сторону квадрата, описанного около окружности радиуса {radius}.",
            dec(2 * radius),
            f"Сторона описанного квадрата равна диаметру окружности: 2 · {radius} = {2 * radius}.",
        )
    radius = r.randint(2, 12)
    perimeter = r.randrange(20, 121, 2)
    return task(
        f"Периметр треугольника равен {perimeter}, а радиус вписанной окружности равен {radius}. Найдите площадь этого треугольника.",
        dec(Fraction(perimeter * radius, 2)),
        f"S = p · r, где p это полупериметр: {dec(Fraction(perimeter, 2))} · {radius} = {dec(Fraction(perimeter * radius, 2))}.",
    )


def p1_circumcircle(r):
    kind = r.choice(["right", "angle30", "angle150", "rectangle"])
    if kind == "right":
        a, b, c = r.choice(TRIPLES)
        k = r.choice([1, 2, 4])
        return task(
            f"Катеты прямоугольного треугольника равны {a * k} и {b * k}. Найдите радиус окружности, описанной около этого треугольника.",
            dec(Fraction(c * k, 2)),
            f"Гипотенуза равна {c * k}, центр описанной окружности лежит на её середине: R = {dec(Fraction(c * k, 2))}.",
        )
    if kind in ("angle30", "angle150"):
        side = r.randint(3, 60)
        angle = 30 if kind == "angle30" else 150
        return task(
            f"Сторона AB треугольника ABC равна {side}, противолежащий ей угол C равен {angle}°. Найдите радиус окружности, описанной около этого треугольника.",
            dec(side),
            f"По теореме синусов R = AB : (2 · sin C) = {side} : (2 · 0,5) = {side}.",
        )
    a, b, c = r.choice(TRIPLES)
    return task(
        f"Стороны прямоугольника равны {a} и {b}. Найдите радиус окружности, описанной около этого прямоугольника.",
        dec(Fraction(c, 2)),
        f"Диагональ прямоугольника равна {c}, она является диаметром описанной окружности: R = {dec(Fraction(c, 2))}.",
    )


# ---------------------------------------------------------------- №2 Векторы

LENGTH_5 = [(3, 4), (4, 3), (-3, 4), (-4, 3), (3, -4), (4, -3), (5, 0), (0, 5), (-3, -4), (0, -5)]


def vector(name, x, y):
    return f"{name}({x}; {y})"


def v_sum_length(r):
    sx, sy, length = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (12, 5, 13), (8, 6, 10), (9, 12, 15), (7, 24, 25)])
    sx, sy = sx * r.choice([1, -1]), sy * r.choice([1, -1])
    ax, ay = r.randint(-9, 9), r.randint(-9, 9)
    kind = r.choice(["sum", "difference", "double"])
    if kind == "sum":
        bx, by = sx - ax, sy - ay
        expression, how = "a + b", f"a + b имеет координаты ({sx}; {sy})"
    elif kind == "difference":
        bx, by = ax - sx, ay - sy
        expression, how = "a - b", f"a - b имеет координаты ({sx}; {sy})"
    else:
        # 2a + b = (sx, sy)
        bx, by = sx - 2 * ax, sy - 2 * ay
        expression, how = "2a + b", f"2a + b имеет координаты ({sx}; {sy})"
    return task(
        f"Даны векторы {vector('a', ax, ay)} и {vector('b', bx, by)}. Найдите длину вектора {expression}.",
        dec(length),
        f"Вектор {how}, его длина равна √({sx * sx} + {sy * sy}) = {length}.",
    )


def v_dot(r):
    if r.random() < 0.6:
        ax, ay, bx, by = (r.randint(-9, 9) for _ in range(4))
        return task(
            f"Даны векторы {vector('a', ax, ay)} и {vector('b', bx, by)}. Найдите скалярное произведение a · b.",
            dec(ax * bx + ay * by),
            f"a · b = {ax} · ({bx}) + {ay} · ({by}) = {ax * bx + ay * by}.",
        )
    length_a, length_b = r.randint(2, 12), r.randint(2, 12)
    angle, cosine = r.choice([(60, Fraction(1, 2)), (120, Fraction(-1, 2)), (90, Fraction(0)), (0, Fraction(1)), (180, Fraction(-1))])
    return task(
        f"Длины векторов a и b равны {length_a} и {length_b}, а угол между ними равен {angle}°. Найдите скалярное произведение a · b.",
        dec(length_a * length_b * cosine),
        f"a · b = |a| · |b| · cos {angle}° = {length_a} · {length_b} · ({dec(cosine)}) = {dec(length_a * length_b * cosine)}.",
    )


def v_cosine(r):
    while True:
        (ax, ay), (bx, by) = r.sample(LENGTH_5, 2)
        ka, kb = r.choice([1, 2]), r.choice([1, 2])
        ax, ay, bx, by = ax * ka, ay * ka, bx * kb, by * kb
        cosine = Fraction(ax * bx + ay * by, 25 * ka * kb)
        if abs(cosine) != 1:
            break
    return task(
        f"Даны векторы {vector('a', ax, ay)} и {vector('b', bx, by)}. Найдите косинус угла между ними.",
        dec(cosine),
        f"a · b = {ax * bx + ay * by}, |a| = {5 * ka}, |b| = {5 * kb}; cos = {ax * bx + ay * by} : ({5 * ka} · {5 * kb}) = {dec(cosine)}.",
    )


def v_perpendicular(r):
    while True:
        bx = r.choice([n for n in range(-9, 10) if n != 0])
        ay, by = r.randint(-9, 9), r.randint(-9, 9)
        if ay != 0 and by != 0 and (ay * by) % bx == 0:
            break
    x = -ay * by // bx
    return task(
        f"При каком значении x векторы {vector('a', 'x', ay)} и {vector('b', bx, by)} перпендикулярны?",
        dec(x),
        f"Скалярное произведение должно быть равно нулю: {bx}x + ({ay}) · ({by}) = 0, откуда x = {x}.",
    )


def v_endpoint(r):
    ax, ay, vx, vy = (r.randint(-9, 9) for _ in range(4))
    kind = r.choice(["sum", "abscissa", "length"])
    if kind == "length":
        dx, dy, length = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (12, 5, 13), (15, 8, 17), (9, 12, 15)])
        dx, dy = dx * r.choice([1, -1]), dy * r.choice([1, -1])
        return task(
            f"Вектор AB с началом в точке A({ax}; {ay}) и концом в точке B({ax + dx}; {ay + dy}). Найдите длину вектора AB.",
            dec(length),
            f"Координаты вектора: ({dx}; {dy}), длина равна √({dx * dx} + {dy * dy}) = {length}.",
        )
    if kind == "sum":
        return task(
            f"Вектор AB с началом в точке A({ax}; {ay}) имеет координаты ({vx}; {vy}). Найдите сумму координат точки B.",
            dec(ax + vx + ay + vy),
            f"B({ax + vx}; {ay + vy}), сумма координат равна {ax + vx + ay + vy}.",
        )
    return task(
        f"Вектор AB с концом в точке B({ax}; {ay}) имеет координаты ({vx}; {vy}). Найдите абсциссу точки A.",
        dec(ax - vx),
        f"Абсцисса начала равна {ax} - ({vx}) = {ax - vx}.",
    )


# ---------------------------------------------------------------- №3 Стереометрия

BOX_QUADRUPLES = [(1, 2, 2, 3), (2, 3, 6, 7), (1, 4, 8, 9), (4, 4, 7, 9), (2, 6, 9, 11), (6, 6, 7, 11), (3, 4, 12, 13), (2, 10, 11, 15), (2, 5, 14, 15), (8, 9, 12, 17), (1, 12, 12, 17)]


def s_cube(r):
    edge = r.randint(2, 12)
    kind = r.choice(["diagonal_volume", "volume_surface", "surface_volume", "edge_change"])
    if kind == "diagonal_volume":
        return task(
            f"Диагональ куба равна √{3 * edge * edge}. Найдите его объём.",
            dec(edge**3),
            f"Диагональ куба равна a√3, откуда a = {edge}, объём равен {edge}³ = {edge ** 3}.",
        )
    if kind == "volume_surface":
        return task(
            f"Объём куба равен {edge ** 3}. Найдите площадь его поверхности.",
            dec(6 * edge * edge),
            f"Ребро равно {edge}, площадь поверхности равна 6 · {edge}² = {6 * edge * edge}.",
        )
    if kind == "surface_volume":
        return task(
            f"Площадь поверхности куба равна {6 * edge * edge}. Найдите его объём.",
            dec(edge**3),
            f"Площадь грани равна {edge * edge}, ребро равно {edge}, объём равен {edge ** 3}.",
        )
    factor = r.choice([2, 3, 4, 5])
    return task(
        f"Во сколько раз увеличится объём куба, если все его рёбра увеличить в {factor} раза?" if factor < 5
        else f"Во сколько раз увеличится объём куба, если все его рёбра увеличить в {factor} раз?",
        dec(factor**3),
        f"Объём пропорционален кубу ребра: {factor}³ = {factor ** 3}.",
    )


def s_box(r):
    a, b, c, d = r.choice(BOX_QUADRUPLES)
    edges = [a, b, c]
    r.shuffle(edges)
    a, b, c = edges
    kind = r.choice(["volume", "diagonal", "surface"])
    if kind == "volume":
        return task(
            f"Два ребра прямоугольного параллелепипеда, выходящие из одной вершины, равны {a} и {b}. Диагональ параллелепипеда равна {d}. Найдите объём параллелепипеда.",
            dec(a * b * c),
            f"Третье ребро равно √({d}² - {a}² - {b}²) = {c}, объём равен {a} · {b} · {c} = {a * b * c}.",
        )
    if kind == "diagonal":
        return task(
            f"Рёбра прямоугольного параллелепипеда, выходящие из одной вершины, равны {a}, {b} и {c}. Найдите его диагональ.",
            dec(d),
            f"d = √({a}² + {b}² + {c}²) = {d}.",
        )
    return task(
        f"Два ребра прямоугольного параллелепипеда, выходящие из одной вершины, равны {a} и {b}. Объём параллелепипеда равен {a * b * c}. Найдите площадь его поверхности.",
        dec(2 * (a * b + b * c + a * c)),
        f"Третье ребро равно {c}, площадь поверхности равна 2 · ({a * b} + {b * c} + {a * c}) = {2 * (a * b + b * c + a * c)}.",
    )


def s_prism(r):
    kind = r.choice(["water", "section", "volume"])
    if kind == "water":
        factor = r.choice([2, 3, 4, 5])
        height = factor * factor * r.randint(1, 9)
        return task(
            f"В сосуд, имеющий форму правильной треугольной призмы, налили воду. Уровень воды достигает {height} см. На какой высоте будет находиться уровень воды, "
            f"если её перелить в другой такой же сосуд, у которого сторона основания в {factor} раза больше, чем у первого? Ответ выразите в сантиметрах.",
            dec(height // (factor * factor)),
            f"Площадь основания больше в {factor * factor} раз, значит уровень воды ниже в {factor * factor} раз: {height} : {factor * factor} = {height // (factor * factor)}.",
        )
    if kind == "section":
        volume = 4 * r.randint(3, 40)
        return task(
            f"Через среднюю линию основания треугольной призмы, объём которой равен {volume}, проведена плоскость, параллельная боковому ребру. Найдите объём отсечённой треугольной призмы.",
            dec(volume // 4),
            f"Площадь основания отсечённой призмы в 4 раза меньше, высота та же: {volume} : 4 = {volume // 4}.",
        )
    a, b, c = r.choice(TRIPLES[:4])
    height = r.randint(2, 15)
    return task(
        f"Основанием прямой треугольной призмы служит прямоугольный треугольник с катетами {a} и {b}, боковое ребро равно {height}. Найдите объём призмы.",
        dec(Fraction(a * b * height, 2)),
        f"Площадь основания равна {dec(Fraction(a * b, 2))}, объём равен {dec(Fraction(a * b, 2))} · {height} = {dec(Fraction(a * b * height, 2))}.",
    )


def s_pyramid(r):
    kind = r.choice(["edge", "volume_change", "side"])
    if kind == "edge":
        options = [t for t in TRIPLES + [(4, 3, 5), (12, 5, 13), (15, 8, 17), (24, 7, 25)] if (2 * t[1] * t[1] * t[0]) % 3 == 0]
        height, half_diagonal, edge = r.choice(options)
        volume = Fraction(2 * half_diagonal * half_diagonal * height, 3)
        return task(
            f"В правильной четырёхугольной пирамиде высота равна {height}, боковое ребро равно {edge}. Найдите её объём.",
            dec(volume),
            f"Половина диагонали основания равна {half_diagonal}, площадь основания равна 2 · {half_diagonal}² = {2 * half_diagonal ** 2}, "
            f"объём равен {2 * half_diagonal ** 2} · {height} : 3 = {dec(volume)}.",
        )
    if kind == "volume_change":
        factor = r.choice([2, 3, 4])
        return task(
            f"Во сколько раз увеличится объём правильного тетраэдра, если все его рёбра увеличить в {factor} раза?",
            dec(factor**3),
            f"Объёмы подобных тел относятся как кубы соответствующих размеров: {factor}³ = {factor ** 3}.",
        )
    side = r.randint(2, 12)
    height = 3 * r.randint(1, 8)
    volume = Fraction(side * side * height, 3)
    return task(
        f"Сторона основания правильной четырёхугольной пирамиды равна {side}, высота равна {height}. Найдите объём пирамиды.",
        dec(volume),
        f"Площадь основания равна {side * side}, объём равен {side * side} · {height} : 3 = {dec(volume)}.",
    )


def s_cylinder(r):
    kind = r.choice(["detail", "pour", "lateral"])
    if kind == "detail":
        volume = r.randrange(600, 5001, 100)
        level = r.choice([10, 12, 15, 16, 20, 25])
        rise = r.choice([2, 3, 4, 5, 6])
        if (volume * rise) % level:
            volume = level * 100
        return task(
            f"В цилиндрический сосуд налили {volume} см³ воды. Уровень воды при этом достигает высоты {level} см. В жидкость полностью погрузили деталь. "
            f"При этом уровень жидкости в сосуде поднялся на {rise} см. Чему равен объём детали? Ответ выразите в см³.",
            dec(Fraction(volume * rise, level)),
            f"Объём детали равен объёму вытесненной воды: {volume} · {rise} : {level} = {dec(Fraction(volume * rise, level))}.",
        )
    if kind == "pour":
        factor = r.choice([2, 3, 4])
        level = factor * factor * r.randint(1, 9)
        return task(
            f"В цилиндрическом сосуде уровень жидкости достигает {level} см. На какой высоте будет находиться уровень жидкости, если её перелить во второй "
            f"цилиндрический сосуд, диаметр которого в {factor} раза больше диаметра первого? Ответ выразите в сантиметрах.",
            dec(level // (factor * factor)),
            f"Площадь основания больше в {factor * factor} раз, уровень ниже в {factor * factor} раз: {level // (factor * factor)}.",
        )
    radius, height = r.randint(2, 9), r.randint(2, 12)
    return task(
        f"Радиус основания цилиндра равен {radius}, высота равна {height}. Найдите площадь боковой поверхности цилиндра, делённую на π.",
        dec(2 * radius * height),
        f"S = 2πrh = 2π · {radius} · {height}; после деления на π получаем {2 * radius * height}.",
    )


def s_cone(r):
    kind = r.choice(["small", "radius_change", "axial", "volume"])
    if kind == "small":
        volume = 8 * r.randint(2, 40)
        return task(
            f"Объём конуса равен {volume}. Через середину высоты параллельно основанию конуса проведено сечение, которое является основанием меньшего конуса с той же вершиной. "
            "Найдите объём меньшего конуса.",
            dec(volume // 8),
            f"Меньший конус подобен данному с коэффициентом 1/2, объём меньше в 8 раз: {volume // 8}.",
        )
    if kind == "radius_change":
        factor = r.choice([2, 3, 4, 5, 6])
        word = "раза" if factor < 5 else "раз"
        return task(
            f"Во сколько раз увеличится объём конуса, если радиус его основания увеличить в {factor} {word}, а высоту оставить прежней?",
            dec(factor * factor),
            f"Объём пропорционален квадрату радиуса: {factor}² = {factor * factor}.",
        )
    radius, height, slant = r.choice(TRIPLES + [(4, 3, 5), (12, 5, 13), (15, 8, 17)])
    if kind == "axial":
        return task(
            f"Высота конуса равна {height}, образующая равна {slant}. Найдите площадь его осевого сечения.",
            dec(radius * height),
            f"Радиус основания равен √({slant}² - {height}²) = {radius}. Осевое сечение это треугольник с основанием {2 * radius} и высотой {height}: S = {radius * height}.",
        )
    if (radius * radius * height) % 3:
        height *= 3
    return task(
        f"Радиус основания конуса равен {radius}, высота равна {height}. Найдите объём конуса, делённый на π.",
        dec(Fraction(radius * radius * height, 3)),
        f"V = πr²h : 3 = π · {radius * radius} · {height} : 3; после деления на π получаем {dec(Fraction(radius * radius * height, 3))}.",
    )


def s_sphere(r):
    kind = r.choice(["surface_change", "volume_change", "cylinder_surface", "cylinder_volume"])
    factor = r.choice([2, 3, 4, 5])
    word = "раза" if factor < 5 else "раз"
    if kind == "surface_change":
        return task(
            f"Во сколько раз увеличится площадь поверхности шара, если радиус шара увеличить в {factor} {word}?",
            dec(factor * factor),
            f"Площадь поверхности пропорциональна квадрату радиуса: {factor}² = {factor * factor}.",
        )
    if kind == "volume_change":
        return task(
            f"Во сколько раз увеличится объём шара, если его радиус увеличить в {factor} {word}?",
            dec(factor**3),
            f"Объём пропорционален кубу радиуса: {factor}³ = {factor ** 3}.",
        )
    if kind == "cylinder_surface":
        surface = 2 * r.randint(3, 60)
        return task(
            f"Шар вписан в цилиндр. Площадь поверхности шара равна {surface}. Найдите площадь полной поверхности цилиндра.",
            dec(Fraction(3 * surface, 2)),
            f"Площадь поверхности шара 4πr², цилиндра 6πr², то есть в 1,5 раза больше: {dec(Fraction(3 * surface, 2))}.",
        )
    volume = 3 * r.randint(2, 50)
    return task(
        f"Цилиндр описан около шара. Объём цилиндра равен {volume}. Найдите объём шара.",
        dec(2 * volume // 3),
        f"Объём шара равен 4πr³/3, объём цилиндра 2πr³: шар занимает 2/3 объёма цилиндра, то есть {2 * volume // 3}.",
    )


# ---------------------------------------------------------------- №4 Начала теории вероятностей

SPORTS = ["по гимнастике", "по прыжкам в воду", "по фигурному катанию", "по художественной гимнастике", "по синхронному плаванию"]
COUNTRIES = [("России", "США", "Китая"), ("Сербии", "Хорватии", "Словении"), ("Норвегии", "Дании", "Швеции"), ("Испании", "Португалии", "Италии"), ("Японии", "Кореи", "Китая")]


def pr_sportsmen(r):
    total = r.choice([20, 25, 40, 50, 80])
    first = r.randint(2, total // 3)
    second = r.randint(2, total // 3)
    third = total - first - second
    a, b, c = r.choice(COUNTRIES)
    return task(
        f"В чемпионате {r.choice(SPORTS)} участвуют {total} спортсменок: {first} из {a}, {second} из {b}, остальные из {c}. "
        f"Порядок, в котором выступают спортсменки, определяется жребием. Найдите вероятность того, что спортсменка, выступающая первой, окажется из {c}.",
        dec(Fraction(third, total)),
        f"Из {c} выступает {third} спортсменок, вероятность равна {third} : {total} = {dec(Fraction(third, total))}.",
    )


def pr_defect(r):
    item, bad = r.choice([("садовых насосов", "подтекают"), ("аккумуляторов", "неисправны"), ("фонариков", "неисправны"), ("чайников", "имеют дефект")])
    total = r.choice([500, 1000, 1500, 2000, 250, 400, 800])
    while True:
        defect = r.randint(2, 40)
        if is_finite_decimal(Fraction(total - defect, total)):
            break
    return task(
        f"В среднем из {total} {item}, поступивших в продажу, {defect} {bad}. Найдите вероятность того, что один случайно выбранный для контроля товар исправен.",
        dec(Fraction(total - defect, total)),
        f"Исправных {total - defect}, вероятность равна {total - defect} : {total} = {dec(Fraction(total - defect, total))}.",
    )


def pr_bags(r):
    good = r.choice([50, 80, 100, 120, 150, 180, 200])
    bad = r.randint(2, 20)
    value = round_half_up(Fraction(good, good + bad), 2)
    return task(
        f"Фабрика выпускает сумки. В среднем на {good} качественных сумок приходится {bad} сумок со скрытыми дефектами. "
        "Найдите вероятность того, что купленная сумка окажется качественной. Результат округлите до сотых.",
        dec(value),
        f"Всего сумок {good + bad}, вероятность равна {good} : {good + bad} ≈ {dec(value)}.",
    )


def pr_dice(r):
    total = r.randint(4, 10)
    count = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == total)
    value = round_half_up(Fraction(count, 36), 2)
    return task(
        f"В случайном эксперименте бросают две игральные кости. Найдите вероятность того, что в сумме выпадет {total} очков. Результат округлите до сотых.",
        dec(value),
        f"Всего исходов 36, подходящих {count}: {count} : 36 ≈ {dec(value)}.",
    )


def pr_coin(r):
    tosses = r.choice([2, 3, 4])
    heads = r.randint(0, tosses)
    word = {2: "дважды", 3: "трижды", 4: "четыре раза"}[tosses]
    count = math.comb(tosses, heads)
    how_many = {0: "ни разу", 1: "ровно один раз", 2: "ровно два раза", 3: "ровно три раза", 4: "ровно четыре раза"}[heads]
    return task(
        f"В случайном эксперименте симметричную монету бросают {word}. Найдите вероятность того, что орёл выпадет {how_many}.",
        dec(Fraction(count, 2**tosses)),
        f"Всего исходов {2 ** tosses}, подходящих {count}: вероятность равна {dec(Fraction(count, 2 ** tosses))}.",
    )


def pr_tickets(r):
    subject, topic = r.choice([("биологии", "ботанике"), ("математике", "неравенствам"), ("физике", "оптике"), ("химии", "углеводородам"), ("истории", "XX веку")])
    total = r.choice([20, 25, 40, 50])
    with_topic = r.randint(2, total - 2)
    return task(
        f"В сборнике билетов по {subject} всего {total} билетов, в {with_topic} из них встречается вопрос по {topic}. "
        f"Найдите вероятность того, что в случайно выбранном на экзамене билете школьнику не достанется вопроса по {topic}.",
        dec(Fraction(total - with_topic, total)),
        f"Билетов без такого вопроса {total - with_topic}, вероятность равна {dec(Fraction(total - with_topic, total))}.",
    )


def pr_conference(r):
    while True:
        days = r.choice([3, 4, 5])
        first_days = r.randint(1, days - 2)
        per_day = r.randint(8, 24)
        rest_each = r.randint(4, 20)
        total = first_days * per_day + (days - first_days) * rest_each
        if is_finite_decimal(Fraction(rest_each, total)):
            break
    if first_days == 1:
        first_text = f"В первый день запланировано {per_day} докладов"
    else:
        first_text = f"В первые {first_days} дня запланировано по {per_day} докладов"
    return task(
        f"Научная конференция проводится в {days} {'дня' if days < 5 else 'дней'}. Всего запланировано {total} докладов. {first_text}, "
        "остальные распределены поровну между оставшимися днями. Порядок докладов определяется жеребьёвкой. "
        "Какова вероятность, что доклад профессора М. окажется запланированным на последний день конференции?",
        dec(Fraction(rest_each, total)),
        f"На последний день приходится {rest_each} докладов, вероятность равна {rest_each} : {total} = {dec(Fraction(rest_each, total))}.",
    )


def pr_pairs(r):
    sport, people = r.choice([("бадминтону", "бадминтонистов"), ("теннису", "теннисистов"), ("шахматам", "шахматистов"), ("настольному теннису", "спортсменов")])
    total = r.choice([11, 21, 26, 51, 41, 76])
    russians = r.randint(3, total // 2)
    name = r.choice(["Руслан Орлов", "Максим Зайцев", "Антон Попов", "Никита Литвинов", "Сергей Зуев"])
    value = Fraction(russians - 1, total - 1)
    if not is_finite_decimal(value):
        return pr_pairs(r)
    return task(
        f"Перед началом первого тура чемпионата по {sport} участников разбивают на игровые пары случайным образом с помощью жребия. "
        f"Всего в чемпионате участвует {total} {people}, среди которых {russians} спортсменов из России, в том числе {name}. "
        f"Найдите вероятность того, что в первом туре {name} будет играть с каким-либо спортсменом из России.",
        dec(value),
        f"Соперником может стать любой из {total - 1} участников, из России среди них {russians - 1}: {russians - 1} : {total - 1} = {dec(value)}.",
    )


# ---------------------------------------------------------------- №5 Вероятности сложных событий


def c_two_machines(r):
    p = Fraction(r.choice([20, 25, 30, 35, 40]), 100)
    both = Fraction(r.randint(6, int(p * 100) - 4), 100)
    return task(
        "В торговом центре два одинаковых автомата продают кофе. Вероятность того, что к концу дня в автомате закончится кофе, "
        f"равна {dec(p)}. Вероятность того, что кофе закончится в обоих автоматах, равна {dec(both)}. "
        "Найдите вероятность того, что к концу дня кофе останется в обоих автоматах.",
        dec(1 - (2 * p - both)),
        f"Кофе закончится хотя бы в одном автомате с вероятностью {dec(p)} + {dec(p)} - {dec(both)} = {dec(2 * p - both)}. Искомая вероятность равна {dec(1 - (2 * p - both))}.",
    )


def c_shooter(r):
    hit = Fraction(r.choice([6, 7, 8, 9]), 10)
    shots = r.choice([4, 5])
    hits = r.randint(1, shots - 1)
    value = hit**hits * (1 - hit) ** (shots - hits)
    names = {1: "первый раз", 2: "первые два раза", 3: "первые три раза", 4: "первые четыре раза"}
    rest = {1: "последний раз промахнулся", 2: "последние два раза промахнулся", 3: "последние три раза промахнулся", 4: "последние четыре раза промахнулся"}
    return task(
        f"Биатлонист {'четыре' if shots == 4 else 'пять'} раз стреляет по мишеням. Вероятность попадания в мишень при одном выстреле равна {dec(hit)}. "
        f"Найдите вероятность того, что биатлонист {names[hits]} попал в мишени, а {rest[shots - hits]}. Результат округлите до сотых.",
        dec(round_half_up(value, 2)),
        f"{dec(hit)}{sup(hits)} · {dec(1 - hit)}{sup(shots - hits)} = {dec(value)} ≈ {dec(round_half_up(value, 2))}.",
    )


def c_factories(r):
    share = Fraction(r.choice([25, 30, 35, 40, 45, 55, 60, 65, 70]), 100)
    defect1, defect2 = Fraction(r.randint(1, 5), 100), Fraction(r.randint(1, 5), 100)
    value = share * defect1 + (1 - share) * defect2
    return task(
        f"Две фабрики выпускают одинаковые стёкла для автомобильных фар. Первая фабрика выпускает {dec(share * 100)}% этих стёкол, вторая {dec((1 - share) * 100)}%. "
        f"Первая фабрика выпускает {dec(defect1 * 100)}% бракованных стёкол, а вторая {dec(defect2 * 100)}%. "
        "Найдите вероятность того, что случайно купленное в магазине стекло окажется бракованным.",
        dec(value),
        f"{dec(share)} · {dec(defect1)} + {dec(1 - share)} · {dec(defect2)} = {dec(value)}.",
    )


def c_lamps(r):
    burn = Fraction(r.choice([1, 2, 3, 4]), 10)
    lamps = r.choice([2, 3])
    value = 1 - burn**lamps
    return task(
        f"Помещение освещается фонарём с {'двумя' if lamps == 2 else 'тремя'} лампами. Вероятность перегорания одной лампы в течение года равна {dec(burn)}. "
        "Найдите вероятность того, что в течение года хотя бы одна лампа не перегорит.",
        dec(value),
        f"Все лампы перегорят с вероятностью {dec(burn)}{sup(lamps)} = {dec(burn ** lamps)}. Искомая вероятность равна 1 - {dec(burn ** lamps)} = {dec(value)}.",
    )


def c_chess(r):
    white = Fraction(r.choice([50, 52, 55, 60, 62]), 100)
    black = Fraction(r.choice([30, 32, 34, 40, 45]), 100)
    return task(
        f"Если шахматист А. играет белыми фигурами, то он выигрывает у шахматиста Б. с вероятностью {dec(white)}. Если А. играет чёрными, то А. выигрывает у Б. "
        f"с вероятностью {dec(black)}. Шахматисты А. и Б. играют две партии, причём во второй партии меняют цвет фигур. Найдите вероятность того, что А. выиграет оба раза.",
        dec(white * black),
        f"Партии независимы: {dec(white)} · {dec(black)} = {dec(white * black)}.",
    )


def c_kettle(r):
    item = r.choice(["электрический чайник", "ноутбук", "сканер", "телевизор"])
    more_one = Fraction(r.randint(90, 98), 100)
    more_two = more_one - Fraction(r.randint(4, 15), 100)
    return task(
        f"Вероятность того, что новый {item} прослужит больше года, равна {dec(more_one)}. Вероятность того, что он прослужит больше двух лет, равна {dec(more_two)}. "
        "Найдите вероятность того, что он прослужит меньше двух лет, но больше года.",
        dec(more_one - more_two),
        f"{dec(more_one)} - {dec(more_two)} = {dec(more_one - more_two)}.",
    )


def c_artillery(r):
    first = Fraction(r.choice([3, 4, 5]), 10)
    following = Fraction(r.choice([6, 7, 8]), 10)
    target = Fraction(r.choice([95, 96, 98, 99]), 100)
    miss, shots = 1 - first, 1
    while 1 - miss < target:
        miss *= 1 - following
        shots += 1
    return task(
        "При артиллерийской стрельбе автоматическая система делает выстрел по цели. Если цель не уничтожена, то система делает повторный выстрел. "
        f"Выстрелы повторяются до тех пор, пока цель не будет уничтожена. Вероятность уничтожения некоторой цели при первом выстреле равна {dec(first)}, "
        f"а при каждом последующем {dec(following)}. Сколько выстрелов потребуется для того, чтобы вероятность уничтожения цели была не менее {dec(target)}?",
        dec(shots),
        f"Вероятность промаха после каждого выстрела умножается: сначала на {dec(1 - first)}, затем на {dec(1 - following)}. "
        f"После {shots} выстрелов вероятность уничтожения впервые не меньше {dec(target)}.",
    )


def c_test(r):
    sick = Fraction(r.choice([2, 4, 5, 8, 10]), 100)
    true_positive = Fraction(r.choice([8, 9]), 10)
    false_positive = Fraction(r.choice([1, 2]), 100)
    value = sick * true_positive + (1 - sick) * false_positive
    return task(
        "Всем пациентам с подозрением на гепатит делают анализ крови. Если анализ выявляет гепатит, то результат анализа называется положительным. "
        f"У больных гепатитом пациентов анализ даёт положительный результат с вероятностью {dec(true_positive)}. Если пациент не болен гепатитом, "
        f"то анализ может дать ложный положительный результат с вероятностью {dec(false_positive)}. Известно, что {dec(sick * 100)}% пациентов, поступающих с подозрением на гепатит, "
        "действительно больны гепатитом. Найдите вероятность того, что результат анализа у пациента, поступившего в клинику с подозрением на гепатит, будет положительным.",
        dec(value),
        f"{dec(sick)} · {dec(true_positive)} + {dec(1 - sick)} · {dec(false_positive)} = {dec(value)}.",
    )


def c_exam(r):
    math_p, rus_p = Fraction(r.choice([6, 7, 8]), 10), Fraction(r.choice([7, 8, 9]), 10)
    foreign, social = Fraction(r.choice([5, 6, 7]), 10), Fraction(r.choice([5, 6, 8]), 10)
    value = math_p * rus_p * (1 - (1 - foreign) * (1 - social))
    return task(
        "Чтобы поступить в институт на специальность «Лингвистика», абитуриент должен набрать на ЕГЭ не менее 70 баллов по каждому из трёх предметов: математике, русскому языку "
        "и иностранному языку. Чтобы поступить на специальность «Коммерция», нужно набрать не менее 70 баллов по каждому из трёх предметов: математике, русскому языку и обществознанию. "
        f"Вероятность того, что абитуриент З. получит не менее 70 баллов по математике, равна {dec(math_p)}, по русскому языку {dec(rus_p)}, "
        f"по иностранному языку {dec(foreign)} и по обществознанию {dec(social)}. Найдите вероятность того, что З. сможет поступить хотя бы на одну из двух упомянутых специальностей.",
        dec(value),
        f"Нужны математика, русский и хотя бы один из двух оставшихся предметов: {dec(math_p)} · {dec(rus_p)} · (1 - {dec(1 - foreign)} · {dec(1 - social)}) = {dec(value)}.",
    )


# ---------------------------------------------------------------- №6 Статистика: математическое ожидание


def st_table(r):
    while True:
        values = sorted(r.sample(range(-5, 9), 4))
        weights = [r.randint(1, 5) for _ in range(4)]
        if sum(weights) == 10:
            break
    probabilities = [Fraction(w, 10) for w in weights]
    expectation = sum(v * p for v, p in zip(values, probabilities))
    fig = table_figure([["Значения X"] + [dec(v) for v in values], ["Вероятности"] + [dec(p) for p in probabilities]])
    return task(
        "В таблице показано распределение случайной величины X. Найдите математическое ожидание этой случайной величины.",
        dec(expectation),
        "E(X) = " + " + ".join(f"({dec(v)}) · {dec(p)}" for v, p in zip(values, probabilities)) + f" = {dec(expectation)}.",
        fig,
    )


def st_lottery(r):
    total = 1000
    while True:
        prizes = [r.choice([100, 200, 500, 1000, 2000, 5000]) for _ in range(3)]
        counts = [r.choice([1, 2, 5, 10, 20, 50]) for _ in range(3)]
        if len(set(prizes)) == 3:
            break
    prizes.sort(reverse=True)
    counts.sort()
    expectation = Fraction(sum(p * c for p, c in zip(prizes, counts)), total)
    price = int(expectation) + r.choice([10, 20, 30, 50])
    price -= price % 10
    if price <= expectation:
        price += 50
    fig = table_figure([["Выигрыш, руб."] + [str(p) for p in prizes], ["Число билетов"] + [str(c) for c in counts]])
    return task(
        f"В таблице показаны количество выигрышных билетов и размеры выигрышей денежной лотереи. Остальные билеты без выигрыша. Цена билета равна {price} рублей, "
        f"всего выпущено {total} билетов. Участник покупает один случайный билет. На сколько рублей цена билета выше, чем математическое ожидание выигрыша?",
        dec(price - expectation),
        f"Математическое ожидание выигрыша равно ({' + '.join(f'{p} · {c}' for p, c in zip(prizes, counts))}) : {total} = {dec(expectation)} руб. Разность равна {dec(price - expectation)}.",
        fig,
    )


def st_until(r):
    if r.random() < 0.5:
        times = r.choice([2, 3, 4, 5])
        word = {2: "два раза", 3: "три раза", 4: "четыре раза", 5: "пять раз"}[times]
        return task(
            f"Монету подбрасывают до тех пор, пока орёл не выпадет {word} (не обязательно подряд). Найдите математическое ожидание числа бросков.",
            dec(2 * times),
            f"До каждого очередного орла в среднем нужно 1 : 0,5 = 2 броска, всего {times} · 2 = {2 * times}.",
        )
    times = r.choice([1, 2, 3])
    word = {1: "один раз", 2: "два раза", 3: "три раза"}[times]
    return task(
        f"Игральную кость бросают до тех пор, пока шестёрка не выпадет {word}. Найдите математическое ожидание числа бросков.",
        dec(6 * times),
        f"До каждой очередной шестёрки в среднем нужно 1 : (1/6) = 6 бросков, всего {6 * times}.",
    )


def st_binomial(r):
    shots = r.randint(5, 40)
    hit = Fraction(r.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]), 10)
    who, what = r.choice([("Стрелок делает", "попаданий"), ("Баскетболист выполняет", "попаданий"), ("Автомат изготавливает", "бракованных деталей")])
    if what == "бракованных деталей":
        hit = Fraction(r.choice([1, 2, 5]), 100)
        shots = r.choice([100, 200, 300, 400, 500])
        return task(
            f"Автомат изготавливает {shots} деталей. Вероятность того, что деталь окажется бракованной, равна {dec(hit)}. "
            "Найдите математическое ожидание числа бракованных деталей.",
            dec(shots * hit),
            f"E = n · p = {shots} · {dec(hit)} = {dec(shots * hit)}.",
        )
    return task(
        f"{who} {shots} бросков по цели. Вероятность попадания при каждом броске равна {dec(hit)}. Найдите математическое ожидание числа {what}.",
        dec(shots * hit),
        f"E = n · p = {shots} · {dec(hit)} = {dec(shots * hit)}.",
    )


def st_dice(r):
    dice = r.choice([2, 3, 4, 5, 6, 7, 8, 10, 12, 20])
    words = {2: "две игральные кости", 3: "три игральные кости", 4: "четыре игральные кости"}
    return task(
        f"Одновременно бросают {words.get(dice, str(dice) + ' игральных костей')}. Найдите математическое ожидание суммы выпавших очков.",
        dec(Fraction(7 * dice, 2)),
        f"Для одной кости математическое ожидание равно (1 + 2 + 3 + 4 + 5 + 6) : 6 = 3,5; для {dice} костей {dec(Fraction(7 * dice, 2))}.",
    )


def st_game(r):
    win = 6 * r.randint(2, 20)
    lose = 6 * r.randint(1, 5)
    faces = r.choice([1, 2, 3])
    names = {1: "шесть очков", 2: "пять или шесть очков", 3: "чётное число очков"}
    expectation = Fraction(faces * win - (6 - faces) * lose, 6)
    return task(
        f"Игрок бросает игральную кость. Если выпадает {names[faces]}, игрок получает {win} рублей, в остальных случаях он платит {lose} рублей. "
        "Найдите математическое ожидание выигрыша игрока за один бросок. Если игрок в среднем проигрывает, запишите ответ со знаком минус.",
        dec(expectation),
        f"E = {win} · {faces}/6 - {lose} · {6 - faces}/6 = {dec(expectation)}.",
    )


# ---------------------------------------------------------------- №7 Простейшие уравнения


def e_rational(r):
    while True:
        x = r.randint(-20, 20)
        a = r.randint(-20, 20)
        k = r.choice([n for n in range(-6, 7) if n not in (0, 1)])
        # (x + b) / (x + a) = k
        if x + a == 0:
            continue
        b = k * (x + a) - x
        if abs(b) <= 150 and b != a:
            break
    return task(
        f"Найдите корень уравнения ({poly([(1, 'x'), (b, '')])}) : ({poly([(1, 'x'), (a, '')])}) = {k}.",
        dec(x),
        f"{poly([(1, 'x'), (b, '')])} = {k} · ({poly([(1, 'x'), (a, '')])}), откуда x = {x}.",
    )


def e_quadratic(r):
    x1, x2 = sorted(r.sample(range(-12, 13), 2))
    which = r.choice(["меньший", "больший"])
    return task(
        f"Решите уравнение {poly([(1, 'x²'), (-(x1 + x2), 'x'), (x1 * x2, '')])} = 0. Если уравнение имеет более одного корня, в ответе запишите {which} из корней.",
        dec(x1 if which == "меньший" else x2),
        f"Корни уравнения: {x1} и {x2}.",
    )


def e_irrational(r):
    if r.random() < 0.5:
        while True:
            a = r.choice([n for n in range(-9, 10) if n != 0])
            c = r.randint(2, 11)
            x = r.randint(-20, 20)
            b = c * c - a * x
            if abs(b) <= 200:
                break
        return task(
            f"Найдите корень уравнения √({poly([(a, 'x'), (b, '')])}) = {c}.",
            dec(x),
            f"Возводим в квадрат: {poly([(a, 'x'), (b, '')])} = {c * c}, откуда x = {x}.",
        )
    # √(p - qx) = -x, корни x² + qx - p = 0, подходит неположительный
    x1 = -r.randint(1, 12)
    x2 = r.randint(1, 12)
    q, p = -(x1 + x2), -x1 * x2  # x² - (x1+x2)x + x1x2 = 0  ->  x² + qx - p = 0
    return task(
        f"Найдите корень уравнения √({poly([(p, ''), (-q, 'x')])}) = -x. Если уравнение имеет более одного корня, в ответе запишите меньший из корней.",
        dec(x1),
        f"Возводим в квадрат: x² {signed(q)}x {signed(-p)} = 0, корни {x1} и {x2}. Правая часть должна быть неотрицательной, поэтому подходит только x = {x1}.",
    )


def e_exponential(r):
    base = r.choice([2, 3, 5, 7])
    power = r.randint(2, 5 if base == 2 else 3)
    kind = r.choice(["plain", "inverse", "square"])
    a = r.choice([n for n in range(-8, 9) if n != 0])
    if kind == "plain":
        k = r.choice([1, 2, -1, -2, 3])
        if (power - a) % k:
            k = 1
        x = (power - a) // k
        return task(
            f"Найдите корень уравнения {base}{sup(poly([(k, 'x'), (a, '')]))} = {base ** power}.",
            dec(x),
            f"{base ** power} = {base}{sup(power)}, поэтому {poly([(k, 'x'), (a, '')])} = {power}, x = {x}.",
        )
    if kind == "inverse":
        x = a - power
        return task(
            f"Найдите корень уравнения (1/{base}){sup(poly([(1, 'x'), (-a, '')]))} = {base ** power}.",
            dec(x),
            f"(1/{base}){sup('x')} = {base}{sup('-x')}, поэтому -({poly([(1, 'x'), (-a, '')])}) = {power}, x = {x}.",
        )
    # (base²)^(x + a) = base^power
    if power % 2:
        power += 1
    x = Fraction(power, 2) - a
    return task(
        f"Найдите корень уравнения {base * base}{sup(poly([(1, 'x'), (a, '')]))} = {base ** power}.",
        dec(x),
        f"{base * base} = {base}², поэтому 2({poly([(1, 'x'), (a, '')])}) = {power}, x = {dec(x)}.",
    )


def e_logarithm(r):
    base = r.choice([2, 3, 4, 5])
    kind = r.choice(["plain", "double", "equal"])
    if kind == "plain":
        power = r.randint(2, 6 if base == 2 else 3)
        a = r.randint(-20, 30)
        sign = r.choice([1, -1])
        x = (base**power - a) * sign
        return task(
            f"Найдите корень уравнения log{sub(base)}({poly([(a, ''), (sign, 'x')])}) = {power}.",
            dec(x),
            f"{poly([(a, ''), (sign, 'x')])} = {base}{sup(power)} = {base ** power}, откуда x = {x}.",
        )
    if kind == "double":
        m = r.choice([2, 3, 4, 5, 6])
        a = r.randint(-10, 40)
        x = a - m * m
        return task(
            f"Найдите корень уравнения log{sub(base)}({poly([(a, ''), (-1, 'x')])}) = 2 · log{sub(base)} {m}.",
            dec(x),
            f"2 · log {m} = log {m * m}, поэтому {a} - x = {m * m}, x = {x}.",
        )
    while True:
        p, q = r.randint(2, 9), r.randint(1, 8)
        a, b = r.randint(-20, 20), r.randint(-20, 20)
        if p != q and (b - a) % (p - q) == 0:
            x = (b - a) // (p - q)
            if p * x + a > 0:
                break
    return task(
        f"Найдите корень уравнения log{sub(base)}({poly([(p, 'x'), (a, '')])}) = log{sub(base)}({poly([(q, 'x'), (b, '')])}).",
        dec(x),
        f"Аргументы равны: {poly([(p, 'x'), (a, '')])} = {poly([(q, 'x'), (b, '')])}, x = {x}; при этом аргумент положителен.",
    )


def e_trigonometric(r):
    # Перебором находим нужный корень уравнения вида cos(π(x + a)/n) = значение.
    function, n, value_text, angles = r.choice([
        ("cos", 3, "1/2", [1, -1]), ("cos", 6, "√3/2", [1, -1]), ("cos", 4, "√2/2", [1, -1]),
        ("sin", 6, "1/2", [1, 5]), ("sin", 3, "√3/2", [1, 2]), ("sin", 4, "√2/2", [1, 3]),
        ("tg", 4, "1", [1]), ("tg", 4, "-1", [-1]), ("tg", 3, "√3", [1]), ("tg", 6, "√3/3", [1]),
    ])
    a = r.randint(-9, 9)
    period = n if function == "tg" else 2 * n
    roots = sorted({angle + period * k - a for angle in angles for k in range(-12, 13)})
    which = r.choice(["наибольший отрицательный", "наименьший положительный"])
    answer = max(x for x in roots if x < 0) if which.startswith("наибольший") else min(x for x in roots if x > 0)
    argument = f"π({poly([(1, 'x'), (a, '')])})/{n}" if a else f"πx/{n}"
    return task(
        f"Решите уравнение {function} ({argument}) = {value_text}. В ответе запишите {which} корень.",
        dec(answer),
        f"Корни уравнения образуют серии с периодом {period}; {which} корень равен {answer}.",
    )


# ---------------------------------------------------------------- №8 Вычисления и преобразования


def t_powers(r):
    base = r.choice([2, 3, 5])
    kind = r.choice(["fraction", "product", "decimal"])
    if kind == "fraction":
        den = r.choice([2, 3, 4, 5])
        total = r.randint(1, 3)
        num1 = r.randint(1, den * total - 1)
        num2 = den * total - num1
        return task(
            f"Найдите значение выражения {base}^({num1}/{den}) · {base}^({num2}/{den}). Знак ^ означает возведение в степень.",
            dec(base**total),
            f"При умножении показатели складываются: {num1}/{den} + {num2}/{den} = {total}, {base}{sup(total)} = {base ** total}.",
        )
    if kind == "product":
        m, n = r.randint(2, 6), r.randint(2, 6)
        other = r.choice([b for b in (2, 3, 5, 7) if b != base])
        low = min(m, n)
        value = Fraction(base**m * other**n, (base * other) ** low)
        return task(
            f"Найдите значение выражения ({base}{sup(m)} · {other}{sup(n)}) : {base * other}{sup(low)}.",
            dec(value),
            f"{base * other}{sup(low)} = {base}{sup(low)} · {other}{sup(low)}; остаётся {base}{sup(m - low)} · {other}{sup(n - low)} = {dec(value)}.",
        )
    a = r.randint(4, 15)
    x1 = Fraction(r.randint(100, 900), 100)
    x2 = Fraction(r.randint(100, 900), 100)
    x3 = x1 + x2 - 2
    return task(
        f"Найдите значение выражения a^({dec(x1)}) · a^({dec(x2)}) : a^({dec(x3)}) при a = {a}. Знак ^ означает возведение в степень.",
        dec(a * a),
        f"Показатель степени равен {dec(x1)} + {dec(x2)} - {dec(x3)} = 2, значение равно {a}² = {a * a}.",
    )


def t_roots(r):
    kind = r.choice(["conjugate", "difference", "product"])
    if kind == "conjugate":
        a, b = sorted(r.sample([2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 23], 2), reverse=True)
        return task(
            f"Найдите значение выражения (√{a} - √{b})(√{a} + √{b}).",
            dec(a - b),
            f"По формуле разности квадратов: {a} - {b} = {a - b}.",
        )
    if kind == "difference":
        small, big, hyp = r.choice([(33, 56, 65), (5, 12, 13), (7, 24, 25), (9, 40, 41), (15, 8, 17), (20, 21, 29), (12, 35, 37), (11, 60, 61), (16, 63, 65)])
        return task(
            f"Найдите значение выражения √({hyp}² - {big}²).",
            dec(small),
            f"{hyp}² - {big}² = ({hyp} - {big})({hyp} + {big}) = {(hyp - big) * (hyp + big)}, корень равен {small}.",
        )
    k = r.randint(2, 9)
    a = r.choice([2, 3, 5, 6, 7])
    m = r.choice([2, 3, 4, 5])
    return task(
        f"Найдите значение выражения {k}√{a * m * m} · √{a}.",
        dec(k * a * m),
        f"√{a * m * m} · √{a} = √{a * a * m * m} = {a * m}, значение равно {k} · {a * m} = {k * a * m}.",
    )


def t_logs(r):
    base = r.choice([2, 3, 5, 6, 7])
    kind = r.choice(["difference", "sum", "identity", "product", "fractional"])
    if kind == "difference":
        power = r.randint(1, 3)
        b = r.choice([n for n in (2, 3, 4, 5, 6, 7, 12) if n % base])
        return task(
            f"Найдите значение выражения log{sub(base)} {b * base ** power} - log{sub(base)} {b}.",
            dec(power),
            f"Разность логарифмов равна логарифму частного: log{sub(base)} {base ** power} = {power}.",
        )
    if kind == "sum":
        power = r.randint(2, 3)
        number = base**power
        second = r.choice([4, 5, 8, 10, 20, 25])
        first = Fraction(number, second)
        return task(
            f"Найдите значение выражения log{sub(base)} {dec(first)} + log{sub(base)} {second}.",
            dec(power),
            f"Сумма логарифмов равна логарифму произведения: log{sub(base)} {number} = {power}.",
        )
    if kind == "identity":
        value = r.randint(2, 40)
        multiplier = r.randint(2, 9)
        return task(
            f"Найдите значение выражения {multiplier} · {base}^(log{sub(base)} {value}). Знак ^ означает возведение в степень.",
            dec(multiplier * value),
            f"По основному логарифмическому тождеству {base}^(log{sub(base)} {value}) = {value}; ответ {multiplier * value}.",
        )
    if kind == "product":
        other = r.choice([b for b in (2, 3, 5, 6) if b != base])
        m, n = r.randint(2, 4), r.randint(2, 3)
        return task(
            f"Найдите значение выражения (log{sub(base)} {base ** m}) · (log{sub(other)} {other ** n}).",
            dec(m * n),
            f"log{sub(base)} {base ** m} = {m}, log{sub(other)} {other ** n} = {n}, произведение равно {m * n}.",
        )
    small = r.choice([2, 3])
    m, n = r.choice([(2, 1), (2, 3), (2, 5), (4, 1), (4, 2), (4, 3), (4, 6), (5, 2), (5, 3), (2, 4), (4, 5)])
    return task(
        f"Найдите значение выражения log{sub(small ** m)} {small ** n}.",
        dec(Fraction(n, m)),
        f"{small ** n} = {small}{sup(n)}, {small ** m} = {small}{sup(m)}, логарифм равен {n} : {m} = {dec(Fraction(n, m))}.",
    )


def t_trig(r):
    kind = r.choice(["find_cos", "double", "squares", "tangent"])
    if kind == "find_cos":
        sine, cosine = r.choice([(Fraction(3, 5), Fraction(4, 5)), (Fraction(4, 5), Fraction(3, 5)), (Fraction(7, 25), Fraction(24, 25)), (Fraction(24, 25), Fraction(7, 25))])
        quarter, sin_sign, cos_sign = r.choice([("(π/2; π)", 1, -1), ("(π; 3π/2)", -1, -1), ("(3π/2; 2π)", -1, 1), ("(0; π/2)", 1, 1)])
        k = r.choice([5, 10, 25, 50])
        return task(
            f"Найдите {k}cos α, если sin α = {dec(sine * sin_sign)} и α ∈ {quarter}.",
            dec(k * cosine * cos_sign),
            f"cos²α = 1 - sin²α = {dec(cosine * cosine)}; в этой четверти косинус {'положителен' if cos_sign > 0 else 'отрицателен'}: cos α = {dec(cosine * cos_sign)}.",
        )
    if kind == "double":
        k = r.choice([2, 4, 6, 8, 10, 12])
        argument, sine = r.choice([("π/12", Fraction(1, 2)), ("5π/12", Fraction(1, 2)), ("7π/12", Fraction(-1, 2)), ("11π/12", Fraction(-1, 2))])
        return task(
            f"Найдите значение выражения {k} sin ({argument}) · cos ({argument}).",
            dec(Fraction(k, 2) * sine),
            f"2 sin x cos x = sin 2x. Здесь sin 2x = {dec(sine)}, значение равно {dec(Fraction(k, 2))} · ({dec(sine)}) = {dec(Fraction(k, 2) * sine)}.",
        )
    if kind == "squares":
        k = r.choice([2, 4, 6, 8, 10, 14])
        argument, cosine = r.choice([("π/6", Fraction(1, 2)), ("π/3", Fraction(-1, 2)), ("5π/6", Fraction(1, 2)), ("2π/3", Fraction(-1, 2))])
        return task(
            f"Найдите значение выражения {k}cos²({argument}) - {k}sin²({argument}).",
            dec(k * cosine),
            f"cos²x - sin²x = cos 2x = {dec(cosine)}, значение равно {dec(k * cosine)}.",
        )
    leg, other, hyp = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)])
    tangent = Fraction(other, leg)
    if not is_finite_decimal(tangent):
        tangent, leg, other = Fraction(leg, other), other, leg
    if not is_finite_decimal(tangent):
        return t_trig(r)
    quarter, sign = r.choice([("(0; π/2)", 1), ("(3π/2; 2π)", -1)])
    return task(
        f"Найдите tg α, если cos α = {leg}/{hyp} и α ∈ {quarter}.",
        dec(tangent * sign),
        f"sin²α = 1 - cos²α = {other * other}/{hyp * hyp}; sin α = {'' if sign > 0 else '-'}{other}/{hyp}, tg α = sin α : cos α = {dec(tangent * sign)}.",
    )


# ---------------------------------------------------------------- №9 Производная и первообразная


def d_physical(r):
    a = r.choice([1, 2, 3, 4, 6])  # x(t) = (a/3)t³ - b t² + c t + d
    b = r.randint(1, 6)
    c = r.randint(-9, 12)
    d = r.randint(0, 20)
    t0 = r.randint(2, 9)

    def speed(t):
        return a * t * t - 2 * b * t + c

    cubic = "t³" if a == 3 else f"{frac(Fraction(a, 3))}t³"
    tail = poly([(-b, "t²"), (c, "t"), (d, "")])
    law = f"x(t) = {cubic} " + (f"- {tail[1:]}" if tail.startswith("-") else f"+ {tail}")
    if r.random() < 0.5:
        return task(
            f"Материальная точка движется прямолинейно по закону {law}, где x это расстояние от точки отсчёта в метрах, t это время в секундах, "
            f"измеренное с начала движения. Найдите её скорость (в метрах в секунду) в момент времени t = {t0} с.",
            dec(speed(t0)),
            f"v(t) = x'(t) = {a}t² - {2 * b}t {signed(c)}; v({t0}) = {speed(t0)}.",
        )
    target = speed(t0)
    roots = [t for t in range(0, 40) if speed(t) == target]
    if len(roots) != 1 or target <= 0:
        return d_physical(r)
    return task(
        f"Материальная точка движется прямолинейно по закону {law}, где x это расстояние от точки отсчёта в метрах, t это время в секундах, "
        f"измеренное с начала движения. В какой момент времени (в секундах) её скорость была равна {target} м/с?",
        dec(t0),
        f"v(t) = {a}t² - {2 * b}t {signed(c)} = {target}; подходит неотрицательный корень t = {t0}.",
    )


def d_parallel(r):
    a = r.choice([1, 2, -1, -2, 4])
    b = r.randint(-9, 9)
    c = r.randint(-9, 9)
    x0 = Fraction(r.randint(-12, 12), 2)
    k = 2 * a * x0 + b
    if k.denominator != 1:
        return d_parallel(r)
    m = r.randint(-9, 9)
    return task(
        f"Прямая y = {poly([(k, 'x'), (m, '')])} параллельна касательной к графику функции y = {poly([(a, 'x²'), (b, 'x'), (c, '')])}. Найдите абсциссу точки касания.",
        dec(x0),
        f"Угловой коэффициент касательной равен производной: {poly([(2 * a, 'x'), (b, '')])} = {k}, откуда x = {dec(x0)}.",
    )


def d_tangent_coefficient(r):
    while True:
        x0 = r.choice([n for n in range(-6, 7) if n != 0])
        a = Fraction(r.choice([1, 2, 3, 4, 5, 6, 8, 10]), r.choice([1, 2, 4, 5, 8]))
        b = r.randint(-9, 9)
        c = r.randint(-9, 9)
        k = 2 * a * x0 + b
        m = a * x0 * x0 + b * x0 + c - k * x0
        if k.denominator == 1 and m.denominator == 1 and is_finite_decimal(a) and a.denominator != 1:
            break
    return task(
        f"Прямая y = {poly([(k, 'x'), (m, '')])} является касательной к графику функции y = ax² {signed(b)}x {signed(c)}. Найдите a.",
        dec(a),
        f"Уравнение ax² {signed(b - k)}x {signed(c - m)} = 0 должно иметь один корень: дискриминант равен нулю, откуда a = {dec(a)}.",
    )


def d_graph_tangent(r):
    while True:
        x0 = r.randint(-5, 5)
        y0 = r.randint(-3, 3)
        run = r.choice([1, 2, 4])
        rise = r.choice([n for n in range(-6, 7) if n != 0])
        slope = Fraction(rise, run)
        curvature = r.choice([-0.35, -0.25, 0.25, 0.35])
        x1, y1 = x0 + run, y0 + rise
        x2, y2 = x0 - run, y0 - rise
        plane = Plane()
        if plane.inside(x1, y1) and plane.inside(x2, y2) and abs(slope) <= 3:
            break
    plane.curve(lambda x: y0 + float(slope) * (x - x0) + curvature * (x - x0) ** 2, x0 - 6, x0 + 6, 70, 1)
    plane.line(float(slope), y0 - float(slope) * x0, 2)
    plane.mark(x0, y0)
    plane.mark(x1, y1)
    plane.mark(x2, y2)
    if y0 != 0:
        plane.tick(x0, "x₀")
    return task(
        "На рисунке изображены график функции y = f(x) (чёрная линия) и касательная к нему в точке с абсциссой x₀ (цветная линия). "
        "На касательной отмечены три точки с целыми координатами, средняя из них является точкой касания. Найдите значение производной функции f(x) в точке x₀.",
        dec(slope),
        f"Производная равна угловому коэффициенту касательной. При смещении на {run} вправо касательная поднимается на {rise}: k = {dec(slope)}.",
        plane.fig,
    )


def d_graph_derivative(r):
    # График производной проходит через нули в целых точках, знак чередуется.
    left, right = -9, 9
    zeros = sorted(r.sample(range(left + 2, right - 1), r.choice([3, 4, 5])))
    if any(b - a < 2 for a, b in zip(zeros, zeros[1:])):
        return d_graph_derivative(r)
    sign = r.choice([1, -1])
    nodes = [left] + zeros + [right]

    def derivative(x):
        for index in range(len(nodes) - 1):
            a, b = nodes[index], nodes[index + 1]
            if a <= x <= b:
                local_sign = sign * (-1) ** index
                height = min(3.5, 0.9 + 0.55 * (b - a))
                if index == 0:
                    return local_sign * height * math.sin(math.pi * (x - a + (b - a)) / (2 * (b - a)))
                if index == len(nodes) - 2:
                    return local_sign * height * math.sin(math.pi * (x - a) / (2 * (b - a)))
                return local_sign * height * math.sin(math.pi * (x - a) / (b - a))
        return 0

    plane = Plane()
    plane.curve(derivative, left, right, 90, 2)
    signs = [sign * (-1) ** index for index in range(len(nodes) - 1)]
    maxima = [zeros[i] for i in range(len(zeros)) if signs[i] > 0 and signs[i + 1] < 0]
    minima = [zeros[i] for i in range(len(zeros)) if signs[i] < 0 and signs[i + 1] > 0]
    kind = r.choice(["max_count", "min_count", "extremum_count", "max_point"])
    intro = f"На рисунке изображён график y = f'(x) производной функции f(x), определённой на интервале ({left}; {right}). "
    if kind == "max_count":
        return task(intro + "Найдите количество точек максимума функции f(x).", dec(len(maxima)),
                    f"В точке максимума производная меняет знак с плюса на минус. Таких точек {len(maxima)}.", plane.fig)
    if kind == "min_count":
        return task(intro + "Найдите количество точек минимума функции f(x).", dec(len(minima)),
                    f"В точке минимума производная меняет знак с минуса на плюс. Таких точек {len(minima)}.", plane.fig)
    if kind == "extremum_count":
        return task(intro + "Найдите количество точек экстремума функции f(x).", dec(len(zeros)),
                    f"В точках экстремума производная меняет знак. График пересекает ось абсцисс {len(zeros)} раз.", plane.fig)
    if len(maxima) != 1:
        return d_graph_derivative(r)
    return task(intro + "Найдите точку максимума функции f(x).", dec(maxima[0]),
                f"Производная меняет знак с плюса на минус в точке x = {maxima[0]}.", plane.fig)


def d_graph_points(r):
    phase = r.uniform(0, 6.28)
    period = r.uniform(5.5, 8.5)
    amplitude = r.uniform(2.2, 3.4)

    def f(x):
        return amplitude * math.sin(2 * math.pi * x / period + phase) + 0.25 * math.sin(x * 1.7 + phase)

    def slope(x):
        return (f(x + 0.01) - f(x - 0.01)) / 0.02

    candidates = [x / 2 for x in range(-17, 18) if abs(slope(x / 2)) > 0.5]
    if len(candidates) < 7:
        return d_graph_points(r)
    points = sorted(r.sample(candidates, 7))
    plane = Plane(labels=False)
    plane.curve(f, -9.5, 9.5, 100, 1)
    for index, x in enumerate(points, start=1):
        plane.fig.line(*plane.px(x, 0), *plane.px(x, f(x)), 0)
        plane.fig.circle(*plane.px(x, f(x)), 3.5, 2)
        plane.fig.text(plane.px(x, 0)[0], plane.px(x, 0)[1] + (11 if f(x) > 0 else -11), f"x{sub(index)}")
    negative = sum(1 for x in points if slope(x) < 0)
    if r.random() < 0.5:
        question, answer = "В скольких из этих точек производная функции f(x) отрицательна?", negative
        how = f"Производная отрицательна там, где функция убывает. Таких точек {negative}."
    else:
        question, answer = "В скольких из этих точек производная функции f(x) положительна?", 7 - negative
        how = f"Производная положительна там, где функция возрастает. Таких точек {7 - negative}."
    return task(
        "На рисунке изображён график функции y = f(x). На оси абсцисс отмечены семь точек: x₁, x₂, x₃, x₄, x₅, x₆, x₇. " + question,
        dec(answer),
        how,
        plane.fig,
    )


# ---------------------------------------------------------------- №10 Задачи с прикладным содержанием


def a_ball(r):
    t1 = Fraction(r.randint(1, 8), 5)
    t2 = t1 + Fraction(r.randint(2, 12), 5)
    level = Fraction(r.randint(2, 8))
    # h(t) - level = -5(t - t1)(t - t2)
    v = 5 * (t1 + t2)
    h0 = level - 5 * t1 * t2
    if h0 < 0 or not is_finite_decimal(h0):
        return a_ball(r)
    return task(
        f"Высота над землёй подброшенного вверх мяча меняется по закону h(t) = {dec(h0)} + {dec(v)}t - 5t², где h это высота в метрах, t это время в секундах, "
        f"прошедшее с момента броска. Сколько секунд мяч будет находиться на высоте не менее {dec(level)} метров?",
        dec(t2 - t1),
        f"Неравенство {dec(h0)} + {dec(v)}t - 5t² ≥ {dec(level)} выполняется при t от {dec(t1)} до {dec(t2)}: это {dec(t2 - t1)} с.",
    )


def a_ohm(r):
    percent, factor = r.choice([(20, 4), (25, 3), (10, 9), (5, 19), (50, 1), (40, Fraction(3, 2)), (4, 24)])
    resistance = r.choice([1, 2, 4, 5, 10]) if factor != Fraction(3, 2) else r.choice([2, 4, 10])
    return task(
        "В розетку электросети подключены приборы. Сила тока в цепи определяется формулой I = ε : (R + r), где ε это ЭДС источника (в вольтах), "
        f"r = {resistance} Ом это его внутреннее сопротивление, R это сопротивление цепи (в омах). При каком наименьшем сопротивлении цепи сила тока будет составлять "
        f"не более {percent}% от силы тока короткого замыкания I = ε : r? Ответ дайте в омах.",
        dec(factor * resistance),
        f"ε : (R + r) ≤ {dec(Fraction(percent, 100))} · ε : r, откуда R + r ≥ {dec(Fraction(100, percent))}r и R ≥ {dec(factor)}r = {dec(factor * resistance)} Ом.",
    )


def a_horizon(r):
    distance = r.choice([4, 8, 16, 24, 32, 40, 48, 64])
    height = Fraction(500 * distance * distance, 6400)
    return task(
        "Расстояние от наблюдателя, находящегося на небольшой высоте h метров над землёй, до наблюдаемой им линии горизонта вычисляется по формуле "
        f"l = √(R · h : 500), где R = 6400 км это радиус Земли, l выражено в километрах. С какой высоты горизонт виден на расстоянии {distance} километров? Ответ дайте в метрах.",
        dec(height),
        f"l² = R · h : 500, откуда h = 500 · {distance}² : 6400 = {dec(height)} м.",
    )


def a_decay(r):
    half_life = r.choice([2, 3, 5, 7, 8, 10, 12, 15])
    halvings = r.randint(2, 5)
    final = r.choice([1, 2, 3, 5, 6, 10])
    start = final * 2**halvings
    return task(
        "Масса радиоактивного вещества уменьшается по закону m(t) = m₀ · 2^(-t/T), где m₀ это начальная масса, t это время в минутах, T это период полураспада "
        f"(в минутах). В начальный момент масса изотопа равна {start} мг, период его полураспада равен {half_life} мин. Через сколько минут масса изотопа будет равна {final} мг? "
        "Знак ^ означает возведение в степень.",
        dec(half_life * halvings),
        f"{start} : {final} = {2 ** halvings} = 2{sup(halvings)}, значит прошло {halvings} периодов полураспада: {half_life * halvings} мин.",
    )


def a_capacitor(r):
    alpha = Fraction(7, 10)
    resistance = r.choice([2, 3, 4, 5, 6, 8])
    capacity = r.choice([2, 3, 4, 5])
    power = r.choice([1, 2, 3, 4])
    final = r.choice([1, 2, 3, 4, 5])
    start = final * 2**power
    time = alpha * resistance * capacity * power
    return task(
        "Ёмкость высоковольтного конденсатора в телевизоре C = " + f"{capacity} · 10⁻⁶ Ф. Параллельно с конденсатором подключён резистор с сопротивлением R = {resistance} · 10⁶ Ом. "
        f"Во время работы телевизора напряжение на конденсаторе U₀ = {start} кВ. После выключения телевизора напряжение на конденсаторе убывает до значения U (кВ) за время, "
        f"определяемое выражением t = αRC · log₂ (U₀ : U) (с), где α = {dec(alpha)} это постоянная. Определите наибольшее возможное напряжение на конденсаторе, "
        f"если после выключения телевизора прошло не менее {dec(time)} с. Ответ дайте в киловольтах.",
        dec(final),
        f"αRC = {dec(alpha * resistance * capacity)} с, поэтому log₂ ({start} : U) ≥ {power}, {start} : U ≥ {2 ** power}, U ≤ {final} кВ.",
    )


def a_brake(r):
    acceleration = r.choice([2, 4, 5, 6])
    t = r.randint(1, 4)
    v0 = acceleration * (t + r.randint(1, 3))
    distance = Fraction(v0 * t) - Fraction(acceleration * t * t, 2)
    return task(
        f"Автомобиль, движущийся в начальный момент времени со скоростью v₀ = {v0} м/с, начал торможение с постоянным ускорением a = {acceleration} м/с². "
        "За t секунд после начала торможения он прошёл путь S = v₀t - at² : 2 (м). Определите время, прошедшее от момента начала торможения, "
        f"если известно, что за это время автомобиль проехал {dec(distance)} метров. Ответ выразите в секундах.",
        dec(t),
        f"{v0}t - {dec(Fraction(acceleration, 2))}t² = {dec(distance)}; меньший корень t = {t} с (больший соответствует времени после остановки).",
    )


def a_flight(r):
    v0 = r.choice([10, 12, 14, 16, 20, 24, 30])
    time = Fraction(v0, 10)
    return task(
        "Мяч бросили под углом α к плоской горизонтальной поверхности земли. Время полёта мяча (в секундах) определяется по формуле t = 2v₀ · sin α : g. "
        f"При каком наименьшем значении угла α (в градусах) время полёта будет не меньше {dec(time)} секунды, если мяч бросают с начальной скоростью v₀ = {v0} м/с? "
        "Считайте, что ускорение свободного падения g = 10 м/с².",
        "30",
        f"2 · {v0} · sin α : 10 ≥ {dec(time)}, откуда sin α ≥ 0,5; наименьший угол равен 30°.",
    )


def a_heater(r):
    t0 = r.choice([1300, 1350, 1400, 1450])
    a_coef = r.choice([-5, -10, -15])
    t1 = r.randint(2, 6)
    t2 = t1 + r.randint(4, 20)
    b_coef = -a_coef * (t1 + t2)
    limit = t0 - a_coef * t1 * t2
    return task(
        "Зависимость температуры (в градусах Кельвина) от времени для нагревательного элемента некоторого прибора была получена экспериментально: "
        f"T(t) = T₀ + bt + at², где t это время в минутах, T₀ = {t0} К, a = {a_coef} К/мин², b = {b_coef} К/мин. Известно, что при температуре нагревательного элемента свыше "
        f"{limit} К прибор может испортиться, поэтому его нужно отключить. Найдите, через какое наибольшее время после начала работы нужно отключить прибор. Ответ дайте в минутах.",
        dec(t1),
        f"T(t) = {limit} при t = {t1} и t = {t2}. Температура впервые достигает предела через {t1} мин, к этому моменту прибор нужно отключить.",
    )


# ---------------------------------------------------------------- №11 Текстовые задачи


def w_boat(r):
    while True:
        boat, current = r.randint(8, 30), r.randint(1, 6)
        if boat <= current + 2:
            continue
        up, down = boat - current, boat + current
        k = r.randint(1, 4)
        distance = k * up * down // math.gcd(up, down)
        difference = Fraction(distance, up) - Fraction(distance, down)
        if distance <= 400 and difference.denominator == 1 and difference >= 1:
            break
    if r.random() < 0.5:
        return task(
            f"Моторная лодка прошла против течения реки {distance} км и вернулась в пункт отправления, затратив на обратный путь на {difference} ч меньше. "
            f"Найдите скорость течения, если скорость лодки в неподвижной воде равна {boat} км/ч. Ответ дайте в км/ч.",
            dec(current),
            f"{distance} : ({boat} - x) - {distance} : ({boat} + x) = {difference}; подходит x = {current}.",
        )
    return task(
        f"Моторная лодка прошла против течения реки {distance} км и вернулась в пункт отправления, затратив на обратный путь на {difference} ч меньше. "
        f"Найдите скорость лодки в неподвижной воде, если скорость течения равна {current} км/ч. Ответ дайте в км/ч.",
        dec(boat),
        f"{distance} : (x - {current}) - {distance} : (x + {current}) = {difference}; подходит x = {boat}.",
    )


def w_half_way(r):
    options = [(v, d, v * (v + d) // (v + 2 * d)) for v in range(20, 100) for d in range(4, 60) if (v * (v + d)) % (v + 2 * d) == 0]
    v, d, a = r.choice([o for o in options if o[2] != o[0] and o[2] >= 15])
    return task(
        "Из пункта A в пункт B одновременно выехали два автомобиля. Первый проехал с постоянной скоростью весь путь. Второй проехал первую половину пути "
        f"со скоростью {a} км/ч, а вторую половину пути со скоростью, на {d} км/ч большей скорости первого, в результате чего прибыл в пункт B одновременно с первым автомобилем. "
        "Найдите скорость первого автомобиля. Ответ дайте в км/ч.",
        dec(v),
        f"1 : x = 1 : (2 · {a}) + 1 : (2(x + {d})); положительный корень x = {v}.",
    )


def w_cyclist(r):
    while True:
        v, d, stop = r.randint(6, 24), r.randint(1, 8), r.randint(1, 6)
        distance = Fraction(stop * v * (v + d), d)
        if distance.denominator == 1 and 30 <= distance <= 300:
            break
    return task(
        f"Велосипедист выехал с постоянной скоростью из города A в город B, расстояние между которыми равно {distance} км. На следующий день он отправился обратно в A "
        f"со скоростью на {d} км/ч больше прежней. По дороге он сделал остановку на {stop} ч. В результате велосипедист затратил на обратный путь столько же времени, "
        "сколько на путь из A в B. Найдите скорость велосипедиста на пути из A в B. Ответ дайте в км/ч.",
        dec(v),
        f"{distance} : x = {distance} : (x + {d}) + {stop}; положительный корень x = {v}.",
    )


def w_pipes(r):
    while True:
        x, d, delta = r.randint(5, 40), r.randint(1, 6), r.randint(1, 6)
        if x <= d:
            continue
        volume = Fraction(delta * x * (x - d), d)
        if volume.denominator == 1 and 60 <= volume <= 900:
            break
    if r.random() < 0.5:
        return task(
            f"Первая труба пропускает на {d} л воды в минуту меньше, чем вторая. Сколько литров воды в минуту пропускает вторая труба, если резервуар объёмом {volume} литров "
            f"она заполняет на {delta} мин быстрее, чем первая труба?",
            dec(x),
            f"{volume} : (x - {d}) - {volume} : x = {delta}; положительный корень x = {x}.",
        )
    return task(
        f"Заказ на {volume} деталей первый рабочий выполняет на {delta} ч быстрее, чем второй. Сколько деталей в час делает второй рабочий, если известно, "
        f"что первый за час делает на {d} детали больше?" if d < 5 else
        f"Заказ на {volume} деталей первый рабочий выполняет на {delta} ч быстрее, чем второй. Сколько деталей в час делает второй рабочий, если известно, "
        f"что первый за час делает на {d} деталей больше?",
        dec(x - d),
        f"{volume} : x - {volume} : (x + {d}) = {delta}; положительный корень x = {x - d}.",
    )


def w_alloy(r):
    while True:
        p1, p2 = sorted(r.sample(range(5, 60, 5), 2))
        p3 = r.randrange(p1 + 1, p2)
        mass = r.choice([100, 150, 200, 225, 250, 300])
        m1 = Fraction(mass * (p2 - p3), p2 - p1)
        if m1.denominator == 1 and m1 != mass - m1:
            break
    m2 = mass - m1
    metal = r.choice(["никеля", "меди", "олова", "цинка"])
    return task(
        f"Имеется два сплава. Первый содержит {p1}% {metal}, второй {p2}% {metal}. Из этих двух сплавов получили третий сплав массой {mass} кг, содержащий {p3}% {metal}. "
        "На сколько килограммов масса первого сплава была меньше массы второго? Если первый сплав тяжелее, запишите ответ со знаком минус.",
        dec(m2 - m1),
        f"Масса первого сплава {dec(m1)} кг, второго {dec(m2)} кг; разность равна {dec(m2 - m1)} кг.",
    )


def w_solution(r):
    kind = r.choice(["equal", "water"])
    if kind == "equal":
        p1, p2 = r.sample(range(5, 50), 2)
        if (p1 + p2) % 2:
            p2 += 1
        return task(
            f"Смешали некоторое количество {p1}-процентного раствора некоторого вещества с таким же количеством {p2}-процентного раствора этого вещества. "
            "Сколько процентов составляет концентрация получившегося раствора?",
            dec(Fraction(p1 + p2, 2)),
            f"При равных количествах концентрация равна среднему арифметическому: ({p1} + {p2}) : 2 = {dec(Fraction(p1 + p2, 2))}.",
        )
    while True:
        litres, percent, water = r.randint(2, 12), r.randrange(6, 40), r.randint(1, 12)
        value = Fraction(litres * percent, litres + water)
        if value.denominator == 1:
            break
    return task(
        f"В сосуд, содержащий {litres} л {percent}-процентного водного раствора некоторого вещества, добавили {water} л воды. "
        "Сколько процентов составляет концентрация получившегося раствора?",
        dec(value),
        f"Вещества {dec(Fraction(litres * percent, 100))} л на {litres + water} л раствора: {dec(value)}%.",
    )


def w_percent(r):
    people = r.choice([20000, 40000, 50000, 60000, 80000])
    first, second = r.choice([2, 4, 5, 8, 10]), r.choice([2, 5, 8, 9, 10])
    year = r.randint(2015, 2022)
    result = people * (100 + first) * (100 + second) // 10000
    return task(
        f"В {year} году в городском квартале проживало {people} человек. В {year + 1} году в результате строительства новых домов число жителей выросло на {first}%, "
        f"а в {year + 2} году на {second}% по сравнению с {year + 1} годом. Сколько человек стало проживать в квартале в {year + 2} году?",
        dec(result),
        f"{people} · {dec(Fraction(100 + first, 100))} · {dec(Fraction(100 + second, 100))} = {result}.",
    )


def w_progression(r):
    days = r.randint(5, 16)
    pair = 2 * r.randint(10, 60)
    total = pair * days // 2
    return task(
        f"Бригада маляров красит забор длиной {total} метров, ежедневно увеличивая норму покраски на одно и то же число метров. Известно, что за первый и последний день "
        f"в сумме бригада покрасила {pair} метров забора. Определите, сколько дней бригада маляров красила весь забор.",
        dec(days),
        f"Сумма арифметической прогрессии: {total} = {pair} · n : 2, откуда n = {days}.",
    )


def w_train(r):
    speed = r.choice([36, 54, 60, 72, 80, 90, 108])
    seconds = r.choice([18, 24, 27, 30, 36, 45, 48, 54])
    length = Fraction(speed * 1000 * seconds, 3600)
    if length.denominator != 1:
        return w_train(r)
    return task(
        f"Поезд, двигаясь равномерно со скоростью {speed} км/ч, проезжает мимо придорожного столба за {seconds} секунд. Найдите длину поезда в метрах.",
        dec(length),
        f"{speed} км/ч = {frac(Fraction(speed * 1000, 3600))} м/с; длина равна {frac(Fraction(speed * 1000, 3600))} · {seconds} = {dec(length)} м.",
    )


# ---------------------------------------------------------------- №12 Графики функций


def g_two_lines(r):
    while True:
        k1, k2 = r.sample([Fraction(n, d) for n in range(-4, 5) for d in (1, 2) if n != 0], 2)
        b1, b2 = r.randint(-4, 4), r.randint(-4, 4)
        if k1 == k2:
            continue
        x = Fraction(b2 - b1) / (k1 - k2)
        if abs(x) > 11 and abs(x) < 60 and is_finite_decimal(x):
            break
    plane = Plane()
    plane.line(float(k1), b1, 2)
    plane.line(float(k2), b2, 1)
    for k, b in ((k1, b1), (k2, b2)):
        points = [(px, k * px + b) for px in range(-9, 10) if (k * px + b).denominator == 1 and plane.inside(px, k * px + b)]
        for px, py in points[:1] + points[-1:]:
            plane.mark(px, py)
    return task(
        "На рисунке изображены графики двух линейных функций. На каждой прямой отмечены две точки с целыми координатами. Найдите абсциссу точки пересечения графиков.",
        dec(x),
        f"Уравнения прямых: y = {poly([(k1, 'x'), (b1, '')])} и y = {poly([(k2, 'x'), (b2, '')])}. Приравниваем и получаем x = {dec(x)}.",
        plane.fig,
    )


def g_parabola(r):
    a = r.choice([1, -1, 2, -2])
    m = r.randint(-5, 5)
    n = r.randint(-4, 2) if a > 0 else r.randint(-2, 4)
    plane = Plane()

    def f(x):
        return a * (x - m) ** 2 + n

    plane.curve(f, m - 4, m + 4, 80, 2)
    for x in (m - 1, m, m + 1):
        if plane.inside(x, f(x)):
            plane.mark(x, f(x))
    b, c = -2 * a * m, a * m * m + n
    kind = r.choice(["value", "c", "b"])
    if kind == "value":
        x0 = r.choice([n0 for n0 in (-12, -10, 10, 12, 15, -8) if abs(n0 - m) > 4])
        question, answer = f"Найдите f({x0}).", f(x0)
    elif kind == "c":
        question, answer = "Найдите c.", c
    else:
        question, answer = "Найдите b.", b
    return task(
        f"На рисунке изображён график функции f(x) = ax² + bx + c. На графике отмечены вершина параболы и две соседние точки с целыми координатами. {question}",
        dec(answer),
        f"Вершина параболы находится в точке ({m}; {n}), a = {a}: f(x) = {poly([(a, 'x²'), (b, 'x'), (c, '')])}.",
        plane.fig,
    )


def g_hyperbola(r):
    k = r.choice([-6, -4, -3, -2, 2, 3, 4, 6])
    a = r.randint(-3, 3)
    plane = Plane()

    def f(x):
        return k / x + a

    plane.curve(f, -10, -0.2, 70, 2)
    plane.curve(f, 0.2, 10, 70, 2)
    if a != 0:
        plane.fig.line(*plane.px(-10, a), *plane.px(10, a), 0)
    marked = [x for x in (-6, -4, -3, -2, -1, 1, 2, 3, 4, 6) if k % x == 0 and plane.inside(x, k // x + a)]
    for x in r.sample(marked, min(3, len(marked))):
        plane.mark(x, k // x + a)
    x0 = r.choice([10, -10, 20, -20, 25, 40, 50])
    return task(
        f"На рисунке изображён график функции f(x) = k/x + a. На графике отмечены точки с целыми координатами. Найдите f({x0}).",
        dec(Fraction(k, x0) + a),
        f"По отмеченным точкам k = {k}, a = {a}; f({x0}) = {k} : ({x0}) + ({a}) = {dec(Fraction(k, x0) + a)}.",
        plane.fig,
    )


def g_exponent(r):
    base = r.choice([2, 3, Fraction(1, 2)])
    b = r.randint(-5, 1)
    plane = Plane()

    def f(x):
        return float(base) ** x + b

    plane.curve(f, -10, 10, 110, 2)
    points = [x for x in range(-4, 5) if plane.inside(x, f(x)) and (Fraction(base) ** x).denominator == 1][:3]
    for x in points:
        plane.mark(x, f(x))
    if base == Fraction(1, 2):
        x0 = r.choice([-5, -6, -7])
        base_text = "1/2"
    else:
        x0 = r.choice([5, 6]) if base == 2 else r.choice([4, 5])
        base_text = str(base)
    value = Fraction(base) ** x0 + b
    return task(
        f"На рисунке изображён график функции f(x) = aˣ + b. На графике отмечены точки с целыми координатами. Найдите f({x0}).",
        dec(value),
        f"По отмеченным точкам a = {base_text}, b = {b}; f({x0}) = {dec(Fraction(base) ** x0)} + ({b}) = {dec(value)}.",
        plane.fig,
    )


def g_logarithm(r):
    base = r.choice([2, 3])
    b = r.randint(-3, 3)
    plane = Plane(x_min=-2, x_max=18, y_min=-6, y_max=6)

    def f(x):
        return math.log(x, base) + b

    plane.curve(f, 0.02, 18, 120, 2)
    for power in range(0, 3):
        plane.mark(base**power, power + b)
    target_power = r.choice([4, 5, 6]) if base == 2 else r.choice([3, 4, 5])
    intro = "На рисунке изображён график функции f(x) = log_a x + b (логарифм по основанию a). На графике отмечены точки с целыми координатами. "
    if r.random() < 0.5:
        return task(
            intro + f"Найдите f({base ** target_power}).",
            dec(target_power + b),
            f"По отмеченным точкам a = {base}, b = {b}; f({base ** target_power}) = {target_power} + ({b}) = {target_power + b}.",
            plane.fig,
        )
    return task(
        intro + f"Найдите значение x, при котором f(x) = {target_power + b}.",
        dec(base**target_power),
        f"По отмеченным точкам a = {base}, b = {b}; log{sub(base)} x = {target_power}, x = {base ** target_power}.",
        plane.fig,
    )


def g_root(r):
    k = Fraction(r.choice([3, 4, 5, 6, 7]), 2)
    plane = Plane(x_min=-2, x_max=18, y_min=-2, y_max=10)

    def f(x):
        return float(k) * math.sqrt(x)

    plane.curve(f, 0, 18, 110, 2)
    marked = [x for x in (1, 4, 9, 16) if plane.inside(x, f(x)) and (k * int(math.isqrt(x))).denominator == 1]
    if not marked:
        marked = [4]
    for x in marked[:2]:
        plane.mark(x, f(x))
    root = Fraction(r.choice([13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26]), 5)
    x0 = root * root
    return task(
        f"На рисунке изображён график функции f(x) = k√x. На графике отмечены точки с целыми координатами. Найдите f({dec(x0)}).",
        dec(k * root),
        f"По отмеченным точкам k = {dec(k)}; √{dec(x0)} = {dec(root)}, f({dec(x0)}) = {dec(k)} · {dec(root)} = {dec(k * root)}.",
        plane.fig,
    )


NUMBERS = [
    Entry(1, "Планиметрия", 1, [p1_right_triangle, p1_isosceles, p1_parallelogram, p1_trapezoid, p1_circle_angles, p1_incircle, p1_circumcircle]),
    Entry(2, "Векторы", 1, [v_sum_length, v_dot, v_cosine, v_perpendicular, v_endpoint]),
    Entry(3, "Стереометрия", 1, [s_cube, s_box, s_prism, s_pyramid, s_cylinder, s_cone, s_sphere]),
    Entry(4, "Начала теории вероятностей", 1, [pr_sportsmen, pr_defect, pr_bags, pr_dice, pr_coin, pr_tickets, pr_conference, pr_pairs]),
    Entry(5, "Вероятности сложных событий", 1, [c_two_machines, c_shooter, c_factories, c_lamps, c_chess, c_kettle, c_artillery, c_test, c_exam]),
    Entry(6, "Статистика", 1, [st_table, st_lottery, st_until, st_binomial, st_dice, st_game]),
    Entry(7, "Простейшие уравнения", 1, [e_rational, e_quadratic, e_irrational, e_exponential, e_logarithm, e_trigonometric]),
    Entry(8, "Вычисления и преобразования", 1, [t_powers, t_roots, t_logs, t_trig]),
    Entry(9, "Производная и первообразная", 1, [d_physical, d_parallel, d_tangent_coefficient, d_graph_tangent, d_graph_derivative, d_graph_points]),
    Entry(10, "Задачи с прикладным содержанием", 1, [a_ball, a_ohm, a_horizon, a_decay, a_capacitor, a_brake, a_flight, a_heater]),
    Entry(11, "Текстовые задачи", 1, [w_boat, w_half_way, w_cyclist, w_pipes, w_alloy, w_solution, w_percent, w_progression, w_train]),
    Entry(12, "Графики функций", 1, [g_two_lines, g_parabola, g_hyperbola, g_exponent, g_logarithm, g_root]),
]
