"""Информатика: задания первой части по структуре ЕГЭ 2026.

Номера 3, 9, 17, 18, 22, 24-27 требуют файлов или программирования и в игру не переносятся.
Числа подобраны так, чтобы остальные задания решались без компьютера. Ответы считает перебор.
"""

import math
from itertools import permutations, product

import figures
from exam_common import Entry, plural, table_figure
from figures import Fig
from generators import dec, task

LETTERS = "АБВГДЕ"


def exact(made):
    made["kind"] = "exact"
    return made


# ---------------------------------------------------------------- №1 Анализ информационных моделей


def automorphisms(adjacent):
    size = len(adjacent)
    return [p for p in permutations(range(size))
            if all(adjacent[u][v] == adjacent[p[u]][p[v]] for u in range(size) for v in range(u + 1, size))]


def m_graph_table(r):
    size = 6
    while True:
        order = list(range(size))
        r.shuffle(order)
        edges = {tuple(sorted((order[i], order[i + 1]))) for i in range(size - 1)}
        while len(edges) < r.choice([7, 8, 9]):
            edges.add(tuple(sorted(r.sample(range(size), 2))))
        adjacent = [[(min(u, v), max(u, v)) in edges for v in range(size)] for u in range(size)]
        weights = {edge: weight for edge, weight in zip(sorted(edges), r.sample(range(4, 60), len(edges)))}
        autos = automorphisms(adjacent)
        # Подходит дорога, длина которой определяется однозначно при любом допустимом сопоставлении таблицы и графа.
        good = [edge for edge in sorted(edges)
                if len({weights[tuple(sorted((auto[edge[0]], auto[edge[1]])))] for auto in autos}) == 1]
        degrees = sorted(sum(row) for row in adjacent)
        if good and len(set(degrees)) >= 3:
            break
    first, second = r.choice(good)
    numbering = list(range(size))
    r.shuffle(numbering)  # numbering[вершина графа] = номер пункта в таблице

    fig = Fig(450, 240)
    cell, left, top = 31, 8, 8
    for line in range(size + 2):
        style = 1 if line in (0, 1, size + 1) else 0
        fig.line(left, top + line * cell, left + (size + 1) * cell, top + line * cell, style)
        fig.line(left + line * cell, top, left + line * cell, top + (size + 1) * cell, style)
    for index in range(size):
        fig.text(left + (index + 1.5) * cell, top + cell / 2, f"П{index + 1}")
        fig.text(left + cell / 2, top + (index + 1.5) * cell, f"П{index + 1}")
    for (u, v), weight in weights.items():
        for row, column in ((numbering[u], numbering[v]), (numbering[v], numbering[u])):
            fig.text(left + (column + 1.5) * cell, top + (row + 1.5) * cell, weight)
    center_x, center_y, radius = 345, 118, 82
    points = [(center_x + radius * math.sin(2 * math.pi * k / size), center_y - radius * math.cos(2 * math.pi * k / size)) for k in range(size)]
    for u, v in sorted(edges):
        fig.line(*points[u], *points[v], 1)
    for k, (x, y) in enumerate(points):
        fig.circle(x, y, 5, 2)
        fig.text(center_x + (radius + 17) * math.sin(2 * math.pi * k / size), center_y - (radius + 17) * math.cos(2 * math.pi * k / size), LETTERS[k])
    return task(
        "На рисунке справа схема дорог района изображена в виде графа, в таблице слева содержатся сведения о длинах этих дорог (в километрах). "
        "Таблицу и схему рисовали независимо друг от друга, поэтому нумерация населённых пунктов в таблице никак не связана с буквенными обозначениями на графе. "
        f"Определите длину дороги из пункта {LETTERS[first]} в пункт {LETTERS[second]}. В ответе запишите целое число.",
        dec(weights[(first, second)]),
        f"Пункты сопоставляются по числу дорог, выходящих из них. Пункт {LETTERS[first]} это П{numbering[first] + 1}, пункт {LETTERS[second]} это П{numbering[second] + 1}; "
        f"длина дороги между ними {weights[(first, second)]} км.",
        fig,
    )


# ---------------------------------------------------------------- №2 Таблицы истинности


def implies(a, b):
    return (not a) or b


EXPRESSIONS = [
    ("({0} → {1}) ∧ ({1} → {2}) ∧ ({2} → {3})", lambda a, b, c, d: implies(a, b) and implies(b, c) and implies(c, d)),
    ("({0} ∧ ¬{1}) ∨ ({2} ≡ {3})", lambda a, b, c, d: (a and not b) or (c == d)),
    ("¬({0} → {1}) ∨ ({2} ∧ ¬{3})", lambda a, b, c, d: (not implies(a, b)) or (c and not d)),
    ("({0} ∨ {1}) → ({2} ∧ {3})", lambda a, b, c, d: implies(a or b, c and d)),
    ("({0} ≡ {1}) ∧ (¬{2} ∨ {3})", lambda a, b, c, d: (a == b) and ((not c) or d)),
    ("(({0} → {1}) ∧ {2}) ∨ ¬{3}", lambda a, b, c, d: (implies(a, b) and c) or not d),
    ("({0} ∨ ¬{1}) ∧ ({2} → {3}) ∧ ¬({0} ∧ {3})", lambda a, b, c, d: (a or not b) and implies(c, d) and not (a and d)),
    ("(¬{0} ∧ {1}) ∨ ({2} ∧ {3}) ∨ ({0} ∧ ¬{2})", lambda a, b, c, d: ((not a) and b) or (c and d) or (a and not c)),
    ("({0} → ({1} ∧ {2})) ∧ ({3} ∨ ¬{1})", lambda a, b, c, d: implies(a, b and c) and (d or not b)),
    ("({0} ∧ {1}) ∨ (¬{2} → {3}) ∧ ¬{0}", lambda a, b, c, d: (a and b) or (implies(not c, d) and not a)),
]


