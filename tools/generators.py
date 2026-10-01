"""Генераторы заданий с вычисляемым ответом.

Каждый генератор получает random.Random и возвращает словарь с полями
text, answer и explanation. Числа в условии случайные, ответ считает программа,
поэтому он всегда соответствует условию.
"""

from fractions import Fraction


def dec(value) -> str:
    """Число в записи ЕГЭ: конечная десятичная дробь через запятую, без лишних нулей."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    den = value.denominator
    for prime in (2, 5):
        while den % prime == 0:
            den //= prime
    if den != 1:
        raise ValueError(f"{value} не записывается конечной десятичной дробью")
    digits = 0
    scaled = value
    while scaled.denominator != 1:
        scaled *= 10
        digits += 1
    sign = "-" if scaled < 0 else ""
    text = str(abs(scaled.numerator)).rjust(digits + 1, "0")
    return f"{sign}{text[:-digits]},{text[-digits:]}"


def poly(terms) -> str:
    """Многочлен из пар (коэффициент, буквенная часть): poly([(1, 'x²'), (-5, 'x'), (6, '')]) -> 'x² - 5x + 6'."""
    parts = []
    for coef, var in terms:
        if coef == 0:
            continue
        magnitude = abs(coef)
        body = var if (magnitude == 1 and var) else f"{dec(magnitude)}{var}"
        if not parts:
            parts.append(("-" if coef < 0 else "") + body)
        else:
            parts.append(("- " if coef < 0 else "+ ") + body)
    return " ".join(parts) if parts else "0"


SUPERSCRIPT = str.maketrans("0123456789+-xn", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ˣⁿ")
SUBSCRIPT = str.maketrans("0123456789+-n", "₀₁₂₃₄₅₆₇₈₉₊₋ₙ")


def sup(value) -> str:
    """Верхний индекс: sup(5) -> '⁵', sup('x + 6') -> 'ˣ⁺⁶'."""
    return str(value).replace(" ", "").translate(SUPERSCRIPT)


def sub(value) -> str:
    """Нижний индекс: sub(2) -> '₂'."""
    return str(value).replace(" ", "").translate(SUBSCRIPT)


def chem(formula: str) -> str:
    """Химическая формула с нижними индексами: chem('H2SO4') -> 'H₂SO₄'. Коэффициент в начале не трогает."""
    out = []
    for index, ch in enumerate(formula):
        previous = formula[index - 1] if index > 0 else ""
        if ch.isdigit() and (previous.isalpha() or previous == ")" or (previous.isdigit() and out[-1] in "₀₁₂₃₄₅₆₇₈₉")):
            out.append(sub(ch))
        else:
            out.append(ch)
    return "".join(out)


def task(text, answer, explanation, figure=None):
    made = {"text": text, "answer": answer, "explanation": explanation}
    if figure is not None:
        made["figure"] = figure.data()
    return made


# ---------------------------------------------------------------- математика, база


def mb_linear(r):
    a = r.randint(2, 9)
    x = r.choice([n for n in range(-9, 13) if n != 0])
    b = r.choice([n for n in range(-20, 21) if n != 0])
    c = a * x + b
    return task(
        f"Найдите корень уравнения {poly([(a, 'x'), (b, '')])} = {c}.",
        dec(x),
        f"{a}x = {c - b}, откуда x = {x}.",
    )


def mb_discount(r):
    price = r.randrange(200, 3001, 20)
    k = r.choice([5, 10, 15, 20, 25, 30, 40])
    new = price * (100 - k) // 100
    return task(
        f"Товар стоил {price} рублей. Во время распродажи цена снизилась на {k}%. Сколько рублей стал стоить товар?",
        dec(new),
        f"Скидка равна {price} · {k} : 100 = {price * k // 100} рублей, новая цена {new} рублей.",
    )


def mb_decimals(r):
    a = Fraction(r.randint(11, 59), 10)
    b = Fraction(r.randint(11, 49), 10)
    c = Fraction(r.randint(11, 99), 10)
    while c >= a * b:
        c = Fraction(r.randint(11, 99), 10)
    value = a * b - c
    return task(
        f"Найдите значение выражения {dec(a)} · {dec(b)} - {dec(c)}.",
        dec(value),
        f"{dec(a)} · {dec(b)} = {dec(a * b)}; {dec(a * b)} - {dec(c)} = {dec(value)}.",
    )


def mb_powers(r):
    base = r.choice([2, 3, 5])
    diff = r.randint(2, 4)
    n = r.randint(2, 6)
    m = n + diff
    return task(
        f"Найдите значение выражения {base}{sup(m)} : {base}{sup(n)}.",
        dec(base**diff),
        f"При делении степеней с одинаковым основанием показатели вычитаются: {base}{sup(diff)} = {base ** diff}.",
    )


def mb_speed(r):
    v = r.randrange(50, 95, 5)
    t1 = r.randint(2, 4)
    t2 = r.randint(5, 8)
    return task(
        f"Автомобиль проехал {v * t1} км за {t1} ч. Сколько километров он проедет за {t2} ч, если будет двигаться с той же скоростью?",
        dec(v * t2),
        f"Скорость равна {v * t1} : {t1} = {v} км/ч, за {t2} ч автомобиль проедет {v * t2} км.",
    )


def mb_probability(r):
    total = r.choice([10, 20, 25, 40, 50])
    fav = r.randint(1, total - 1)
    return task(
        f"В коробке {total} шаров, из них {fav} красных, остальные синие. Наугад вынимают один шар. Найдите вероятность того, что он красный.",
        dec(Fraction(fav, total)),
        f"Вероятность равна {fav} : {total} = {dec(Fraction(fav, total))}.",
    )


def mb_arith_progression(r):
    a1 = r.randint(-10, 15)
    d = r.choice([n for n in range(-6, 10) if n != 0])
    n = r.randint(8, 25)
    value = a1 + d * (n - 1)
    return task(
        f"В арифметической прогрессии первый член равен {a1}, разность равна {d}. Найдите {n}-й член прогрессии.",
        dec(value),
        f"a{sub(n)} = a₁ + d · (n - 1) = {a1} + ({d}) · {n - 1} = {value}.",
    )


def mb_sqrt(r):
    k = r.randint(11, 45)
    return task(
        f"Найдите значение выражения √{k * k}.",
        dec(k),
        f"{k} · {k} = {k * k}, поэтому корень равен {k}.",
    )


def mb_purchase(r):
    price = r.randint(12, 48)
    money = r.randrange(200, 1001, 50)
    count = money // price
    return task(
        f"Тетрадь стоит {price} рублей. Какое наибольшее число таких тетрадей можно купить на {money} рублей?",
        dec(count),
        f"{money} : {price} = {count} и остаток {money - count * price}, значит, можно купить {count}.",
    )


def mb_pythagoras(r):
    a, b, c = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41)])
    k = r.randint(1, 4)
    return task(
        f"Катеты прямоугольного треугольника равны {a * k} и {b * k}. Найдите гипотенузу.",
        dec(c * k),
        f"По теореме Пифагора квадрат гипотенузы равен {(a * k) ** 2} + {(b * k) ** 2} = {(c * k) ** 2}, гипотенуза равна {c * k}.",
    )


def mb_rectangle(r):
    a = r.randint(3, 20)
    b = r.randint(3, 20)
    p = 2 * (a + b)
    return task(
        f"Периметр прямоугольника равен {p}, одна из его сторон равна {a}. Найдите площадь прямоугольника.",
        dec(a * b),
        f"Вторая сторона равна {p} : 2 - {a} = {b}, площадь равна {a} · {b} = {a * b}.",
    )


def mb_average(r):
    while True:
        numbers = [r.randint(2, 40) for _ in range(4)]
        if sum(numbers) % 2 == 0:
            break
    mean = Fraction(sum(numbers), 4)
    listed = ", ".join(str(n) for n in numbers)
    return task(
        f"Найдите среднее арифметическое чисел {listed}.",
        dec(mean),
        f"Сумма чисел равна {sum(numbers)}, {sum(numbers)} : 4 = {dec(mean)}.",
    )


MATH_BASE = [
    mb_linear, mb_discount, mb_decimals, mb_powers, mb_speed, mb_probability,
    mb_arith_progression, mb_sqrt, mb_purchase, mb_pythagoras, mb_rectangle, mb_average,
]

# ---------------------------------------------------------------- математика, профиль


def mp_quadratic(r):
    x1, x2 = sorted(r.sample(range(-9, 10), 2))
    return task(
        f"Решите уравнение {poly([(1, 'x²'), (-(x1 + x2), 'x'), (x1 * x2, '')])} = 0. "
        "Если уравнение имеет более одного корня, в ответе запишите больший из них.",
        dec(x2),
        f"Корни уравнения: {x1} и {x2}. Больший корень равен {x2}.",
    )


def mp_log(r):
    base = r.choice([2, 2, 3, 4, 5, 10])
    k = r.randint(2, {2: 9, 3: 5, 4: 4, 5: 4, 10: 5}[base])
    return task(
        f"Найдите значение выражения log{sub(base)} {base ** k}.",
        dec(k),
        f"{base}{sup(k)} = {base ** k}, поэтому логарифм равен {k}.",
    )


def mp_derivative(r):
    a = r.choice([1, 2, 3, -1, -2])
    b = r.randint(-5, 5)
    c = r.randint(-9, 9)
    d = r.randint(-9, 9)
    x0 = r.choice([-3, -2, -1, 1, 2, 3])
    value = 3 * a * x0 * x0 + 2 * b * x0 + c
    derivative = poly([(3 * a, "x²"), (2 * b, "x"), (c, "")])
    return task(
        f"Найдите значение производной функции f(x) = {poly([(a, 'x³'), (b, 'x²'), (c, 'x'), (d, '')])} в точке x = {x0}.",
        dec(value),
        f"f'(x) = {derivative}; f'({x0}) = {value}.",
    )


def mp_independent(r):
    p1 = Fraction(r.choice([5, 6, 7, 8, 9]), 10)
    p2 = Fraction(r.choice([5, 6, 7, 8, 9]), 10)
    if r.random() < 0.5:
        value = p1 * p2
        question = "в мишень попадут оба стрелка"
        how = f"Вероятности независимых событий перемножаются: {dec(p1)} · {dec(p2)} = {dec(value)}."
    else:
        value = 1 - (1 - p1) * (1 - p2)
        question = "в мишень попадёт хотя бы один стрелок"
        how = f"Вероятность двух промахов равна {dec(1 - p1)} · {dec(1 - p2)} = {dec((1 - p1) * (1 - p2))}, искомая вероятность равна {dec(value)}."
    return task(
        f"Два стрелка независимо друг от друга делают по одному выстрелу по мишени. Вероятность попадания первого равна {dec(p1)}, "
        f"второго {dec(p2)}. Найдите вероятность того, что {question}.",
        dec(value),
        how,
    )


def mp_exponential(r):
    base = r.choice([2, 3, 5])
    k = r.randint(2, 5 if base == 2 else 4)
    shift = r.choice([n for n in range(-6, 7) if n != 0])
    x = k - shift
    return task(
        f"Найдите корень уравнения {base}{sup(poly([(1, 'x'), (shift, '')]))} = {base ** k}.",
        dec(x),
        f"{base ** k} = {base}{sup(k)}, поэтому {poly([(1, 'x'), (shift, '')])} = {k}, откуда x = {x}.",
    )


TRIG_VALUES = [
    ("sin 30°", Fraction(1, 2)), ("cos 60°", Fraction(1, 2)), ("tg 45°", Fraction(1)),
    ("sin 90°", Fraction(1)), ("cos 0°", Fraction(1)), ("cos 180°", Fraction(-1)),
    ("sin 270°", Fraction(-1)), ("cos 120°", Fraction(-1, 2)), ("sin 150°", Fraction(1, 2)),
]


def mp_trig(r):
    (name1, v1), (name2, v2) = r.sample(TRIG_VALUES, 2)
    k = r.choice([2, 4, 6, 8, 10])
    m = r.choice([2, 4, 6, 8])
    value = k * v1 + m * v2
    return task(
        f"Найдите значение выражения {k} · {name1} + {m} · {name2}.",
        dec(value),
        f"{name1} = {dec(v1)}, {name2} = {dec(v2)}; значение выражения равно {dec(value)}.",
    )


def mp_meeting(r):
    v1 = r.randrange(50, 95, 5)
    v2 = r.randrange(50, 95, 5)
    t = r.randint(2, 6)
    s = (v1 + v2) * t
    return task(
        f"Из двух городов, расстояние между которыми равно {s} км, навстречу друг другу одновременно выехали два автомобиля "
        f"со скоростями {v1} км/ч и {v2} км/ч. Через сколько часов автомобили встретятся?",
        dec(t),
        f"Скорость сближения равна {v1 + v2} км/ч, {s} : {v1 + v2} = {t} ч.",
    )


def mp_mixture(r):
    while True:
        a, b = r.randint(2, 12), r.randint(2, 12)
        p, q = r.sample(range(5, 65, 5), 2)
        if (a * p + b * q) % (a + b) == 0:
            break
    value = (a * p + b * q) // (a + b)
    return task(
        f"Смешали {a} л {p}-процентного раствора вещества и {b} л {q}-процентного раствора этого же вещества. "
        "Сколько процентов составляет концентрация получившегося раствора?",
        dec(value),
        f"Вещества в смеси {dec(Fraction(a * p + b * q, 100))} л на {a + b} л раствора, это {value}%.",
    )


def mp_cube(r):
    k = r.randint(2, 12)
    if r.random() < 0.5:
        return task(
            f"Объём куба равен {k ** 3}. Найдите площадь его поверхности.",
            dec(6 * k * k),
            f"Ребро куба равно {k}, площадь поверхности равна 6 · {k}² = {6 * k * k}.",
        )
    return task(
        f"Площадь поверхности куба равна {6 * k * k}. Найдите его объём.",
        dec(k**3),
        f"Площадь одной грани равна {k * k}, ребро равно {k}, объём равен {k}³ = {k ** 3}.",
    )


def mp_dot(r):
    x1, y1, x2, y2 = (r.randint(-9, 9) for _ in range(4))
    value = x1 * x2 + y1 * y2
    return task(
        f"Даны векторы a({x1}; {y1}) и b({x2}; {y2}). Найдите их скалярное произведение.",
        dec(value),
        f"{x1} · ({x2}) + {y1} · ({y2}) = {value}.",
    )


def mp_geom_progression(r):
    b1 = r.choice([1, 2, 3, 5])
    q = r.choice([2, 3, -2])
    n = r.randint(4, 7)
    value = b1 * q ** (n - 1)
    return task(
        f"В геометрической прогрессии первый член равен {b1}, знаменатель равен {q}. Найдите {n}-й член прогрессии.",
        dec(value),
        f"b{sub(n)} = b₁ · q{sup(n - 1)} = {b1} · ({q}){sup(n - 1)} = {value}.",
    )


def mp_parabola_min(r):
    a = r.choice([n for n in range(-8, 9) if n != 0])
    c = r.randint(-20, 30)
    value = c - a * a
    return task(
        f"Найдите наименьшее значение функции y = {poly([(1, 'x²'), (-2 * a, 'x'), (c, '')])}.",
        dec(value),
        f"Вершина параболы находится в точке x = {a}, значение функции в ней равно {value}.",
    )


def mp_root_equation(r):
    while True:
        a = r.randint(2, 7)
        c = r.randint(2, 9)
        b = r.randint(-15, 15)
        if b != 0 and (c * c - b) % a == 0:
            break
    x = (c * c - b) // a
    inner = poly([(a, "x"), (b, "")])
    return task(
        f"Найдите корень уравнения √({inner}) = {c}.",
        dec(x),
        f"Возводим обе части в квадрат: {inner} = {c * c}, откуда x = {x}.",
    )


MATH_PROF = [
    mp_quadratic, mp_log, mp_derivative, mp_independent, mp_exponential, mp_trig, mp_meeting,
    mp_mixture, mp_cube, mp_dot, mp_geom_progression, mp_parabola_min, mp_root_equation,
]

# ---------------------------------------------------------------- физика


def ph_speed(r):
    v = r.randint(3, 30)
    t = r.randint(4, 40)
    return task(
        f"Тело движется равномерно и за {t} с проходит {v * t} м. Найдите скорость тела. Ответ дайте в м/с.",
        dec(v),
        f"v = s : t = {v * t} : {t} = {v} м/с.",
    )


def ph_acceleration(r):
    v0 = r.randint(0, 12)
    a = r.randint(1, 6)
    t = r.randint(2, 10)
    return task(
        f"Тело движется прямолинейно с постоянным ускорением {a} м/с², начальная скорость равна {v0} м/с. "
        f"Какой станет скорость тела через {t} с? Ответ дайте в м/с.",
        dec(v0 + a * t),
        f"v = v0 + a · t = {v0} + {a} · {t} = {v0 + a * t} м/с.",
    )


def ph_newton(r):
    m = r.randint(2, 40)
    a = Fraction(r.randint(1, 12), 2)
    return task(
        f"Тело массой {m} кг движется с ускорением {dec(a)} м/с². Найдите равнодействующую сил, действующих на тело. Ответ дайте в ньютонах.",
        dec(m * a),
        f"F = m · a = {m} · {dec(a)} = {dec(m * a)} Н.",
    )


def ph_ohm(r):
    resistance = r.choice([2, 4, 5, 8, 10, 20, 25, 40, 50])
    current = Fraction(r.randint(1, 12), 2)
    voltage = resistance * current
    return task(
        f"Напряжение на резисторе сопротивлением {resistance} Ом равно {dec(voltage)} В. Найдите силу тока в резисторе. Ответ дайте в амперах.",
        dec(current),
        f"I = U : R = {dec(voltage)} : {resistance} = {dec(current)} А.",
    )


def ph_kinetic(r):
    m = r.choice([2, 4, 6, 8, 10, 20])
    v = r.randint(2, 12)
    return task(
        f"Тело массой {m} кг движется со скоростью {v} м/с. Найдите кинетическую энергию тела. Ответ дайте в джоулях.",
        dec(m * v * v // 2),
        f"E = m · v² : 2 = {m} · {v * v} : 2 = {m * v * v // 2} Дж.",
    )


def ph_potential(r):
    m = r.randint(2, 30)
    h = r.randint(2, 25)
    return task(
        f"Груз массой {m} кг подняли на высоту {h} м над землёй. На сколько увеличилась потенциальная энергия груза? "
        "Ускорение свободного падения считайте равным 10 м/с². Ответ дайте в джоулях.",
        dec(m * 10 * h),
        f"E = m · g · h = {m} · 10 · {h} = {m * 10 * h} Дж.",
    )


def ph_heat(r):
    m = r.randint(1, 5)
    dt = r.choice([10, 20, 30, 40, 50])
    q = Fraction(4200 * m * dt, 1000)
    return task(
        f"Какое количество теплоты нужно, чтобы нагреть {m} кг воды на {dt} °C? Удельная теплоёмкость воды равна 4200 Дж/(кг·°C). Ответ дайте в килоджоулях.",
        dec(q),
        f"Q = c · m · Δt = 4200 · {m} · {dt} = {4200 * m * dt} Дж = {dec(q)} кДж.",
    )


def ph_power(r):
    voltage = r.choice([12, 24, 36, 110, 220])
    current = Fraction(r.randint(1, 10), 2)
    return task(
        f"Сила тока в лампе равна {dec(current)} А при напряжении {voltage} В. Найдите мощность лампы. Ответ дайте в ваттах.",
        dec(voltage * current),
        f"P = U · I = {voltage} · {dec(current)} = {dec(voltage * current)} Вт.",
    )


def ph_density(r):
    name, rho = r.choice([("алюминия", 2700), ("железа", 7800), ("меди", 8900), ("льда", 900), ("стекла", 2500)])
    volume = Fraction(r.choice([1, 2, 4, 5, 10, 20, 50]), 1000)
    return task(
        f"Плотность {name} равна {rho} кг/м³. Найдите массу тела из этого вещества объёмом {dec(volume)} м³. Ответ дайте в килограммах.",
        dec(rho * volume),
        f"m = ρ · V = {rho} · {dec(volume)} = {dec(rho * volume)} кг.",
    )


def ph_wave(r):
    medium, speed = r.choice([("в воздухе", 340), ("в воде", 1500), ("в стали", 5000)])
    while True:
        length = Fraction(r.choice([1, 2, 4, 5, 8, 10, 20, 25, 40, 50]), r.choice([1, 2, 4, 5, 10]))
        frequency = Fraction(speed) / length
        if frequency.denominator == 1 and 20 <= frequency <= 20000:
            break
    return task(
        f"Звуковая волна частотой {frequency.numerator} Гц распространяется {medium} со скоростью {speed} м/с. Найдите длину волны. Ответ дайте в метрах.",
        dec(length),
        f"λ = v : ν = {speed} : {frequency.numerator} = {dec(length)} м.",
    )


def ph_parallel(r):
    n = r.choice([2, 4, 5])
    resistance = n * r.randint(1, 12)
    return task(
        f"{n} одинаковых резистора сопротивлением {resistance} Ом каждый соединены параллельно. Найдите общее сопротивление участка. Ответ дайте в омах."
        if n < 5
        else f"{n} одинаковых резисторов сопротивлением {resistance} Ом каждый соединены параллельно. Найдите общее сопротивление участка. Ответ дайте в омах.",
        dec(resistance // n),
        f"При параллельном соединении одинаковых резисторов R = {resistance} : {n} = {resistance // n} Ом.",
    )


def ph_momentum(r):
    m = Fraction(r.randint(1, 40), 2)
    v = r.randint(2, 20)
    return task(
        f"Тело массой {dec(m)} кг движется со скоростью {v} м/с. Найдите модуль импульса тела. Ответ дайте в кг·м/с.",
        dec(m * v),
        f"p = m · v = {dec(m)} · {v} = {dec(m * v)} кг·м/с.",
    )


def ph_free_fall(r):
    t = r.randint(1, 10)
    if r.random() < 0.5:
        return task(
            f"Камень свободно падает без начальной скорости в течение {t} с. Какой путь он прошёл за это время? "
            "Ускорение свободного падения считайте равным 10 м/с², сопротивлением воздуха пренебрегите. Ответ дайте в метрах.",
            dec(5 * t * t),
            f"h = g · t² : 2 = 10 · {t * t} : 2 = {5 * t * t} м.",
        )
    return task(
        f"Камень свободно падает без начальной скорости. Какой будет его скорость через {t} с после начала падения? "
        "Ускорение свободного падения считайте равным 10 м/с², сопротивлением воздуха пренебрегите. Ответ дайте в м/с.",
        dec(10 * t),
        f"v = g · t = 10 · {t} = {10 * t} м/с.",
    )


def ph_pressure(r):
    area = Fraction(r.choice([1, 2, 4, 5, 8, 10, 20]), 10)
    pressure = r.randrange(100, 2001, 100)
    force = pressure * area
    return task(
        f"Сила {dec(force)} Н действует перпендикулярно поверхности площадью {dec(area)} м². Найдите давление на поверхность. Ответ дайте в паскалях.",
        dec(pressure),
        f"p = F : S = {dec(force)} : {dec(area)} = {pressure} Па.",
    )


def ph_work(r):
    force = r.randint(5, 80)
    distance = r.randint(2, 30)
    return task(
        f"Тело перемещают на {distance} м, действуя на него силой {force} Н, направленной вдоль перемещения. Найдите работу этой силы. Ответ дайте в джоулях.",
        dec(force * distance),
        f"A = F · s = {force} · {distance} = {force * distance} Дж.",
    )


def ph_period(r):
    frequency = r.choice([2, 4, 5, 8, 10, 16, 20, 25, 40, 50, 80, 100, 125, 200, 250, 400, 500])
    period = Fraction(1, frequency)
    if r.random() < 0.5:
        return task(
            f"Частота колебаний равна {frequency} Гц. Найдите период колебаний. Ответ дайте в секундах.",
            dec(period),
            f"T = 1 : ν = 1 : {frequency} = {dec(period)} с.",
        )
    return task(
        f"Период колебаний равен {dec(period)} с. Найдите частоту колебаний. Ответ дайте в герцах.",
        dec(frequency),
        f"ν = 1 : T = 1 : {dec(period)} = {frequency} Гц.",
    )


PHYSICS = [
    ph_speed, ph_acceleration, ph_newton, ph_ohm, ph_kinetic, ph_potential, ph_heat, ph_power,
    ph_density, ph_wave, ph_parallel, ph_momentum, ph_free_fall, ph_pressure, ph_work, ph_period,
]

# ---------------------------------------------------------------- информатика


def inf_bin_to_dec(r):
    n = r.randint(17, 255)
    return task(
        f"Переведите двоичное число {n:b} в десятичную систему счисления.",
        dec(n),
        f"Сумма степеней двойки на местах единиц равна {n}.",
    )


def inf_ones(r):
    n = r.randint(100, 1000)
    return task(
        f"Сколько единиц в двоичной записи десятичного числа {n}?",
        dec(bin(n).count("1")),
        f"{n} в двоичной системе записывается как {n:b}.",
    )


def inf_hex_to_dec(r):
    n = r.randint(30, 4000)
    return task(
        f"Переведите шестнадцатеричное число {n:X} в десятичную систему счисления.",
        dec(n),
        f"Раскладываем по степеням числа 16 и получаем {n}.",
    )


def inf_bits(r):
    n = r.randint(5, 2000)
    bits = (n - 1).bit_length()
    return task(
        f"Какое минимальное число бит нужно, чтобы закодировать каждое из {n} различных значений одинаковым числом бит?",
        dec(bits),
        f"2{sup(bits - 1)} = {2 ** (bits - 1)} меньше {n}, а 2{sup(bits)} = {2 ** bits} не меньше {n}.",
    )


def inf_volume(r):
    while True:
        alphabet = r.choice([8, 16, 26, 32, 33, 64, 100, 128, 200, 256])
        bits = (alphabet - 1).bit_length()
        length = r.randrange(40, 801, 8)
        if (bits * length) % 8 == 0:
            break
    return task(
        f"Сообщение длиной {length} символов записано буквами алфавита из {alphabet} символов. Каждый символ кодируется одинаковым "
        "минимально возможным числом бит. Сколько байт занимает сообщение?",
        dec(bits * length // 8),
        f"На символ нужно {bits} бит, всего {bits * length} бит, это {bits * length // 8} байт.",
    )


LOGIC = [
    ("(x И y) ИЛИ (НЕ z)", lambda x, y, z: (x and y) or not z),
    ("(x ИЛИ y) И (НЕ z)", lambda x, y, z: (x or y) and not z),
    ("x И (y ИЛИ z)", lambda x, y, z: x and (y or z)),
    ("(НЕ x) ИЛИ (y И z)", lambda x, y, z: (not x) or (y and z)),
    ("(x ИЛИ y) И (y ИЛИ z)", lambda x, y, z: (x or y) and (y or z)),
    ("НЕ (x И y) И z", lambda x, y, z: (not (x and y)) and z),
    ("(x И НЕ y) ИЛИ (y И НЕ z)", lambda x, y, z: (x and not y) or (y and not z)),
    ("НЕ (x ИЛИ y ИЛИ z)", lambda x, y, z: not (x or y or z)),
    ("(x ИЛИ НЕ y) И (y ИЛИ НЕ z)", lambda x, y, z: (x or not y) and (y or not z)),
    ("x ИЛИ (y И НЕ z)", lambda x, y, z: x or (y and not z)),
    ("(x И y) ИЛИ (y И z)", lambda x, y, z: (x and y) or (y and z)),
    ("(x ИЛИ y) И НЕ (x И y)", lambda x, y, z: (x or y) and not (x and y)),
    ("НЕ x ИЛИ НЕ y ИЛИ z", lambda x, y, z: (not x) or (not y) or z),
    ("(x И y И z) ИЛИ (НЕ x И НЕ y)", lambda x, y, z: (x and y and z) or ((not x) and (not y))),
    ("x И НЕ (y ИЛИ z)", lambda x, y, z: x and not (y or z)),
    ("(x ИЛИ z) И (НЕ y)", lambda x, y, z: (x or z) and not y),
    ("НЕ (x И y И z)", lambda x, y, z: not (x and y and z)),
    ("(x ИЛИ y ИЛИ z) И НЕ x", lambda x, y, z: (x or y or z) and not x),
    ("(НЕ x И y) ИЛИ (x И НЕ z)", lambda x, y, z: ((not x) and y) or (x and not z)),
    ("(x ИЛИ НЕ z) И (y ИЛИ z)", lambda x, y, z: (x or not z) and (y or z)),
    ("НЕ (x ИЛИ y) ИЛИ (y И z)", lambda x, y, z: (not (x or y)) or (y and z)),
    ("(x И НЕ y И z) ИЛИ (НЕ x И y)", lambda x, y, z: (x and (not y) and z) or ((not x) and y)),
]


def inf_logic(r):
    expression, function = r.choice(LOGIC)
    count = sum(
        1 for x in (False, True) for y in (False, True) for z in (False, True) if function(x, y, z)
    )
    return task(
        f"Логические переменные x, y, z принимают значения «истина» или «ложь». "
        f"Сколько существует наборов значений (x, y, z), при которых выражение {expression} истинно?",
        dec(count),
        f"Перебираем все 8 наборов значений: выражение истинно на {count} из них.",
    )


def inf_for_loop(r):
    s0 = r.randint(0, 20)
    a = r.randint(1, 5)
    b = a + r.randint(3, 7)
    c = r.randint(2, 5)
    s = s0 + sum(k * c for k in range(a, b))
    return task(
        "Что выведет программа на языке Python?\n\n"
        f"s = {s0}\nfor k in range({a}, {b}):\n    s = s + k * {c}\nprint(s)",
        dec(s),
        f"Переменная k принимает значения от {a} до {b - 1}; в итоге s = {s}.",
    )


def inf_while_loop(r):
    n = r.randint(50, 3000)
    d = r.choice([2, 3, 4, 5])
    k, m = 0, n
    while m > 0:
        m //= d
        k += 1
    return task(
        "Что выведет программа на языке Python?\n\n"
        f"n = {n}\nk = 0\nwhile n > 0:\n    n = n // {d}\n    k = k + 1\nprint(k)",
        dec(k),
        f"Число делится нацело на {d}, пока не станет нулём. Это происходит за {k} шагов.",
    )


def inf_divisible(r):
    p, q = r.choice([(2, 3), (3, 2), (3, 5), (5, 3), (4, 3), (7, 2), (5, 2), (2, 5)])
    a = r.randint(1, 60)
    b = a + r.randint(40, 200)
    count = sum(1 for n in range(a, b + 1) if n % p == 0 and n % q != 0)
    return task(
        f"Сколько натуральных чисел от {a} до {b} включительно делятся на {p}, но не делятся на {q}?",
        dec(count),
        f"Из чисел, кратных {p}, убираем кратные {p * q}. Остаётся {count}.",
    )


def inf_robot(r):
    start = r.randint(1, 3)
    goal = r.randint(10, 26)
    ways = [0] * (goal + 1)
    ways[start] = 1
    for n in range(start + 1, goal + 1):
        ways[n] = ways[n - 1] + (ways[n // 2] if n % 2 == 0 and n // 2 >= start else 0)
    return task(
        "Исполнитель преобразует число на экране. У него две команды: «прибавить 1» и «умножить на 2». "
        f"Сколько существует программ, которые преобразуют число {start} в число {goal}?",
        dec(ways[goal]),
        f"Считаем число программ для каждого числа от {start} до {goal}: в число n можно попасть из n - 1 и, если n чётное, из n : 2. Получается {ways[goal]}.",
    )


def inf_transfer(r):
    speed = r.choice([4096, 8192, 16384, 32768])
    size = r.randrange(16, 513, 16)
    seconds = size * 8192 // speed
    return task(
        f"Файл размером {size} Кбайт передаётся по каналу со скоростью {speed} бит в секунду. Сколько секунд займёт передача файла?",
        dec(seconds),
        f"В файле {size} · 1024 · 8 = {size * 8192} бит, {size * 8192} : {speed} = {seconds} с.",
    )


def inf_words(r):
    letters = r.randint(2, 6)
    length = r.randint(2, 6)
    return task(
        f"Сколько различных слов длиной {length} можно составить из букв алфавита, в котором {letters} "
        f"{'буквы' if letters < 5 else 'букв'}? Буквы в слове могут повторяться, слово не обязано быть осмысленным.",
        dec(letters**length),
        f"На каждом из {length} мест может стоять любая из {letters} букв: {letters}{sup(length)} = {letters ** length}.",
    )


def inf_recursion(r):
    a = r.randint(1, 4)
    b = r.randint(1, 5)
    n = r.randint(6, 10)
    values = [0, a, b]
    for index in range(3, n + 1):
        values.append(values[index - 1] + values[index - 2])
    return task(
        f"Функция F(n) задана так: F(1) = {a}, F(2) = {b}, F(n) = F(n - 1) + F(n - 2) при n > 2. Чему равно F({n})?",
        dec(values[n]),
        "Считаем по порядку: " + ", ".join(str(v) for v in values[1:]) + ".",
    )


def inf_to_base(r):
    base = r.choice([3, 5, 8])
    n = r.randint(20, 300)
    digits, m = "", n
    while m > 0:
        digits = str(m % base) + digits
        m //= base
    return task(
        f"Запишите десятичное число {n} в системе счисления с основанием {base}. В ответе укажите только цифры, основание писать не нужно.",
        digits,
        f"Делим {n} на {base} с остатком и выписываем остатки в обратном порядке: {digits}.",
    )


INFORMATICS = [
    inf_bin_to_dec, inf_ones, inf_hex_to_dec, inf_bits, inf_volume, inf_logic, inf_for_loop,
    inf_while_loop, inf_divisible, inf_robot, inf_transfer, inf_words, inf_recursion, inf_to_base,
]

# ---------------------------------------------------------------- химия

ATOMIC_MASS = {"H": 1, "C": 12, "N": 14, "O": 16, "Na": 23, "Mg": 24, "Al": 27, "P": 31, "S": 32, "Cl": Fraction(71, 2), "K": 39, "Ca": 40, "Fe": 56, "Cu": 64}

COMPOUNDS = [
    ("серной кислоты", "H2SO4", {"H": 2, "S": 1, "O": 4}),
    ("воды", "H2O", {"H": 2, "O": 1}),
    ("углекислого газа", "CO2", {"C": 1, "O": 2}),
    ("гидроксида натрия", "NaOH", {"Na": 1, "O": 1, "H": 1}),
    ("карбоната кальция", "CaCO3", {"Ca": 1, "C": 1, "O": 3}),
    ("аммиака", "NH3", {"N": 1, "H": 3}),
    ("метана", "CH4", {"C": 1, "H": 4}),
    ("азотной кислоты", "HNO3", {"H": 1, "N": 1, "O": 3}),
    ("оксида алюминия", "Al2O3", {"Al": 2, "O": 3}),
    ("оксида железа(III)", "Fe2O3", {"Fe": 2, "O": 3}),
    ("хлорида натрия", "NaCl", {"Na": 1, "Cl": 1}),
    ("сульфата меди(II)", "CuSO4", {"Cu": 1, "S": 1, "O": 4}),
    ("гидроксида кальция", "Ca(OH)2", {"Ca": 1, "O": 2, "H": 2}),
    ("фосфорной кислоты", "H3PO4", {"H": 3, "P": 1, "O": 4}),
    ("оксида магния", "MgO", {"Mg": 1, "O": 1}),
    ("этанола", "C2H5OH", {"C": 2, "H": 6, "O": 1}),
    ("хлороводорода", "HCl", {"H": 1, "Cl": 1}),
    ("оксида серы(VI)", "SO3", {"S": 1, "O": 3}),
    ("сероводорода", "H2S", {"H": 2, "S": 1}),
    ("карбоната натрия", "Na2CO3", {"Na": 2, "C": 1, "O": 3}),
    ("гидроксида калия", "KOH", {"K": 1, "O": 1, "H": 1}),
    ("хлорида кальция", "CaCl2", {"Ca": 1, "Cl": 2}),
    ("нитрата калия", "KNO3", {"K": 1, "N": 1, "O": 3}),
    ("оксида меди(II)", "CuO", {"Cu": 1, "O": 1}),
    ("сульфата натрия", "Na2SO4", {"Na": 2, "S": 1, "O": 4}),
    ("оксида фосфора(V)", "P2O5", {"P": 2, "O": 5}),
    ("этана", "C2H6", {"C": 2, "H": 6}),
    ("глюкозы", "C6H12O6", {"C": 6, "H": 12, "O": 6}),
]


def molar_mass(composition):
    return sum(ATOMIC_MASS[element] * count for element, count in composition.items())


def masses_note(composition):
    return ", ".join(f"{element} = {dec(ATOMIC_MASS[element])}" for element in composition)


def ch_molar_mass(r):
    name, formula, composition = r.choice(COMPOUNDS)
    return task(
        f"Вычислите молярную массу {name} {chem(formula)}. Относительные атомные массы: {masses_note(composition)}. Ответ дайте в г/моль.",
        dec(molar_mass(composition)),
        "Складываем атомные массы с учётом числа атомов: " + dec(molar_mass(composition)) + " г/моль.",
    )


def ch_moles(r):
    name, formula, composition = r.choice(COMPOUNDS)
    amount = Fraction(r.choice([1, 2, 3, 4, 5, 6, 8, 10]), 2)
    mass = molar_mass(composition) * amount
    return task(
        f"Какое количество вещества содержится в {dec(mass)} г {name} {chem(formula)}? Относительные атомные массы: {masses_note(composition)}. Ответ дайте в молях.",
        dec(amount),
        f"M = {dec(molar_mass(composition))} г/моль, n = m : M = {dec(mass)} : {dec(molar_mass(composition))} = {dec(amount)} моль.",
    )


def ch_dilution(r):
    while True:
        m1 = r.randrange(50, 401, 10)
        w = r.choice([5, 10, 15, 20, 25, 30, 40])
        m2 = r.randrange(10, 401, 10)
        if (m1 * w) % (m1 + m2) == 0:
            break
    value = m1 * w // (m1 + m2)
    return task(
        f"К {m1} г раствора с массовой долей соли {w}% добавили {m2} г воды. Найдите массовую долю соли в полученном растворе. Ответ дайте в процентах.",
        dec(value),
        f"Соли в растворе {dec(Fraction(m1 * w, 100))} г, масса нового раствора {m1 + m2} г, массовая доля равна {value}%.",
    )


def ch_gas_volume(r):
    amount = Fraction(r.randint(1, 40), 4)
    volume = amount * Fraction(224, 10)
    return task(
        f"Какой объём при нормальных условиях занимает газ количеством вещества {dec(amount)} моль? Молярный объём газа равен 22,4 л/моль. Ответ дайте в литрах.",
        dec(volume),
        f"V = n · Vm = {dec(amount)} · 22,4 = {dec(volume)} л.",
    )


ISOTOPES = [
    ("углерода", 6, [12, 13, 14]), ("кислорода", 8, [16, 17, 18]), ("натрия", 11, [23]), ("хлора", 17, [35, 37]),
    ("калия", 19, [39, 40]), ("железа", 26, [54, 56]), ("алюминия", 13, [27]), ("фосфора", 15, [31]),
    ("серы", 16, [32, 34]), ("кальция", 20, [40, 42]), ("азота", 7, [14, 15]), ("магния", 12, [24, 26]),
]


def ch_neutrons(r):
    name, protons, mass_numbers = r.choice(ISOTOPES)
    mass_number = r.choice(mass_numbers)
    return task(
        f"Сколько нейтронов содержит ядро атома {name} с массовым числом {mass_number}? Порядковый номер элемента равен {protons}.",
        dec(mass_number - protons),
        f"Число нейтронов равно массовому числу минус число протонов: {mass_number} - {protons} = {mass_number - protons}.",
    )


IONS = [
    ("натрия Na⁺", 11, 1), ("магния Mg²⁺", 12, 2), ("хлора Cl⁻", 17, -1), ("серы S²⁻", 16, -2), ("калия K⁺", 19, 1),
    ("кальция Ca²⁺", 20, 2), ("алюминия Al³⁺", 13, 3), ("кислорода O²⁻", 8, -2), ("фтора F⁻", 9, -1), ("лития Li⁺", 3, 1),
    ("бериллия Be²⁺", 4, 2), ("азота N³⁻", 7, -3), ("фосфора P³⁻", 15, -3), ("брома Br⁻", 35, -1),
    ("иода I⁻", 53, -1), ("железа Fe²⁺", 26, 2), ("железа Fe³⁺", 26, 3), ("цинка Zn²⁺", 30, 2),
    ("меди Cu²⁺", 29, 2), ("бария Ba²⁺", 56, 2), ("рубидия Rb⁺", 37, 1), ("стронция Sr²⁺", 38, 2),
    ("серебра Ag⁺", 47, 1),
]


def ch_ion_electrons(r):
    name, protons, charge = r.choice(IONS)
    return task(
        f"Сколько электронов содержит ион {name}? Порядковый номер элемента равен {protons}.",
        dec(protons - charge),
        f"В атоме {protons} электронов. Заряд иона показывает, сколько электронов отдано или принято, в ионе их {protons - charge}.",
    )


OXIDATION = [
    ("серы", "H2SO4", 6), ("серы", "SO2", 4), ("серы", "H2S", -2), ("азота", "HNO3", 5), ("азота", "NH3", -3),
    ("азота", "NO2", 4), ("углерода", "CO2", 4), ("углерода", "CH4", -4), ("хлора", "HClO4", 7), ("хлора", "NaCl", -1),
    ("марганца", "KMnO4", 7), ("марганца", "MnO2", 4), ("фосфора", "H3PO4", 5), ("хрома", "K2Cr2O7", 6),
    ("железа", "Fe2O3", 3), ("кислорода", "H2O2", -1),
    ("азота", "N2O5", 5), ("азота", "NO", 2), ("серы", "SO3", 6), ("серы", "Na2SO3", 4),
    ("хлора", "KClO3", 5), ("хлора", "HClO", 1), ("фосфора", "PH3", -3), ("фосфора", "P2O5", 5),
    ("углерода", "CO", 2), ("железа", "FeO", 2), ("хрома", "Cr2O3", 3), ("меди", "CuO", 2),
    ("кислорода", "OF2", 2), ("водорода", "NaH", -1),
]


def ch_oxidation(r):
    element, formula, state = r.choice(OXIDATION)
    answer = f"+{state}" if state > 0 else str(state)
    result = task(
        f"Определите степень окисления {element} в соединении {chem(formula)}. Ответ запишите со знаком, например +3 или -2.",
        answer,
        f"Сумма степеней окисления всех атомов в соединении равна нулю, отсюда степень окисления {element} равна {answer}.",
    )
    if state > 0:
        result["answers"] = [answer, str(state)]
    return result


def ch_combustion(r):
    amount = Fraction(r.randint(1, 40), 2)
    return task(
        f"Сколько граммов воды образуется при полном сгорании {dec(amount)} моль водорода? Уравнение реакции: 2H₂ + O₂ = 2H₂O. Молярная масса воды равна 18 г/моль.",
        dec(amount * 18),
        f"Из {dec(amount)} моль водорода получается {dec(amount)} моль воды, её масса {dec(amount)} · 18 = {dec(amount * 18)} г.",
    )


CHEMISTRY = [
    ch_molar_mass, ch_moles, ch_dilution, ch_gas_volume, ch_neutrons, ch_ion_electrons, ch_oxidation, ch_combustion,
]

# Какие предметы строятся генераторами и какой вид проверки у ответа.
GENERATED = {
    "math_base": MATH_BASE,
    "math_prof": MATH_PROF,
    "physics": PHYSICS,
    "informatics": INFORMATICS,
    "chemistry": CHEMISTRY,
}

# Генераторы, чей ответ сравнивается как строка, а не как число.
EXACT_GENERATORS = {"inf_to_base", "ch_oxidation"}