def l_truth_table(r):
    names = "wxyz"
    while True:
        template, function = r.choice(EXPRESSIONS)
        roles = r.sample(range(4), 4)  # какая переменная стоит на каждом месте шаблона
        value = r.choice([False, True])
        rows = [bits for bits in product((0, 1), repeat=4) if bool(function(*(bits[role] for role in roles))) == value]
        if not 2 <= len(rows) <= 5:
            continue
        columns = r.sample(range(4), 4)  # в столбце j стоит переменная columns[j]
        shown = sorted(tuple(bits[column] for column in columns) for bits in rows)
        fits = [p for p in permutations(range(4)) if sorted(tuple(bits[column] for column in p) for bits in rows) == shown]
        if len(fits) == 1:
            break
    r.shuffle(shown)
    table = [["Перем. 1", "Перем. 2", "Перем. 3", "Перем. 4", "F"]] + [[str(bit) for bit in row] + [str(int(value))] for row in shown]
    expression = template.format(*(names[role] for role in roles))
    answer = "".join(names[column] for column in columns)
    return exact(task(
        f"Логическая функция F задаётся выражением {expression}. На рисунке приведён фрагмент таблицы истинности функции F, содержащий все наборы аргументов, "
        f"при которых функция {'истинна' if value else 'ложна'}. Определите, какому столбцу таблицы соответствует каждая из переменных w, x, y, z. "
        "В ответе запишите буквы w, x, y, z в том порядке, в котором идут соответствующие им столбцы, без пробелов и запятых.",
        answer,
        f"Функция {'истинна' if value else 'ложна'} на {len(rows)} наборах; сравнивая их со строками таблицы, получаем порядок столбцов {answer}.",
        table_figure(table, cell_width=72, cell_height=32, first_width=72),
    ))


# ---------------------------------------------------------------- №4 Кодирование и декодирование


def c_fano(r):
    while True:
        count = r.choice([4, 5, 6])
        leaves = [""]
        while len(leaves) < count + 1:
            leaf = r.choice(leaves)
            if len(leaf) < 4:
                leaves.remove(leaf)
                leaves += [leaf + "0", leaf + "1"]
        known = r.sample(leaves, count - 1)
        candidates = ["".join(bits) for length in range(1, 6) for bits in product("01", repeat=length)]
        free = [code for code in candidates if not any(code.startswith(k) or k.startswith(code) for k in known)]
        shortest = [code for code in free if len(code) == len(free[0])]
        if len(free[0]) >= 2:
            break
    letters = LETTERS[:count]
    codes = ", ".join(f"{letter}: {code}" for letter, code in zip(letters, sorted(known, key=lambda code: (len(code), code))))
    return exact(task(
        f"Для кодирования некоторой последовательности, состоящей из букв {', '.join(letters)}, решили использовать неравномерный двоичный код, удовлетворяющий условию Фано. "
        f"Для букв использовали такие кодовые слова: {codes}. Укажите кратчайшее кодовое слово для буквы {letters[-1]}, при котором код будет удовлетворять условию Фано. "
        "Если таких кодов несколько, укажите код с наименьшим числовым значением.",
        shortest[0],
        f"Кодовое слово не должно быть началом другого и не должно начинаться с другого кодового слова. Кратчайшее подходящее слово: {shortest[0]}.",
    ))


def c_fano_total(r):
    while True:
        count, known_count = r.choice([5, 6, 7]), r.choice([2, 3])
        leaves = [""]
        while len(leaves) < known_count + 1:
            leaf = r.choice(leaves)
            if len(leaf) < 3:
                leaves.remove(leaf)
                leaves += [leaf + "0", leaf + "1"]
        known = sorted(r.sample(leaves, known_count), key=lambda code: (len(code), code))
        free_root = [leaf for leaf in leaves if leaf not in known][0]
        rest = count - known_count
        if rest >= 3:
            break
    # Остальные буквы кодируются словами, начинающимися со свободной ветви: нужна наименьшая сумма длин.
    best = min_total(rest) + rest * len(free_root)
    letters = "АБВГДЕЖ"[:count]
    codes = ", ".join(f"{letter}: {code}" for letter, code in zip(letters, known))
    return task(
        f"По каналу связи передаются сообщения, содержащие только буквы {', '.join(letters)}. Для передачи используется двоичный код, удовлетворяющий условию Фано. "
        f"Кодовые слова для некоторых букв известны: {codes}. Какое наименьшее количество двоичных знаков потребуется для кодирования остальных букв? "
        "В ответе запишите суммарную длину кодовых слов для этих букв.",
        dec(best),
        f"Свободна только ветвь, начинающаяся с {free_root}. На ней нужно разместить кодовые слова для остальных букв (их {rest}); наименьшая сумма длин равна {best}.",
    )


def min_total(count):
    """Наименьшая сумма длин count кодовых слов префиксного кода (длины отсчитываются от корня свободной ветви)."""
    if count == 1:
        return 0
    return min(min_total(left) + min_total(count - left) + count for left in range(1, count // 2 + 1))


# ---------------------------------------------------------------- №5 Алгоритмы для исполнителей


def parity_algorithm(number):
    bits = bin(number)[2:]
    bits += str(bits.count("1") % 2)
    bits += str(bits.count("1") % 2)
    return int(bits, 2)


def replace_algorithm(number):
    bits = bin(number)[2:]
    if bits.count("1") % 2 == 0:
        bits = "10" + (bits + "0")[2:]
    else:
        bits = "11" + (bits + "1")[2:]
    return int(bits, 2)


ALGORITHMS = [
    (parity_algorithm,
     "1. Строится двоичная запись числа N.\n2. К этой записи справа дописывается остаток от деления суммы её цифр на 2.\n"
     "3. С полученной записью ещё раз выполняется действие из пункта 2.\nПолученная таким образом запись является двоичной записью искомого числа R."),
    (replace_algorithm,
     "1. Строится двоичная запись числа N.\n2. Если сумма цифр двоичной записи чётная, то к записи справа дописывается 0, а затем два левых разряда заменяются на 10. "
     "Если сумма цифр нечётная, то к записи справа дописывается 1, а затем два левых разряда заменяются на 11.\n"
     "Полученная таким образом запись является двоичной записью искомого числа R."),
]


def a_binary(r):
    function, steps = r.choice(ALGORITHMS)
    limit = r.randint(40, 220)
    results = {n: function(n) for n in range(4, 600)}
    intro = f"На вход алгоритма подаётся натуральное число N. Алгоритм строит по нему новое число R следующим образом.\n{steps}\n"
    if r.random() < 0.5:
        answer = min(value for value in results.values() if value > limit)
        return task(intro + f"Укажите минимальное число R, которое превышает число {limit} и может являться результатом работы этого алгоритма. В ответе запишите это число в десятичной системе счисления.",
                    dec(answer), f"Перебирая числа N по возрастанию, получаем наименьший результат, превышающий {limit}: R = {answer}.")
    answer = min(n for n, value in results.items() if value > limit)
    return task(intro + f"Укажите минимальное число N, для которого результат работы алгоритма больше числа {limit}. В ответе запишите это число в десятичной системе счисления.",
                dec(answer), f"При N = {answer} получается R = {results[answer]}, это первое значение N, для которого R больше {limit}.")


# ---------------------------------------------------------------- №6 Результат работы простейших алгоритмов

TURTLE = ("Исполнитель Черепаха действует на плоскости с декартовой системой координат. В начальный момент Черепаха находится в начале координат, "
          "её голова направлена вдоль положительного направления оси ординат, хвост опущен. При опущенном хвосте Черепаха оставляет на поле след в виде линии. "
          "Команда «Вперёд n» перемещает Черепаху на n единиц в направлении головы, «Направо m» поворачивает её на m градусов по часовой стрелке, "
          "«Налево m» поворачивает против часовой стрелки, «Поднять хвост» и «Опустить хвост» поднимают и опускают хвост. "
          "Запись «Повтори k [Команда1 Команда2 … ]» означает, что команды в скобках повторятся k раз.\n\n")


def t_rectangle(r):
    height, width = r.randint(3, 14), r.randint(3, 14)
    program = f"Повтори 4 [Вперёд {height} Направо 90 Вперёд {width} Направо 90]"
    if r.random() < 0.5:
        return task(
            TURTLE + f"Черепахе был дан для исполнения следующий алгоритм:\n{program}\n\nОпределите, сколько точек с целочисленными координатами находятся внутри области, "
            "ограниченной линией, заданной этим алгоритмом. Точки на линии учитывать не следует.",
            dec((height - 1) * (width - 1)), f"Черепаха рисует прямоугольник {width} × {height}. Точек внутри него: ({width} - 1) · ({height} - 1) = {(height - 1) * (width - 1)}.")
    return task(
        TURTLE + f"Черепахе был дан для исполнения следующий алгоритм:\n{program}\n\nОпределите, сколько точек с целочисленными координатами лежат на линии, "
        "заданной этим алгоритмом.",
        dec(2 * (height + width)), f"Черепаха рисует прямоугольник {width} × {height}. Точек на его границе: 2 · ({width} + {height}) = {2 * (height + width)}.")


def t_two_rectangles(r):
    while True:
        height, width = r.randint(5, 12), r.randint(5, 12)
        up, right = r.randint(1, height - 2), r.randint(1, width - 2)
        second_height, second_width = r.randint(3, 12), r.randint(3, 12)
        overlap_x = min(width, right + second_width) - right
        overlap_y = min(height, up + second_height) - up
        if overlap_x >= 2 and overlap_y >= 2 and (right + second_width > width or up + second_height > height):
            break
    program = (f"Повтори 2 [Вперёд {height} Направо 90 Вперёд {width} Направо 90]\nПоднять хвост\nВперёд {up} Направо 90 Вперёд {right} Налево 90\nОпустить хвост\n"
               f"Повтори 2 [Вперёд {second_height} Направо 90 Вперёд {second_width} Направо 90]")
    if r.random() < 0.5:
        return task(
            TURTLE + f"Черепахе был дан для исполнения следующий алгоритм:\n{program}\n\nОпределите, сколько точек с целочисленными координатами находятся внутри пересечения фигур, "
            "ограниченных заданными алгоритмом линиями. Точки на линиях учитывать не следует.",
            dec((overlap_x - 1) * (overlap_y - 1)),
            f"Пересечение двух прямоугольников это прямоугольник {overlap_x} × {overlap_y}; точек внутри него: {(overlap_x - 1) * (overlap_y - 1)}.")
    return task(
        TURTLE + f"Черепахе был дан для исполнения следующий алгоритм:\n{program}\n\nОпределите, сколько точек с целочисленными координатами находятся внутри пересечения фигур, "
        "ограниченных заданными алгоритмом линиями, включая точки на границах этого пересечения.",
        dec((overlap_x + 1) * (overlap_y + 1)),
        f"Пересечение двух прямоугольников это прямоугольник {overlap_x} × {overlap_y}; точек в нём вместе с границей: {(overlap_x + 1) * (overlap_y + 1)}.")


# ---------------------------------------------------------------- №7 Кодирование изображений и звука. Передача информации


def i_image(r):
    width, height = r.choice([64, 128, 256, 512, 1024]), r.choice([64, 128, 256, 512, 1024])
    depth = r.choice([2, 3, 4, 5, 6, 7, 8])
    kilobytes = width * height * depth // 8 // 1024
    if width * height * depth % (8 * 1024):
        return i_image(r)
    if r.random() < 0.5:
        colors = r.randint(2 ** (depth - 1) + 1, 2 ** depth)
        return task(
            f"Какой минимальный объём памяти (в Кбайт) нужно зарезервировать, чтобы можно было сохранить любое растровое изображение размером {width} на {height} пикселей "
            f"при условии, что в изображении могут использоваться {colors} различных цветов? В ответе запишите только целое число.",
            dec(kilobytes), f"Для {colors} цветов нужно {depth} бит на пиксель: {width} · {height} · {depth} бит = {kilobytes} Кбайт.")
    return task(
        f"Для хранения произвольного растрового изображения размером {width} на {height} пикселей отведено {kilobytes} Кбайт памяти без учёта размера заголовка файла. "
        "Для кодирования цвета каждого пикселя используется одинаковое количество бит, коды пикселей записываются в файл один за другим без промежутков. "
        "Какое максимальное количество цветов можно использовать в изображении?",
        dec(2 ** depth), f"На один пиксель приходится {kilobytes} · 1024 · 8 : ({width} · {height}) = {depth} бит, цветов не больше 2 в степени {depth}, то есть {2 ** depth}.")


def i_sound(r):
    channels, name = r.choice([(1, "одноканальная (моно)"), (2, "двухканальная (стерео)"), (4, "четырёхканальная (квадро)")])
    rate, depth, minutes = r.choice([16, 32, 48, 64]), r.choice([16, 24, 32]), r.choice([1, 2, 3, 4, 5])
    size = channels * rate * 1000 * depth * minutes * 60 / 8 / 2 ** 20
    return task(
        f"Производится {name} звукозапись с частотой дискретизации {rate} кГц и {depth}-битным разрешением. Запись длится {plural(minutes, 'минуту', 'минуты', 'минут')}, "
        "её результаты записываются в файл, сжатие данных не производится. Определите приблизительно размер полученного файла в Мбайт. "
        "В ответе укажите ближайшее к размеру файла целое число.",
        dec(round(size)), f"{channels} · {rate * 1000} · {depth} · {minutes * 60} бит это примерно {dec(round(size))} Мбайт.")


def times(number) -> str:
    return f"в {number} раза" if number in (2, 3, 4) else f"в {number} раз"


def i_transfer(r):
    while True:
        first, seconds = r.choice([64, 128, 256, 512]), r.choice([8, 16, 32, 64])
        bigger, faster = r.choice([2, 4, 8, 16]), r.choice([2, 4, 8])
        if bigger != faster and seconds * bigger % faster == 0:
            break
    answer = seconds * bigger // faster
    return task(
        f"Файл размером {first} Кбайт передаётся через некоторое соединение за {plural(seconds, 'секунду', 'секунды', 'секунд')}. За сколько секунд можно передать файл размером {first * bigger} Кбайт "
        f"через другое соединение, скорость которого {times(faster)} выше? В ответе укажите одно число.",
        dec(answer), f"Файл больше {times(bigger)}, а скорость выше {times(faster)}: {seconds} · {bigger} : {faster} = {answer} с.")


# ---------------------------------------------------------------- №8 Перебор слов и системы счисления

ALPHABETS = ["АКРУ", "АОУ", "ЕЛМР", "АИСТ", "ГДЕ", "КОТ", "АЛМО", "ВИНТ", "ЕНТ", "АПРЯ"]


def w_position(r):
    alphabet = "".join(sorted(r.choice(ALPHABETS)))
    length = 5 if len(alphabet) == 3 else r.choice([4, 5])
    words = ["".join(letters) for letters in product(alphabet, repeat=length)]
    index = r.randrange(len(alphabet) ** (length - 2), len(words))
    head = f"Все {length}-буквенные слова, составленные из букв {', '.join(alphabet)}, записаны в алфавитном порядке и пронумерованы, начиная с 1. Начало списка: 1. {words[0]}, 2. {words[1]}, 3. {words[2]}, 4. {words[3]}, … "
    if r.random() < 0.5:
        return exact(task(head + f"Запишите слово, которое стоит под номером {index + 1}.", words[index],
                          f"Номер {index + 1} соответствует числу {index} в системе счисления с основанием {len(alphabet)}; заменяя цифры буквами, получаем {words[index]}."))
    return task(head + f"Под каким номером в списке стоит слово {words[index]}?", dec(index + 1),
                f"Заменяя буквы цифрами по алфавиту, получаем число в системе счисления с основанием {len(alphabet)}; оно равно {index}, номер слова на единицу больше.")


def w_count(r):
    letters = r.choice(["ТИМУР", "ВЕСНА", "КАТЕР", "ПОЛЕТ", "СОЛНЦЕ", "МАРТ", "ГРОЗА"])
    letters = "".join(dict.fromkeys(letters))
    length = r.choice([3, 4]) if len(letters) > 5 else r.choice([3, 4, 5])
    vowels = set("АЕИОУ")
    special = letters[0]
    rules = [
        (f"буква {special} встречается ровно один раз", lambda word: word.count(special) == 1),
        ("буквы не повторяются", lambda word: len(set(word)) == len(word)),
        ("слово не начинается с гласной буквы", lambda word: word[0] not in vowels),
        ("никакие две одинаковые буквы не стоят рядом", lambda word: all(a != b for a, b in zip(word, word[1:]))),
        (f"буква {special} встречается хотя бы один раз", lambda word: special in word),
    ]
    text, rule = r.choice(rules)
    if "не повторяются" in text and length > len(letters):
        return w_count(r)
    answer = sum(1 for word in product(letters, repeat=length) if rule(word))
    return task(
        f"Сколько существует различных кодовых слов длиной {length}, составленных из букв {', '.join(letters)}, в которых {text}? "
        "Остальные буквы могут встречаться любое количество раз или не встречаться совсем, если это не противоречит условию.",
        dec(answer), f"Подсчёт по правилам комбинаторики (или перебором) даёт {answer}.")


# ---------------------------------------------------------------- №10 Компьютерные сети. Адресация

MASK_BYTES = [0, 128, 192, 224, 240, 248, 252, 254, 255]


def n_network_byte(r):
    address = [r.randint(10, 220), r.randint(0, 255), r.randint(17, 250), r.randint(1, 254)]
    mask = r.choice([192, 224, 240, 248, 252])
    return task(
        f"В терминологии сетей TCP/IP маской сети называют двоичное число, которое показывает, какая часть IP-адреса узла относится к адресу сети, а какая к адресу узла в этой сети. "
        f"Адрес сети получается в результате применения поразрядной конъюнкции к заданному адресу узла и маске сети. Узел имеет IP-адрес {'.'.join(map(str, address))}, "
        f"маска сети равна 255.255.{mask}.0. Чему равен третий слева байт адреса сети? Ответ запишите в виде десятичного числа.",
        dec(address[2] & mask), f"{address[2]} = {address[2]:08b}₂, {mask} = {mask:08b}₂; поразрядная конъюнкция даёт {address[2] & mask:08b}₂ = {address[2] & mask}.")


def n_mask_byte(r):
    while True:
        third, mask = r.randint(17, 250), r.choice([192, 224, 240, 248, 252])
        network = third & mask
        fits = [m for m in MASK_BYTES if third & m == network and m != 0]
        if len(fits) >= 2 and network != third:
            break
    first, second, fourth = r.randint(10, 220), r.randint(0, 255), r.randint(1, 254)
    smallest = r.random() < 0.5
    return task(
        "В терминологии сетей TCP/IP маской сети называют двоичное число, которое показывает, какая часть IP-адреса узла относится к адресу сети, а какая к адресу узла в этой сети. "
        "Адрес сети получается в результате применения поразрядной конъюнкции к заданному адресу узла и маске сети. "
        f"Для узла с IP-адресом {first}.{second}.{third}.{fourth} адрес сети равен {first}.{second}.{network}.0. "
        f"Чему равно {'наименьшее' if smallest else 'наибольшее'} возможное значение третьего слева байта маски? Ответ запишите в виде десятичного числа.",
        dec(min(fits) if smallest else max(fits)),
        f"{third} = {third:08b}₂, {network} = {network:08b}₂. Подходят значения байта маски: {', '.join(map(str, fits))}.")


def n_hosts(r):
    mask = r.choice([128, 192, 224, 240, 248, 252])
    zeros = 8 - bin(mask).count("1")
    if r.random() < 0.5:
        return task(
            f"Сеть задана маской 255.255.255.{mask}. Сколько различных адресов компьютеров теоретически допускает эта маска, если два адреса "
            "(адрес сети и широковещательный адрес) не используют?",
            dec(2 ** zeros - 2), f"В маске {zeros} нулевых бит: 2 в степени {zeros} равно {2 ** zeros}, минус два служебных адреса: {2 ** zeros - 2}.")
    third = r.choice([128, 192, 224, 240, 248, 252, 254])
    return task(
        f"Маска сети равна 255.255.{third}.0. Сколько единиц содержится в двоичной записи этой маски?",
        dec(16 + bin(third).count("1")), f"В первых двух байтах 16 единиц, в байте {third} = {third:08b}₂ их {bin(third).count('1')}: всего {16 + bin(third).count('1')}.")


# ---------------------------------------------------------------- №11 Количество информации


def p_passwords(r):
    length, alphabet = r.randint(7, 25), r.choice([5, 7, 10, 12, 18, 26, 30, 36, 52, 62, 100, 1000])
    bits = max(1, math.ceil(math.log2(alphabet)))
    size = math.ceil(length * bits / 8)
    users = r.choice([20, 25, 40, 50, 100, 200])
    intro = (f"При регистрации в компьютерной системе каждому пользователю выдаётся пароль, состоящий из {length} символов. В качестве символов используют "
             f"символы из {alphabet}-символьного набора. В базе данных для хранения сведений о каждом пользователе отведено одинаковое и минимально возможное целое число байт. "
             "При этом используют посимвольное кодирование паролей, все символы кодируют одинаковым и минимально возможным количеством бит. ")
    if r.random() < 0.5:
        return task(intro + f"Определите объём памяти (в байтах), необходимый для хранения паролей {users} пользователей. В ответе запишите только целое число.",
                    dec(size * users), f"На символ нужно {bits} бит, на пароль {length} · {bits} = {length * bits} бит, то есть {size} байт; на {users} пользователей {size * users} байт.")
    extra = r.randint(4, 30)
    return task(intro + f"Кроме пароля, для каждого пользователя в системе хранятся дополнительные сведения, для которых отведено целое число байт, одинаковое для всех. "
                f"Для хранения сведений о {users} пользователях потребовалось {(size + extra) * users} байт. Сколько байт выделено для хранения дополнительных сведений об одном пользователе?",
                dec(extra), f"На пароль нужно {size} байт. На одного пользователя приходится {(size + extra) * users} : {users} = {size + extra} байт, дополнительных сведений {extra} байт.")


# ---------------------------------------------------------------- №12 Исполнители: Редактор

EDITOR = ("Исполнитель Редактор получает на вход строку цифр и преобразовывает её. Команда заменить (v, w) заменяет в строке первое слева вхождение цепочки v на цепочку w. "
          "Команда нашлось (v) проверяет, встречается ли цепочка v в строке. ")


def run_editor(string, first, second):
    steps = 0
    while first * 3 in string or second * 3 in string:
        if first * 3 in string:
            string = string.replace(first * 3, second, 1)
        else:
            string = string.replace(second * 3, first, 1)
        steps += 1
        if steps > 2000:
            return None
    return string


def e_editor(r):
    while True:
        first, second = r.sample("123456789", 2)
        count = r.randint(18, 99)
        start = r.choice([first, second])
        result = run_editor(start * count, first, second)
        if result and len(result) <= 8:
            break
    program = (f"ПОКА нашлось ({first * 3}) ИЛИ нашлось ({second * 3})\n  ЕСЛИ нашлось ({first * 3})\n    ТО заменить ({first * 3}, {second})\n"
               f"    ИНАЧЕ заменить ({second * 3}, {first})\n  КОНЕЦ ЕСЛИ\nКОНЕЦ ПОКА")
    return exact(task(
        EDITOR + f"Дана программа для Редактора:\n\nНАЧАЛО\n{program}\nКОНЕЦ\n\nКакая строка получится в результате применения этой программы к строке, "
        f"состоящей из {count} идущих подряд цифр {start}? В ответе запишите полученную строку.",
        result, f"Строка сокращается, пока в ней есть три одинаковые цифры подряд. В результате остаётся строка {result}."))


def run_pairs(string, rules):
    steps = 0
    while any(pattern in string for pattern, _ in rules):
        for pattern, replacement in rules:
            if pattern in string:
                string = string.replace(pattern, replacement, 1)
                break
        steps += 1
        if steps > 3000:
            return None
    return string


def e_editor_sum(r):
    while True:
        ones, twos, threes = r.randint(5, 20), r.randint(5, 20), r.randint(5, 20)
        rules = r.choice([[("31", "13"), ("32", "23"), ("21", "12")], [("13", "31"), ("23", "32"), ("12", "21")]])
        digits = ["1"] * ones + ["2"] * twos + ["3"] * threes
        r.shuffle(digits)
        position = r.choice([10, 15, 20, 25])
        if ones + twos + threes > position + 3:
            break
    result = run_pairs("".join(digits), rules)
    program = "ПОКА " + " ИЛИ ".join(f"нашлось ({p})" for p, _ in rules) + "\n" + "\n".join(
        f"  ЕСЛИ нашлось ({p}) ТО заменить ({p}, {q}) КОНЕЦ ЕСЛИ" for p, q in rules) + "\nКОНЕЦ ПОКА"
    return task(
        EDITOR + f"Дана программа для Редактора:\n\nНАЧАЛО\n{program}\nКОНЕЦ\n\nНа вход программе подана строка длиной {ones + twos + threes}, в которой {ones} цифр 1, {twos} цифр 2 и {threes} цифр 3, "
        f"расположенных в произвольном порядке. Какая цифра окажется на {position}-м месте в строке, полученной в результате работы программы? Места нумеруются слева направо, начиная с 1.",
        result[position - 1],
        f"Программа сортирует цифры: в итоговой строке они идут {'по возрастанию' if rules[0][0] == '31' else 'по убыванию'}. На {position}-м месте стоит цифра {result[position - 1]}.")


# ---------------------------------------------------------------- №13 Перебор вариантов, построение дерева


def count_programs(start, goal, moves, required=None, banned=None):
    ways = {start: 1}
    for number in range(start + 1, goal + 1):
        if number == banned:
            ways[number] = 0
            continue
        ways[number] = sum(ways.get(previous, 0) for move in moves for previous in [move(number)] if previous is not None)
    if required is None:
        return ways[goal]
    return ways[required] * count_programs(required, goal, moves, None, banned)


COMMANDS = [
    (["Прибавить 1", "Умножить на 2"], [lambda n: n - 1, lambda n: n // 2 if n % 2 == 0 else None]),
    (["Прибавить 1", "Прибавить 2", "Умножить на 3"], [lambda n: n - 1, lambda n: n - 2, lambda n: n // 3 if n % 3 == 0 else None]),
    (["Прибавить 1", "Умножить на 3"], [lambda n: n - 1, lambda n: n // 3 if n % 3 == 0 else None]),
    (["Прибавить 2", "Умножить на 2"], [lambda n: n - 2, lambda n: n // 2 if n % 2 == 0 else None]),
    (["Прибавить 1", "Прибавить 3", "Умножить на 2"], [lambda n: n - 1, lambda n: n - 3, lambda n: n // 2 if n % 2 == 0 else None]),
]


def g_programs(r):
    while True:
        names, moves = r.choice(COMMANDS)
        start, goal = r.randint(1, 4), r.randint(14, 34)
        required = r.choice([None, r.randint(start + 3, goal - 3)])
        banned = r.choice([None, r.randint(start + 2, goal - 2)])
        if required is not None and banned == required:
            continue
        answer = count_programs(start, goal, moves, required, banned)
        if 6 <= answer <= 600:
            break
    commands = "\n".join(f"{index + 1}. {name}" for index, name in enumerate(names))
    condition = ""
    if required is not None:
        condition += f" и при этом траектория вычислений содержит число {required}"
    if banned is not None:
        condition += f"{' и' if required is not None else ' и при этом траектория вычислений'} не содержит числа {banned}"
    return task(
        f"Исполнитель преобразует число на экране. У исполнителя есть команды, которым присвоены номера:\n{commands}\n\n"
        f"Программа для исполнителя это последовательность команд. Сколько существует программ, для которых при исходном числе {start} результатом является число {goal}{condition}? "
        "Траектория вычислений программы это последовательность результатов выполнения всех команд программы.",
        dec(answer), f"Считаем количество программ для каждого числа по порядку, складывая количества для чисел, из которых в него можно попасть. Получается {answer}.")


# ---------------------------------------------------------------- №14 Системы счисления


def digits_in_base(number, base):
    digits = []
    while number:
        digits.append(number % base)
        number //= base
    return digits[::-1]


def y_expression(r):
    base, square = r.choice([(2, 4), (3, 9), (5, 25), (2, 8), (7, 49)])
    high, low, minus = r.randint(8, 40), r.randint(5, 30), r.randint(2, 60)
    value = square ** high + base ** low - minus
    digits = digits_in_base(value, base)
    if base == 2:
        what, answer = r.choice([("единиц", digits.count(1)), ("значащих нулей", digits.count(0))])
    else:
        what, answer = f"цифр {base - 1}", digits.count(base - 1)
    if value <= 0 or answer == 0:
        return y_expression(r)
    return task(
        f"Значение арифметического выражения {square}^{high} + {base}^{low} - {minus} записали в системе счисления с основанием {base}. "
        f"Сколько {what} содержится в этой записи? Знак ^ обозначает возведение в степень.",
        dec(answer), f"Приводим всё к степеням числа {base} и вычитаем в столбик в системе с основанием {base}. Таких цифр в записи: {answer}.")


def y_unknown_digit(r):
    while True:
        base = r.choice([12, 13, 15, 17, 19])
        divisor = r.choice([base - 1, base + 1, 7, 9, 11, 13])
        template_first = [r.randrange(1, base), None, r.randrange(base), r.randrange(base)]
        template_second = [r.randrange(1, base), r.randrange(base), None]

        def value(x):
            first = sum(digit * base ** power for power, digit in enumerate(reversed([x if d is None else d for d in template_first])))
            second = sum(digit * base ** power for power, digit in enumerate(reversed([x if d is None else d for d in template_second])))
            return first + second

        fits = [x for x in range(base) if value(x) % divisor == 0]
        if len(fits) == 1 and divisor != base:
            break

    def show(template):
        return "".join("x" if d is None else "0123456789ABCDEFGHIJ"[d] for d in template)

    x = fits[0]
    return task(
        f"Операнды арифметического выражения записаны в системе счисления с основанием {base}: {show(template_first)} + {show(template_second)}. "
        f"В записи чисел переменной x обозначена неизвестная цифра из алфавита {base}-ричной системы счисления (цифры после 9 обозначаются буквами A, B, C, …). "
        f"Определите значение x, при котором значение данного выражения кратно {divisor}. Для найденного x вычислите частное от деления значения выражения на {divisor} "
        "и запишите его в ответе в десятичной системе счисления.",
        dec(value(x) // divisor), f"Перебирая цифры, находим x = {x}; значение выражения равно {value(x)}, частное равно {value(x) // divisor}.")


# ---------------------------------------------------------------- №15 Преобразование логических выражений


def b_divisibility(r):
    first, second = r.choice([(6, 9), (4, 6), (6, 10), (9, 12), (8, 12), (10, 15), (6, 14), (12, 18), (14, 21), (15, 20), (9, 15), (6, 21), (10, 14), (12, 20)])
    common = first * second // math.gcd(first, second)
    intro = "Обозначим через ДЕЛ(n, m) утверждение «натуральное число n делится без остатка на натуральное число m». "
    if r.random() < 0.5:
        return task(
            intro + f"Для какого наибольшего натурального числа A формула ¬ДЕЛ(x, A) → (ДЕЛ(x, {first}) → ¬ДЕЛ(x, {second})) тождественно истинна, "
            "то есть принимает значение 1 при любом натуральном значении переменной x?",
            dec(common), f"Формула равносильна утверждению «если x делится на {first} и на {second}, то x делится на A». Наибольшее такое A это НОК({first}, {second}) = {common}.")
    return task(
        intro + f"Для какого наименьшего натурального числа A формула ДЕЛ(x, A) → (ДЕЛ(x, {first}) ∧ ДЕЛ(x, {second})) тождественно истинна, "
        "то есть принимает значение 1 при любом натуральном значении переменной x?",
        dec(common), f"Всякое число, кратное A, должно делиться на {first} и на {second}; наименьшее такое A это НОК({first}, {second}) = {common}.")


def b_inequality(r):
    if r.random() < 0.5:
        factor, bound = r.choice([2, 3, 4]), r.randint(8, 40)
        return task(
            f"Для какого наименьшего целого неотрицательного числа A выражение (x + {factor}y < A) ∨ (y > x) ∨ (x > {bound}) тождественно истинно, "
            "то есть принимает значение 1 при любых целых неотрицательных x и y?",
            dec((factor + 1) * bound + 1),
            f"Первое неравенство обязано выполняться при y ≤ x ≤ {bound}. Наибольшее значение x + {factor}y равно {(factor + 1) * bound}, поэтому A = {(factor + 1) * bound + 1}.")
    first, second = r.randint(5, 30), r.randint(5, 30)
    return task(
        f"Для какого наименьшего целого неотрицательного числа A выражение (x · y < A) ∨ (x > {first}) ∨ (y > {second}) тождественно истинно, "
        "то есть принимает значение 1 при любых целых неотрицательных x и y?",
        dec(first * second + 1),
        f"Неравенство x · y < A обязано выполняться при x ≤ {first} и y ≤ {second}. Наибольшее произведение равно {first * second}, поэтому A = {first * second + 1}.")


def b_segments(r):
    while True:
        p_start, q_start = r.randint(2, 40), r.randint(2, 40)
        p_end, q_end = p_start + r.randint(8, 40), q_start + r.randint(8, 40)
        overlap = min(p_end, q_end) - max(p_start, q_start)
        if overlap >= 3 and (p_start, p_end) != (q_start, q_end):
            break
    intro = f"На числовой прямой даны два отрезка: P = [{p_start}; {p_end}] и Q = [{q_start}; {q_end}]. "
    if r.random() < 0.5:
        return task(
            intro + "Укажите наименьшую возможную длину такого отрезка A, для которого логическое выражение (x ∈ P) → (((x ∈ Q) ∧ ¬(x ∈ A)) → ¬(x ∈ P)) "
            "тождественно истинно, то есть принимает значение 1 при любом значении переменной x.",
            dec(overlap), f"Выражение ложно только для x из P и Q, не входящих в A. Значит, A должен содержать пересечение отрезков [{max(p_start, q_start)}; {min(p_end, q_end)}] длиной {overlap}.")
    union = max(p_end, q_end) - min(p_start, q_start)
    return task(
        intro + "Укажите наибольшую возможную длину такого отрезка A, для которого логическое выражение (x ∈ A) → ((x ∈ P) ∨ (x ∈ Q)) "
        "тождественно истинно, то есть принимает значение 1 при любом значении переменной x.",
        dec(union), f"Отрезок A должен целиком лежать в объединении P и Q. Отрезки пересекаются, их объединение [{min(p_start, q_start)}; {max(p_end, q_end)}] имеет длину {union}.")


# ---------------------------------------------------------------- №16 Рекурсивные алгоритмы


def f_recursion(r):
    kind = r.choice(["linear", "parity", "pair"])
    if kind == "linear":
        factor, target = r.choice([2, 3]), r.randint(6, 9)
        values = [1, 1]
        for n in range(2, target + 1):
            values.append(values[n - 1] + factor * values[n - 2])
        return task(
            f"Алгоритм вычисления значения функции F(n), где n целое неотрицательное число, задан следующими соотношениями:\nF(n) = 1 при n ≤ 1;\n"
            f"F(n) = F(n - 1) + {factor} · F(n - 2) при n > 1.\nЧему равно значение функции F({target})?",
            dec(values[target]), "Вычисляем по порядку: " + ", ".join(f"F({n}) = {values[n]}" for n in range(2, target + 1)) + ".")
    if kind == "parity":
        add, target = r.randint(1, 4), r.randint(7, 12)
        values = {1: 1, 2: 2}
        for n in range(3, target + 1):
            values[n] = values[n - 1] + n if n % 2 == 0 else 2 * values[n - 2] + add
        return task(
            f"Алгоритм вычисления значения функции F(n), где n натуральное число, задан следующими соотношениями:\nF(n) = n при n ≤ 2;\n"
            f"F(n) = F(n - 1) + n, если n > 2 и n чётное;\nF(n) = 2 · F(n - 2) + {add}, если n > 2 и n нечётное.\nЧему равно значение функции F({target})?",
            dec(values[target]), "Вычисляем по порядку: " + ", ".join(f"F({n}) = {values[n]}" for n in range(3, target + 1)) + ".")
    factor, target = r.choice([2, 3]), r.randint(4, 7)
    f_values, g_values = {1: 1}, {1: 1}
    for n in range(2, target + 1):
        f_values[n] = f_values[n - 1] + factor * g_values[n - 1]
        g_values[n] = g_values[n - 1] + n
    return task(
        f"Алгоритмы вычисления значений функций F(n) и G(n), где n натуральное число, заданы следующими соотношениями:\nF(1) = 1, G(1) = 1;\n"
        f"F(n) = F(n - 1) + {factor} · G(n - 1) при n > 1;\nG(n) = G(n - 1) + n при n > 1.\nЧему равно значение функции F({target})?",
        dec(f_values[target]), "Вычисляем по порядку: " + ", ".join(f"F({n}) = {f_values[n]}, G({n}) = {g_values[n]}" for n in range(2, target + 1)) + ".")


# ---------------------------------------------------------------- №19-21 Выигрышная стратегия


def game_classes(add, factor, goal):
    """Классы позиций игры с одной кучей: выигрыш первым ходом, проигрыш первым ходом и так далее."""
    def moves(stones):
        return [stones + add, stones * factor]

    win1 = {s for s in range(1, goal) if any(m >= goal for m in moves(s))}
    lose1 = {s for s in range(1, goal) if s not in win1 and all(m in win1 for m in moves(s))}
    win2 = {s for s in range(1, goal) if s not in win1 and any(m in lose1 for m in moves(s))}
    lose2 = {s for s in range(1, goal) if s not in win1 and s not in lose1 and s not in win2 and all(m in win1 or m in win2 for m in moves(s))}
    return win1, lose1, win2, lose2


def game(r):
    while True:
        add, factor, goal = r.choice([1, 2, 3, 4]), r.choice([2, 3]), r.randint(20, 90)
        win1, lose1, win2, lose2 = game_classes(add, factor, goal)
        if lose1 and len(win2) >= 2 and lose2:
            break
    text = (
        "Два игрока, Петя и Ваня, играют в следующую игру. Перед игроками лежит куча камней. Игроки ходят по очереди, первый ход делает Петя. "
        f"За один ход игрок может добавить в кучу {plural(add, 'камень', 'камня', 'камней')} или увеличить количество камней в куче в {factor} раза. "
        f"Игра завершается в тот момент, когда количество камней в куче становится не менее {goal}. Победителем считается игрок, сделавший последний ход, "
        f"то есть первым получивший кучу, в которой {goal} или больше камней. В начальный момент в куче было S камней, 1 ≤ S ≤ {goal - 1}. ")
    return text, lose1, win2, lose2


def g_first(r):
    text, lose1, _, _ = game(r)
    return task(text + "Укажите минимальное значение S, при котором Петя не может выиграть за один ход, но при любом ходе Пети Ваня может выиграть своим первым ходом.",
                dec(min(lose1)), f"Ищем наименьшую позицию, из которой любой ход ведёт в позицию, выигрышную за один ход: S = {min(lose1)}.")


def g_second(r):
    text, _, win2, _ = game(r)
    first, second = sorted(win2)[:2]
    return exact(task(
        text + "Найдите два наименьших значения S, при которых у Пети есть выигрышная стратегия, причём Петя не может выиграть за один ход, но может выиграть своим вторым ходом "
        "независимо от того, как будет ходить Ваня. В ответе запишите найденные значения подряд, без пробела, в порядке возрастания.",
        f"{first}{second}", f"Петя должен первым ходом получить позицию, проигрышную для Вани за один ход. Наименьшие подходящие значения: {first} и {second}."))


def g_third(r):
    text, _, _, lose2 = game(r)
    return task(
        text + "Найдите минимальное значение S, при котором у Вани есть выигрышная стратегия, позволяющая ему выиграть первым или вторым ходом при любой игре Пети, "
        "и при этом у Вани нет стратегии, которая позволит ему гарантированно выиграть первым ходом.",
        dec(min(lose2)), f"Любой ход Пети из такой позиции ведёт в позицию, где ходящий выигрывает первым или вторым ходом. Наименьшее значение: S = {min(lose2)}.")


NUMBERS = [
    Entry(1, "Анализ информационных моделей", 1, [m_graph_table, figures.fig_roads]),
    Entry(2, "Таблицы истинности логических выражений", 1, [l_truth_table]),
    Entry(4, "Кодирование и декодирование информации", 1, [c_fano, c_fano_total]),
    Entry(5, "Анализ и построение алгоритмов для исполнителей", 1, [a_binary]),
    Entry(6, "Результат работы простейших алгоритмов", 1, [t_rectangle, t_two_rectangles]),
    Entry(7, "Кодирование информации. Передача информации", 1, [i_image, i_sound, i_transfer]),
    Entry(8, "Перебор слов и системы счисления", 1, [w_position, w_count]),
    Entry(10, "Компьютерные сети. Адресация", 1, [n_network_byte, n_mask_byte, n_hosts]),
    Entry(11, "Вычисление количества информации", 1, [p_passwords]),
    Entry(12, "Выполнение алгоритмов для исполнителей", 1, [e_editor, e_editor_sum]),
    Entry(13, "Перебор вариантов, построение дерева", 1, [g_programs]),
    Entry(14, "Кодирование чисел. Системы счисления", 1, [y_expression, y_unknown_digit]),
    Entry(15, "Преобразование логических выражений", 1, [b_divisibility, b_inequality, b_segments]),
    Entry(16, "Рекурсивные алгоритмы", 1, [f_recursion]),
    Entry(19, "Выигрышная стратегия. Задание 1", 1, [g_first]),
    Entry(20, "Выигрышная стратегия. Задание 2", 1, [g_second]),
    Entry(21, "Выигрышная стратегия. Задание 3", 1, [g_third]),
    Entry(23, "Анализ графов", 1, [figures.fig_paths]),
]
