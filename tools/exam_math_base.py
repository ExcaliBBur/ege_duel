"""Математика, базовый уровень: задания №1-21 по структуре ЕГЭ 2026.

Часть номеров (планиметрия, стереометрия, вычисления, уравнения, текстовые задачи) использует те же
типы задач, что и профильный экзамен, как это и бывает на настоящем ЕГЭ.
"""

import math
from fractions import Fraction

import exam_math_prof as prof
import figures
from exam_common import Entry, Plane, frac, is_finite_decimal, plural, quotient, round_half_up, table_figure
from figures import Fig
from generators import dec, poly, task


def matching(text, left, right, answer, explanation):
    """Задание на соответствие: левый столбец с буквами, правый с цифрами, ответ это цифры по порядку букв."""
    letters = "АБВГ"
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


# ---------------------------------------------------------------- №1 Простейшие текстовые задачи


def b1_packs(r):
    grams = r.choice([30, 40, 50, 60])
    people = r.randint(110, 260)
    days = r.randint(4, 9)
    total = grams * people * days
    return task(
        f"В летнем лагере на каждого участника полагается {grams} г сахара в день. В лагере {people} человек. "
        f"Сколько килограммовых пачек сахара понадобится на весь лагерь на {days} дней?",
        dec(math.ceil(total / 1000)),
        f"Нужно {grams} · {people} · {days} = {total} г, то есть {dec(Fraction(total, 1000))} кг. Пачек нужно {math.ceil(total / 1000)}.",
    )


def b1_boats(r):
    passengers = r.randrange(400, 1001, 50)
    crew = r.choice([20, 25, 30, 35])
    capacity = r.choice([50, 60, 70, 80])
    total = passengers + crew
    return task(
        f"Теплоход рассчитан на {passengers} пассажиров и {crew} членов команды. Каждая спасательная шлюпка может вместить {capacity} человек. "
        "Какое наименьшее число шлюпок должно быть на теплоходе, чтобы в случае необходимости в них можно было разместить всех пассажиров и всех членов команды?",
        dec(math.ceil(total / capacity)),
        f"Всего {total} человек. {total} : {capacity} {quotient(Fraction(total, capacity))}, шлюпок нужно {math.ceil(total / capacity)}.",
    )


def b1_promo(r):
    price = r.choice([25, 30, 35, 40, 45, 55])
    money = r.choice([200, 250, 300, 350, 400])
    paid = money // price
    total = paid + paid // 2
    return task(
        f"Шоколадка стоит {price} рублей. В воскресенье в супермаркете действует специальное предложение: заплатив за две шоколадки, покупатель получает три "
        f"(одну в подарок). Какое наибольшее количество шоколадок можно получить, потратив не более {money} рублей в воскресенье?",
        dec(total),
        f"На {money} рублей можно оплатить {paid} шоколадок, за каждые две оплаченные дают ещё одну: {paid} + {paid // 2} = {total}.",
    )


def b1_floor(r):
    item, many, rub, kop = r.choice([
        ("Сырок", "сырков", 7, 20), ("Шариковая ручка", "ручек", 12, 40), ("Почтовый конверт", "конвертов", 5, 60),
        ("Тетрадь", "тетрадей", 18, 50), ("Пакет сока", "пакетов сока", 46, 80), ("Билет на автобус", "билетов", 23, 50),
    ])
    money = r.choice([60, 80, 100, 150, 200, 300, 500])
    price = rub * 100 + kop
    return task(
        f"{item} стоит {rub} рублей {kop} копеек. Какое наибольшее число {many} можно купить на {money} рублей?",
        dec(money * 100 // price),
        f"{money} : {dec(Fraction(price, 100))} {quotient(Fraction(money * 100, price))}; целое число покупок равно {money * 100 // price}.",
    )


def b1_bags(r):
    per_litre = r.choice([8, 10, 12, 15])
    bag = r.choice([10, 20, 25])
    litres = r.randint(4, 14)
    total = per_litre * litres
    return task(
        f"Для приготовления маринада для огурцов на 1 литр воды требуется {per_litre} г лимонной кислоты. Лимонная кислота продаётся в пакетиках по {bag} г. "
        f"Какое наименьшее число пакетиков нужно купить хозяйке для приготовления {litres} литров маринада?",
        dec(math.ceil(total / bag)),
        f"Нужно {total} г кислоты, {total} : {bag} = {dec(Fraction(total, bag))}, пакетиков нужно {math.ceil(total / bag)}.",
    )


# ---------------------------------------------------------------- №2 Размеры и единицы измерения

UNIT_SETS = [
    ("массами", ["масса куриного яйца", "масса детской коляски", "масса взрослого бегемота", "масса активного вещества в таблетке"],
     ["50 г", "14 кг", "3 т", "2,5 мг"]),
    ("длинами", ["рост ребёнка", "толщина листа бумаги", "длина автобусного маршрута", "высота жилого дома"],
     ["110 см", "0,1 мм", "32 км", "30 м"]),
    ("площадями", ["площадь почтовой марки", "площадь письменного стола", "площадь города Санкт-Петербурга", "площадь волейбольной площадки"],
     ["6,8 кв. см", "1,2 кв. м", "1439 кв. км", "162 кв. м"]),
    ("объёмами", ["объём воды в Азовском море", "объём ящика с инструментами", "объём грузового отсека транспортного самолёта", "объём бутылки растительного масла"],
     ["256 куб. км", "76 л", "150 куб. м", "1 л"]),
    ("промежутками времени", ["время одного оборота Земли вокруг Солнца", "длительность полнометражного художественного фильма", "длительность звучания одной песни", "продолжительность вспышки фотоаппарата"],
     ["365 суток", "105 минут", "3,5 минуты", "0,1 секунды"]),
    ("скоростями", ["скорость движения автомобиля", "скорость движения пешехода", "скорость движения улитки", "скорость звука в воздушной среде"],
     ["120 км/ч", "4 км/ч", "0,5 м/мин", "330 м/с"]),
    ("массами", ["масса взрослого кита", "масса футбольного мяча", "масса дождевой капли", "масса стиральной машины"],
     ["130 т", "450 г", "20 мг", "18 кг"]),
    ("длинами", ["длина тела кошки", "высота потолка в комнате", "высота Исаакиевского собора в Санкт-Петербурге", "длина реки Обь"],
     ["54 см", "2,8 м", "102 м", "3650 км"]),
    ("массами", ["масса мобильного телефона", "масса одной ягоды клубники", "масса взрослого слона", "масса курицы"],
     ["100 г", "12,5 г", "5 т", "3 кг"]),
    ("объёмами", ["объём комнаты", "объём воды в Каспийском море", "объём ящика для овощей", "объём банки сметаны"],
     ["45 куб. м", "78 200 куб. км", "72 л", "500 мл"]),
    ("площадями", ["площадь одной страницы учебника", "площадь территории России", "площадь футбольного поля", "площадь трёхкомнатной квартиры"],
     ["330 кв. см", "17,1 млн кв. км", "7000 кв. м", "100 кв. м"]),
    ("промежутками времени", ["время одного оборота Земли вокруг своей оси", "время обращения Луны вокруг Земли", "длительность школьного урока", "время, за которое свет от Солнца доходит до Земли"],
     ["24 часа", "27 суток", "45 минут", "8 минут"]),
    ("длинами", ["диаметр монеты", "длина экватора Земли", "высота горы Эверест", "длина школьного коридора"],
     ["20 мм", "40 000 км", "8848 м", "40 м"]),
    ("массами", ["масса новорождённого ребёнка", "масса школьного ластика", "масса легкового автомобиля", "масса железнодорожного состава"],
     ["3500 г", "15 г", "1,2 т", "4000 т"]),
    ("объёмами", ["объём чайной ложки", "объём ведра", "объём плавательного бассейна", "объём железнодорожной цистерны"],
     ["5 мл", "10 л", "900 куб. м", "70 куб. м"]),
    ("скоростями", ["скорость роста бамбука", "скорость пассажирского самолёта", "скорость велосипедиста", "скорость света в вакууме"],
     ["50 см/сутки", "900 км/ч", "18 км/ч", "300 000 км/с"]),
    ("площадями", ["площадь экрана смартфона", "площадь озера Байкал", "площадь баскетбольной площадки", "площадь дачного участка"],
     ["90 кв. см", "31 500 кв. км", "420 кв. м", "6 соток"]),
    ("промежутками времени", ["продолжительность футбольного тайма", "время обращения Земли вокруг Солнца", "длительность одного удара сердца", "продолжительность суточного сна взрослого человека"],
     ["45 минут", "12 месяцев", "0,8 секунды", "8 часов"]),
    ("длинами", ["толщина человеческого волоса", "расстояние от Москвы до Владивостока", "длина легкового автомобиля", "высота Останкинской телебашни"],
     ["0,08 мм", "6400 км", "4,5 м", "540 м"]),
    ("массами", ["масса буханки хлеба", "масса почтового письма", "масса гружёного самосвала", "масса мешка цемента"],
     ["600 г", "20 г", "25 т", "50 кг"]),
]


def b2_units(r):
    name, objects, values = r.choice(UNIT_SETS)
    order = list(range(4))
    r.shuffle(order)
    left = [objects[i] for i in order]
    shown = list(range(4))
    r.shuffle(shown)
    right = [values[i] for i in shown]
    answer = "".join(str(shown.index(i) + 1) for i in order)
    made = matching(
        "Установите соответствие между величинами и их возможными значениями: к каждому элементу первого столбца подберите соответствующий элемент из второго столбца.",
        left, right, answer,
        "; ".join(f"{objects[i]}: {values[i]}" for i in order) + ".",
    )
    made["key"] = objects[0]
    return made


# ---------------------------------------------------------------- №3 Чтение графиков и диаграмм

MONTHS = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


def b3_bar_chart(r):
    place = r.choice(["Симферополе", "Нижнем Новгороде", "Екатеринбурге", "Минске", "Сочи", "Томске"])
    winter, summer = r.randrange(-16, -1, 2), r.randrange(16, 27, 2)
    temps = []
    for month in range(12):
        share = (1 - math.cos(2 * math.pi * (month - 0.5) / 12)) / 2
        value = int(round((winter + (summer - winter) * share) / 2)) * 2 + r.choice([-2, 0, 0, 2])
        temps.append(value if value != 0 else 2)
    fig = Fig()
    left, zero, width = 40, 140, 31

    def y_of(value):
        return zero - value * 4.4

    for value in range(-20, 29, 4):
        fig.line(left, y_of(value), left + 12 * width, y_of(value), 0)
        fig.text(left - 6, y_of(value), value, "r")
    for month in range(12):
        top = min(y_of(temps[month]), zero)
        fig.rect(left + month * width + 6, top, 19, abs(y_of(temps[month]) - zero), 2)
        fig.text(left + month * width + width / 2, 246, month + 1)
    fig.line(left, zero, left + 12 * width, zero, 1)
    kind = r.choice(["positive", "difference", "above", "max"])
    if kind == "positive":
        question, answer = ", сколько было месяцев с положительной среднемесячной температурой", sum(1 for t in temps if t > 0)
    elif kind == "difference":
        question, answer = " разность между наибольшей и наименьшей среднемесячными температурами. Ответ дайте в градусах Цельсия", max(temps) - min(temps)
    elif kind == "above":
        level = r.choice([8, 12, 16])
        question, answer = f", сколько было месяцев, когда среднемесячная температура превышала {level} градусов Цельсия", sum(1 for t in temps if t > level)
    else:
        question, answer = " наибольшую среднемесячную температуру. Ответ дайте в градусах Цельсия", max(temps)
    return task(
        f"На диаграмме показана среднемесячная температура воздуха в {place} за каждый месяц года. По горизонтали указываются номера месяцев, "
        f"по вертикали температура в градусах Цельсия. Определите по диаграмме{question}.",
        dec(answer),
        f"По диаграмме получаем {answer}.",
        fig,
    )


def b3_line_chart(r):
    return figures.fig_line_chart(r)


def b3_price_graph(r):
    days = 12
    prices = [r.randrange(20, 61, 4)]
    for _ in range(days - 1):
        prices.append(min(64, max(16, prices[-1] + r.choice([-8, -4, -4, 4, 4, 8]))))
    fig = Fig()
    px = figures.axes(fig, 46, 228, 29, 13, days, 16, "день", "руб.", 1, 2, 1, 4)
    for day in range(1, days):
        fig.line(*px(day, prices[day - 1] / 4), *px(day + 1, prices[day] / 4), 2)
    for day in range(1, days + 1):
        fig.circle(*px(day, prices[day - 1] / 4), 3.5, 2)
    kind = r.choice(["max", "min", "difference", "day_max"])
    best_day = prices.index(max(prices)) + 1
    if kind == "day_max" and prices.count(max(prices)) != 1:
        kind = "max"
    if kind == "max":
        question, answer = " наибольшую цену акции за указанный период. Ответ дайте в рублях", max(prices)
    elif kind == "min":
        question, answer = " наименьшую цену акции за указанный период. Ответ дайте в рублях", min(prices)
    elif kind == "difference":
        question, answer = " разность между наибольшей и наименьшей ценой акции за указанный период. Ответ дайте в рублях", max(prices) - min(prices)
    else:
        question, answer = ", какого числа цена акции была наибольшей", best_day
    return task(
        "На рисунке жирными точками показана цена акции компании на момент закрытия биржевых торгов во все рабочие дни с 1 по 12 число месяца. "
        f"По горизонтали указываются числа месяца, по вертикали цена акции в рублях. Определите по рисунку{question}.",
        dec(answer),
        f"По рисунку получаем {answer}.",
        fig,
    )


# ---------------------------------------------------------------- №4 Преобразования выражений


def b4_formula(r):
    kind = r.choice(["force", "energy", "fahrenheit", "area", "work", "power", "triangle", "accel"])
    if kind == "force":
        m, a = r.randint(3, 20), r.randint(2, 15)
        return task(
            f"Второй закон Ньютона можно записать в виде F = ma, где F это сила (в ньютонах), действующая на тело, m это его масса (в килограммах), a это ускорение "
            f"(в м/с²). Пользуясь этой формулой, найдите m (в килограммах), если F = {m * a} Н и a = {a} м/с².",
            dec(m), f"m = F : a = {m * a} : {a} = {m}.")
    if kind == "energy":
        m, v = r.choice([2, 4, 6, 8, 10, 12]), r.randint(2, 12)
        return task(
            f"Кинетическая энергия тела (в джоулях) вычисляется по формуле E = mv² : 2, где m это масса тела (в килограммах), а v это его скорость (в м/с). "
            f"Пользуясь этой формулой, найдите E (в джоулях), если v = {v} м/с и m = {m} кг.",
            dec(m * v * v // 2), f"E = {m} · {v}² : 2 = {m * v * v // 2}.")
    if kind == "fahrenheit":
        celsius = r.randrange(-40, 41, 5)
        value = Fraction(9 * celsius, 5) + 32
        return task(
            "Чтобы перевести температуру из шкалы Цельсия в шкалу Фаренгейта, пользуются формулой tF = 1,8tC + 32, где tC это температура в градусах по шкале Цельсия, "
            f"tF это температура в градусах по шкале Фаренгейта. Скольким градусам по шкале Фаренгейта соответствует {celsius} градусов по шкале Цельсия?",
            dec(value), f"tF = 1,8 · ({celsius}) + 32 = {dec(value)}.")
    if kind == "area":
        d1, d2 = r.randint(3, 16), r.randint(3, 16)
        sine = Fraction(r.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]), 10)
        value = Fraction(d1 * d2, 2) * sine
        return task(
            "Площадь четырёхугольника можно вычислить по формуле S = d₁ · d₂ · sin α : 2, где d₁ и d₂ это длины диагоналей четырёхугольника, α это угол между диагоналями. "
            f"Пользуясь этой формулой, найдите площадь S, если d₁ = {d1}, d₂ = {d2}, а sin α = {dec(sine)}.",
            dec(value), f"S = {d1} · {d2} · {dec(sine)} : 2 = {dec(value)}.")
    if kind == "work":
        current, resistance, time = r.randint(2, 8), r.randint(2, 12), r.randint(2, 10)
        return task(
            "Работа постоянного тока (в джоулях) вычисляется по формуле A = I²Rt, где I это сила тока (в амперах), R это сопротивление (в омах), t это время (в секундах). "
            f"Пользуясь этой формулой, найдите A (в джоулях), если t = {time} с, I = {current} А и R = {resistance} Ом.",
            dec(current * current * resistance * time), f"A = {current}² · {resistance} · {time} = {current * current * resistance * time}.")
    if kind == "power":
        current, resistance = r.randint(2, 9), r.randint(2, 15)
        return task(
            "Мощность постоянного тока (в ваттах) вычисляется по формуле P = I²R, где I это сила тока (в амперах), R это сопротивление (в омах). "
            f"Пользуясь этой формулой, найдите R (в омах), если мощность составляет {current * current * resistance} Вт, а сила тока равна {current} А.",
            dec(resistance), f"R = P : I² = {current * current * resistance} : {current * current} = {resistance}.")
    if kind == "triangle":
        a, h = r.randint(3, 20), r.randint(2, 18)
        if a * h % 2:
            h += 1
        return task(
            f"Площадь треугольника вычисляется по формуле S = a · h : 2, где a это сторона треугольника, h это высота, проведённая к этой стороне. "
            f"Пользуясь этой формулой, найдите сторону a, если площадь треугольника равна {a * h // 2}, а высота h равна {h}.",
            dec(a), f"a = 2S : h = {a * h} : {h} = {a}.")
    omega, radius = r.randint(2, 9), r.randint(2, 12)
    return task(
        "Центростремительное ускорение при движении по окружности (в м/с²) вычисляется по формуле a = ω²R, где ω это угловая скорость (в с⁻¹), R это радиус окружности (в метрах). "
        f"Пользуясь этой формулой, найдите радиус R, если угловая скорость равна {omega} с⁻¹, а центростремительное ускорение равно {omega * omega * radius} м/с². Ответ дайте в метрах.",
        dec(radius), f"R = a : ω² = {omega * omega * radius} : {omega * omega} = {radius}.")


# ---------------------------------------------------------------- №5 Начала теории вероятностей


def b5_taxi(r):
    total = r.choice([10, 20, 25, 40, 50])
    colours = ["чёрные с жёлтыми надписями на боках", "жёлтые с чёрными надписями"]
    first = r.randint(2, total - 3)
    return task(
        f"В фирме такси в наличии {total} легковых автомобилей; {first} из них {colours[0]}, остальные {colours[1]}. "
        "Найдите вероятность того, что на случайный вызов приедет машина жёлтого цвета с чёрными надписями.",
        dec(Fraction(total - first, total)),
        f"Жёлтых машин {total - first}, вероятность равна {total - first} : {total} = {dec(Fraction(total - first, total))}.",
    )


def b5_pen(r):
    item = r.choice([
        "новая шариковая ручка пишет плохо (или не пишет)", "новая лампочка окажется бракованной", "новая батарейка окажется разряженной",
        "новый фонарик окажется неисправным", "новый чайник прослужит меньше года", "новый принтер потребует ремонта в течение года",
    ])
    probability = Fraction(r.randint(2, 30), 100)
    return task(
        f"Вероятность того, что {item}, равна {dec(probability)}. Покупатель в магазине выбирает один такой товар. "
        "Найдите вероятность того, что этого не произойдёт.",
        dec(1 - probability),
        f"1 - {dec(probability)} = {dec(1 - probability)}.",
    )


def b5_topics(r):
    first, second = Fraction(r.randint(10, 35), 100), Fraction(r.randint(10, 35), 100)
    names = r.sample(["Вписанная окружность", "Параллелограмм", "Тригонометрия", "Внешние углы", "Площадь", "Углы"], 2)
    return task(
        f"На экзамене по геометрии школьник отвечает на один вопрос из списка экзаменационных вопросов. Вероятность того, что это вопрос по теме «{names[0]}», "
        f"равна {dec(first)}. Вероятность того, что это вопрос по теме «{names[1]}», равна {dec(second)}. Вопросов, которые одновременно относятся к этим двум темам, нет. "
        "Найдите вероятность того, что на экзамене школьнику достанется вопрос по одной из этих двух тем.",
        dec(first + second),
        f"События несовместны: {dec(first)} + {dec(second)} = {dec(first + second)}.",
    )


# ---------------------------------------------------------------- №6 Выбор оптимального варианта


def b6_carriers(r):
    tons = r.randrange(30, 91, 5)
    distance = r.randrange(600, 2001, 100)
    rows = [["Перевозчик", "Цена, руб. за 100 км", "Грузоподъёмность, т"]]
    costs = []
    for name in "АБВ":
        capacity = r.choice([3.5, 5, 10, 12])
        price = r.randrange(2800, 9601, 200)
        vehicles = math.ceil(tons / capacity)
        costs.append(vehicles * price * distance // 100)
        rows.append([name, str(price), dec(Fraction(capacity).limit_denominator(2))])
    fig = table_figure(rows, cell_width=150, first_width=110)
    return task(
        f"Для транспортировки {tons} тонн груза на {distance} км можно воспользоваться услугами одной из трёх фирм-перевозчиков. В таблице показаны стоимость перевозки "
        "одним автомобилем на 100 км и грузоподъёмность автомобилей каждого перевозчика. Сколько рублей придётся заплатить за самую дешёвую перевозку?",
        dec(min(costs)),
        "Стоимость у перевозчиков: " + ", ".join(f"{name}: {cost} руб" for name, cost in zip("АБВ", costs)) + f". Самая дешёвая перевозка стоит {min(costs)} руб.",
        fig,
    )


def b6_internet(r):
    traffic = r.randrange(500, 1501, 50)
    plans = [
        (0, 0, Fraction(r.choice([4, 5, 6]), 2)),
        (r.choice([500, 550, 600]), r.choice([400, 500]), Fraction(r.choice([3, 4]), 2)),
        (r.choice([900, 1000, 1200]), r.choice([1000, 1200]), Fraction(r.choice([2, 3]), 2)),
    ]
    rows = [["Тариф", "Абонентская плата", "Плата за трафик"]]
    costs = []
    for index, (fee, included, per_mb) in enumerate(plans, start=1):
        costs.append(fee + max(0, traffic - included) * per_mb)
        if fee == 0:
            rows.append([f"План {index}", "нет", f"{dec(per_mb)} руб. за 1 Мб"])
        else:
            rows.append([f"План {index}", f"{fee} руб. за {included} Мб", f"{dec(per_mb)} руб. за 1 Мб сверх"])
    return task(
        f"Интернет-провайдер предлагает три тарифных плана. Пользователь предполагает, что его трафик составит {traffic} Мб в месяц, и исходя из этого выбирает "
        f"наиболее дешёвый тарифный план. Сколько рублей заплатит пользователь за месяц, если его трафик действительно будет равен {traffic} Мб?",
        dec(min(costs)),
        "Стоимость по планам: " + ", ".join(dec(cost) for cost in costs) + f" руб. Наименьшая равна {dec(min(costs))} руб.",
        table_figure(rows, cell_width=165, first_width=80),
    )


def b6_route(r):
    names = ["Автобус", "Электричка", "Маршрутное такси"]
    while True:
        parts = [[r.randrange(5, 41, 5), r.randrange(75, 151, 5), r.randrange(5, 41, 5)] for _ in names]
        totals = [sum(row) for row in parts]
        # Ответ в часах должен быть конечной десятичной дробью, а лучший способ единственным.
        if min(totals) % 15 == 0 and totals.count(min(totals)) == 1:
            break
    rows = [["Вид транспорта", "До станции", "В пути", "От станции"]]
    for name, row in zip(names, parts):
        rows.append([name] + [f"{minutes} мин" for minutes in row])
    best = min(totals)
    return task(
        "Из пункта А в пункт Б можно добраться тремя способами. В таблице показано время, которое нужно затратить на каждый участок пути. "
        "Какое наименьшее время потребуется на дорогу? Ответ дайте в часах.",
        dec(Fraction(best, 60)),
        "Время в пути: " + ", ".join(f"{name}: {total} мин" for name, total in zip(names, totals)) + f". Наименьшее время {best} мин, это {dec(Fraction(best, 60))} ч.",
        table_figure(rows, cell_width=100, first_width=150),
    )


# ---------------------------------------------------------------- №7 Анализ графиков и диаграмм


def b7_function_points(r):
    # В каждой из четырёх точек своё сочетание знаков функции и производной.
    period = r.uniform(6.5, 8.5)
    shift = r.uniform(-9.0, -8.0)
    amplitude = r.uniform(3, 4.5)

    def f(x):
        return amplitude * math.sin(2 * math.pi * (x - shift) / period)

    # Сочетания: (f > 0, f' > 0) в первой четверти периода, далее по порядку.
    combos = [(True, True), (True, False), (False, False), (False, True)]
    quarter_points = []
    for quarter, combo in enumerate(combos):
        cycle = r.choice([0, 1])
        x = shift + period * (cycle + (quarter + 0.5) / 4)
        if not -9.5 <= x <= 9.5:
            x = shift + period * ((1 - cycle) + (quarter + 0.5) / 4)
        if not -9.5 <= x <= 9.5:
            return b7_function_points(r)
        quarter_points.append((x, combo))
    quarter_points.sort()
    plane = Plane(labels=False)
    plane.curve(f, -10, 10, 110, 1)
    letters = "ABCD"
    for letter, (x, _) in zip(letters, quarter_points):
        plane.fig.line(*plane.px(x, 0), *plane.px(x, f(x)), 0)
        plane.fig.circle(*plane.px(x, 0), 3.5, 2)
        plane.fig.text(plane.px(x, 0)[0], plane.px(x, 0)[1] + (12 if f(x) > 0 else -12), letter)
    descriptions = {
        (True, True): "значение функции в точке положительно, и значение производной функции в точке положительно",
        (True, False): "значение функции в точке положительно, а значение производной функции в точке отрицательно",
        (False, False): "значение функции в точке отрицательно, и значение производной функции в точке отрицательно",
        (False, True): "значение функции в точке отрицательно, а значение производной функции в точке положительно",
    }
    order = combos[:]
    r.shuffle(order)
    answer = "".join(str(order.index(combo) + 1) for _, combo in quarter_points)
    made = matching(
        "На рисунке изображён график функции y = f(x), на оси абсцисс отмечены точки A, B, C и D. Пользуясь графиком, поставьте в соответствие каждой точке "
        "характеристику функции и её производной. Буквам А, Б, В, Г отвечают точки A, B, C, D.",
        [f"точка {letter}" for letter in letters],
        [descriptions[combo] for combo in order],
        answer,
        "Знак функции виден по положению графика относительно оси, знак производной по тому, возрастает функция или убывает.",
    )
    made["figure"] = plane.fig.data()
    return made


def b7_speed_intervals(r):
    # График температуры по часам: периоды сопоставляются с характером изменения.
    hours = [0, 3, 6, 9, 12]
    while True:
        changes = [r.choice([-6, -3, 3, 6]) for _ in range(4)]
        if len(set(changes)) == 4:
            break
    values = [12]
    for change in changes:
        values.append(values[-1] + change)
    low = min(values)
    values = [v - low + 2 for v in values]
    fig = Fig()
    px = figures.axes(fig, 46, 228, 28, 10, 12, 20, "ч", "°C", 3, 2)
    for index in range(4):
        fig.line(*px(hours[index], values[index]), *px(hours[index + 1], values[index + 1]), 2)
    for hour, value in zip(hours, values):
        fig.circle(*px(hour, value), 3.5, 2)
    descriptions = {-6: "температура падала быстрее всего", -3: "температура падала медленнее всего", 3: "температура росла медленнее всего", 6: "температура росла быстрее всего"}
    left = [f"{hours[i]}:00-{hours[i + 1]}:00" for i in range(4)]
    order = [-6, -3, 3, 6]
    r.shuffle(order)
    answer = "".join(str(order.index(change) + 1) for change in changes)
    made = matching(
        "На графике показано изменение температуры воздуха в течение 12 часов. По горизонтали указано время в часах, по вертикали температура в градусах Цельсия. "
        "Пользуясь графиком, поставьте в соответствие каждому интервалу времени характеристику изменения температуры на этом интервале.",
        left, [descriptions[change] for change in order], answer,
        "Скорость изменения температуры видна по наклону отрезка графика: чем круче, тем быстрее.",
    )
    made["figure"] = fig.data()
    return made


# ---------------------------------------------------------------- №8 Анализ утверждений


def b8_clubs(r):
    total = r.randint(18, 30)
    first = r.randint(total // 2 + 1, total - 3)
    second = r.randint(total - first + 2, total - 4)
    low, high = first + second - total, min(first, second)
    a_name, b_name = r.choice([("по истории", "по математике"), ("по физике", "по химии"), ("по шахматам", "по рисованию")])
    k_true = r.randint(2, low)
    k_false = high + 1
    statements = [
        ("Каждый ученик этого класса посещает оба кружка.", False),
        (f"Найдутся хотя бы {k_true} учеников из этого класса, которые посещают оба кружка.", True),
        (f"Если ученик из этого класса ходит на кружок {a_name}, то он обязательно ходит на кружок {b_name}.", False),
        (f"Не найдётся {k_false} учеников из этого класса, которые посещают оба кружка.", True),
        (f"В этом классе меньше {low} учеников посещают оба кружка.", False),
        (f"Не больше {high} учеников этого класса посещают оба кружка.", True),
    ]
    picked = r.sample(statements, 4)
    if not any(flag for _, flag in picked) or all(flag for _, flag in picked):
        return b8_clubs(r)
    return choose(
        f"В классе учится {total} человек, из них {first} человек посещают кружок {a_name}, а {second} человек посещают кружок {b_name}. "
        "Выберите утверждения, которые верны при указанных условиях.",
        [text for text, _ in picked], [flag for _, flag in picked],
        f"Оба кружка посещают не меньше {first} + {second} - {total} = {low} и не больше {high} учеников.",
    )


def b8_order(r):
    names = r.sample(["Маша", "Оля", "Лена", "Вера", "Катя", "Аня", "Зина", "Юля"], 4)
    # names[0] самая высокая, names[3] самая низкая.
    a, b, c, d = names
    intro = f"Среди четырёх подруг {a} выше, чем {b}; {b} выше, чем {c}; {d} ниже всех остальных."
    statements = [
        (f"{a} самая высокая из подруг.", True),
        (f"{c} выше, чем {a}.", False),
        (f"{b} ниже, чем {a}, но выше, чем {d}.", True),
        (f"{d} и {c} одного роста.", False),
        (f"Среди подруг есть хотя бы две, которые выше, чем {c}.", True),
        (f"{b} самая низкая из подруг.", False),
        (f"{c} ниже, чем {a}.", True),
    ]
    picked = r.sample(statements, 4)
    if not any(flag for _, flag in picked) or all(flag for _, flag in picked):
        return b8_order(r)
    return choose(intro + " Выберите утверждения, которые верны при указанных условиях.",
                  [text for text, _ in picked], [flag for _, flag in picked],
                  f"По росту подруги идут так: {a}, {b}, {c}, {d}.")


def b8_implication(r):
    place_a, place_b = r.choice([("на даче", "на море"), ("в горах", "в деревне"), ("в лагере", "у бабушки")])
    statements = [
        (f"Каждый сотрудник этой фирмы отдыхал летом либо {place_a}, либо {place_b}, либо и там, и там.", True),
        (f"Сотрудник этой фирмы, который не отдыхал {place_b}, не отдыхал и {place_a}.", False),
        (f"Если Фаина не отдыхала ни {place_a}, ни {place_b}, то она является сотрудником этой фирмы.", False),
        (f"Если сотрудник этой фирмы не отдыхал {place_a}, то он отдыхал {place_b}.", True),
        (f"Все сотрудники этой фирмы отдыхали {place_b}.", False),
        (f"Если Борис не отдыхал ни {place_a}, ни {place_b}, то он не является сотрудником этой фирмы.", True),
    ]
    picked = r.sample(statements, 4)
    if not any(flag for _, flag in picked) or all(flag for _, flag in picked):
        return b8_implication(r)
    return choose(
        f"Некоторые сотрудники фирмы летом отдыхали {place_a}, а некоторые {place_b}. Все сотрудники, которые не отдыхали {place_b}, отдыхали {place_a}. "
        "Выберите утверждения, которые верны при указанных условиях.",
        [text for text, _ in picked], [flag for _, flag in picked],
        "Из условия следует: каждый сотрудник отдыхал хотя бы в одном из двух мест.",
    )


# ---------------------------------------------------------------- №9 Задачи на квадратной решётке


def shoelace(points):
    total = 0
    for index in range(len(points)):
        x1, y1 = points[index]
        x2, y2 = points[(index + 1) % len(points)]
        total += x1 * y2 - x2 * y1
    return Fraction(abs(total), 2)


def grid_figure(points):
    fig = Fig()
    left, bottom, cell = 30, 235, 30

    def px(x, y):
        return left + x * cell, bottom - y * cell

    for n in range(0, 13):
        fig.line(*px(n, 0), *px(n, 7), 0)
    for n in range(0, 8):
        fig.line(*px(0, n), *px(12, n), 0)
    for index in range(len(points)):
        fig.line(*px(*points[index]), *px(*points[(index + 1) % len(points)]), 2)
    return fig


def b9_triangle(r):
    return figures.fig_grid_triangle(r)


def b9_trapezoid(r):
    return figures.fig_grid_trapezoid(r)


def b9_rhombus(r):
    half_w, half_h = r.randint(1, 5), r.randint(1, 3)
    cx, cy = r.randint(half_w, 12 - half_w), r.randint(half_h, 7 - half_h)
    points = [(cx - half_w, cy), (cx, cy + half_h), (cx + half_w, cy), (cx, cy - half_h)]
    return task(
        "На клетчатой бумаге с размером клетки 1 × 1 изображён ромб. Найдите его площадь.",
        dec(2 * half_w * half_h),
        f"Диагонали ромба равны {2 * half_w} и {2 * half_h}, площадь равна половине их произведения: {2 * half_w * half_h}.",
        grid_figure(points),
    )


def b9_plan(r):
    while True:
        width, height = r.randint(4, 11), r.randint(3, 6)
        cut_w, cut_h = r.randint(1, width - 2), r.randint(1, height - 1)
        if width * height - cut_w * cut_h > 6:
            break
    x0, y0 = r.randint(0, 12 - width), r.randint(0, 7 - height)
    points = [(x0, y0), (x0 + width, y0), (x0 + width, y0 + height - cut_h), (x0 + width - cut_w, y0 + height - cut_h),
              (x0 + width - cut_w, y0 + height), (x0, y0 + height)]
    side = r.choice([2, 5, 10])
    area = (width * height - cut_w * cut_h) * side * side
    return task(
        f"На плане изображён земельный участок. Сторона одной клетки на плане соответствует {side} м. Найдите площадь участка. Ответ дайте в квадратных метрах.",
        dec(area),
        f"Участок занимает {width * height - cut_w * cut_h} клеток, площадь одной клетки {side * side} кв. м: всего {area} кв. м.",
        grid_figure(points),
    )


# ---------------------------------------------------------------- №10 Прикладная геометрия


def b10_fence(r):
    a, b = sorted(r.sample(range(15, 61, 5), 2))
    return task(
        f"Дачный участок имеет форму прямоугольника со сторонами {a} метров и {b} метров. Хозяин планирует обнести его забором и разделить таким же забором на две части, "
        "одна из которых имеет форму квадрата. Найдите общую длину забора в метрах.",
        dec(2 * (a + b) + a),
        f"Периметр равен {2 * (a + b)} м, перегородка равна меньшей стороне: {2 * (a + b)} + {a} = {2 * (a + b) + a} м.",
    )


def b10_wheel(r):
    spokes = r.choice([5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45])
    return task(
        f"Колесо имеет {spokes} спиц. Углы между соседними спицами равны. Найдите угол, который образуют две соседние спицы. Ответ дайте в градусах.",
        dec(Fraction(360, spokes)),
        f"360° : {spokes} = {dec(Fraction(360, spokes))}°.",
    )


def b10_stairs(r):
    step_h, step_l, step_d = r.choice([(14, 48, 50), (12, 35, 37), (15, 36, 39), (9, 40, 41), (20, 21, 29), (16, 30, 34)])
    steps = r.choice([10, 20, 25, 30, 40, 50])
    return task(
        f"Лестница соединяет точки A и B и состоит из одинаковых ступеней. Высота каждой ступени равна {step_h} см, а длина {step_l} см. "
        f"Расстояние между точками A и B составляет {dec(Fraction(step_d * steps, 100))} м. Найдите высоту, на которую поднимается лестница (в метрах).",
        dec(Fraction(step_h * steps, 100)),
        f"Отрезок, соответствующий одной ступени, равен √({step_h}² + {step_l}²) = {step_d} см. Ступеней {steps}, высота равна {steps} · {step_h} см = {dec(Fraction(step_h * steps, 100))} м.",
    )


def b10_clock(r):
    hour = r.choice([1, 2, 3, 4, 5, 7, 8, 9, 10, 11])
    angle = min(hour, 12 - hour) * 30
    return task(
        f"Какой наименьший угол (в градусах) образуют минутная и часовая стрелки часов в {hour}:00?",
        dec(angle),
        f"Между соседними часовыми делениями 30°. Число таких промежутков между стрелками равно {min(hour, 12 - hour)}, угол равен {angle}°.",
    )


def b10_parquet(r):
    width, length = r.randint(3, 6), r.randint(4, 9)
    plank_w, plank_l = r.choice([(10, 25), (5, 20), (10, 40), (5, 30), (20, 40), (10, 50)])
    area = width * length * 10000
    if area % (plank_w * plank_l):
        return b10_parquet(r)
    return task(
        f"Пол комнаты, имеющей форму прямоугольника со сторонами {width} м и {length} м, требуется покрыть паркетом из прямоугольных дощечек "
        f"со сторонами {plank_w} см и {plank_l} см. Сколько потребуется таких дощечек?",
        dec(area // (plank_w * plank_l)),
        f"Площадь пола {area} кв. см, площадь дощечки {plank_w * plank_l} кв. см: {area} : {plank_w * plank_l} = {area // (plank_w * plank_l)}.",
    )


def b10_shadow(r):
    while True:
        height = Fraction(r.choice([15, 16, 17, 18, 19]), 10)
        lamp = r.choice([4, 5, 6, 8, 9])
        distance = r.randint(4, 20)
        shadow = height * distance / (lamp - height)
        if shadow.denominator == 1:
            break
    return task(
        f"Человек ростом {dec(height)} м стоит на расстоянии {distance} м от столба, на котором висит фонарь на высоте {lamp} м. Найдите длину тени человека в метрах.",
        dec(shadow),
        f"Из подобия треугольников: x : (x + {distance}) = {dec(height)} : {lamp}, откуда x = {dec(shadow)} м.",
    )


# ---------------------------------------------------------------- №11 Прикладная стереометрия


def b11_aquarium(r):
    a, b, c = r.choice([50, 60, 80, 90, 100]), r.choice([30, 40, 50]), r.choice([30, 40, 50, 60])
    return task(
        f"Аквариум имеет форму прямоугольного параллелепипеда с размерами {a} см × {b} см × {c} см. Сколько литров составляет объём аквариума? "
        "В одном литре 1000 кубических сантиметров.",
        dec(Fraction(a * b * c, 1000)),
        f"{a} · {b} · {c} = {a * b * c} куб. см = {dec(Fraction(a * b * c, 1000))} л.",
    )


def b11_detail(r):
    litres = r.randint(3, 12)
    factor = Fraction(r.choice([11, 12, 13, 14, 15, 16, 18]), 10)
    return task(
        f"В бак, имеющий форму прямой призмы, налито {litres} л воды. После полного погружения в воду детали уровень воды в баке увеличился в {dec(factor)} раза. "
        "Найдите объём детали. Ответ дайте в кубических сантиметрах, зная, что в одном литре 1000 кубических сантиметров.",
        dec(litres * (factor - 1) * 1000),
        f"Объём воды с деталью равен {dec(litres * factor)} л, объём детали {dec(litres * (factor - 1))} л = {dec(litres * (factor - 1) * 1000)} куб. см.",
    )


def b11_faces(r):
    kind = r.choice(["cube_corners", "prism_pyramid", "cube_edges", "two_pyramids"])
    if kind == "cube_corners":
        return task(
            "От деревянного кубика отпилили все его вершины так, что плоскости распилов не пересекаются. Сколько граней у получившегося многогранника "
            "(невидимые рёбра и грани тоже учитываются)?",
            "14", "У куба 6 граней и 8 вершин, каждый распил добавляет одну грань: 6 + 8 = 14.")
    if kind == "cube_edges":
        return task(
            "От деревянного кубика отпилили все его вершины так, что плоскости распилов не пересекаются. Сколько вершин у получившегося многогранника?",
            "24", "Вместо каждой из 8 вершин куба появляется треугольная грань с тремя вершинами: 8 · 3 = 24.")
    if kind == "prism_pyramid":
        return task(
            "К правильной треугольной призме со стороной основания 1 приклеили правильную треугольную пирамиду с ребром 1 так, что основания совпали. "
            "Сколько граней у получившегося многогранника (невидимые рёбра и грани тоже учитываются)?",
            "7", "У призмы остаются одно основание и 3 боковые грани, у пирамиды 3 боковые грани: 1 + 3 + 3 = 7.")
    return task(
        "Две одинаковые правильные четырёхугольные пирамиды склеили основаниями. Сколько рёбер у получившегося многогранника?",
        "12", "У каждой пирамиды 4 боковых ребра, ещё 4 общих ребра основания: 4 + 4 + 4 = 12.")


def b11_mugs(r):
    taller = r.choice([2, 3, Fraction(3, 2)])
    wider = r.choice([2, 3, Fraction(3, 2)])
    words = {2: "вдвое", 3: "втрое", Fraction(3, 2): "в полтора раза"}
    value = Fraction(wider) ** 2 / taller
    if not is_finite_decimal(value) or value <= 1:
        return b11_mugs(r)
    return task(
        f"Даны две кружки цилиндрической формы. Первая кружка {words[taller]} выше второй, а вторая {words[wider]} шире первой. "
        "Во сколько раз объём второй кружки больше объёма первой?",
        dec(value),
        f"Объём пропорционален высоте и квадрату ширины: {dec(wider)}² : {dec(taller)} = {dec(value)}.",
    )


def b11_pour(r):
    factor = r.choice([2, 3, 4, 5])
    level = factor * factor * r.randint(1, 8)
    words = {2: "вдвое", 3: "втрое", 4: "в 4 раза", 5: "в 5 раз"}
    return task(
        f"Вода в сосуде цилиндрической формы находится на уровне h = {level} см. На каком уровне окажется вода, если её перелить в другой цилиндрический сосуд, "
        f"у которого радиус основания {words[factor]} больше, чем у первого? Ответ дайте в сантиметрах.",
        dec(level // (factor * factor)),
        f"Площадь основания больше в {factor * factor} раз, уровень ниже во столько же раз: {level // (factor * factor)} см.",
    )


# ---------------------------------------------------------------- №14 Вычисления


def b14_decimals(r):
    kind = r.choice(["divide", "bracket", "mixed"])
    if kind == "divide":
        b = Fraction(r.choice([2, 3, 4, 5, 6, 8, 12, 15]), 10)
        quotient = r.randint(2, 15)
        c = Fraction(r.randint(5, 60), 10)
        return task(
            f"Найдите значение выражения {dec(b * quotient)} : {dec(b)} - {dec(c)}.",
            dec(quotient - c),
            f"{dec(b * quotient)} : {dec(b)} = {quotient}; {quotient} - {dec(c)} = {dec(quotient - c)}.",
        )
    if kind == "bracket":
        a, b = Fraction(r.randint(30, 95), 10), Fraction(r.randint(5, 29), 10)
        c = Fraction(r.randint(12, 45), 10)
        return task(
            f"Найдите значение выражения ({dec(a)} - {dec(b)}) · {dec(c)}.",
            dec((a - b) * c),
            f"{dec(a)} - {dec(b)} = {dec(a - b)}; {dec(a - b)} · {dec(c)} = {dec((a - b) * c)}.",
        )
    a, b = Fraction(r.randint(11, 39), 10), Fraction(r.randint(11, 39), 10)
    c = Fraction(r.randint(2, 9), 10)
    return task(
        f"Найдите значение выражения {dec(a)} · {dec(b)} + {dec(c)}.",
        dec(a * b + c),
        f"{dec(a)} · {dec(b)} = {dec(a * b)}; {dec(a * b)} + {dec(c)} = {dec(a * b + c)}.",
    )


def b14_fractions(r):
    while True:
        d1, d2 = r.sample([2, 3, 4, 5, 6, 8, 10, 12, 15], 2)
        n1, n2 = r.randint(1, d1 - 1), r.randint(1, d2 - 1)
        multiplier = r.choice([6, 12, 15, 20, 24, 30, 36, 40, 48, 60])
        sign = r.choice([1, -1])
        value = (Fraction(n1, d1) + sign * Fraction(n2, d2)) * multiplier
        if math.gcd(n1, d1) == 1 and math.gcd(n2, d2) == 1 and is_finite_decimal(value) and value != 0:
            break
    return task(
        f"Найдите значение выражения ({n1}/{d1} {'+' if sign > 0 else '-'} {n2}/{d2}) · {multiplier}.",
        dec(value),
        f"{n1}/{d1} · {multiplier} = {frac(Fraction(n1 * multiplier, d1))}, {n2}/{d2} · {multiplier} = {frac(Fraction(n2 * multiplier, d2))}; ответ {dec(value)}.",
    )


# ---------------------------------------------------------------- №15 Простейшие текстовые задачи: проценты


def b15_tax(r):
    salary = r.randrange(12000, 60001, 1000)
    return task(
        f"Ивану Кузьмичу начислена заработная плата {salary} рублей. Из этой суммы вычитается налог на доходы физических лиц в размере 13%. "
        "Сколько рублей он получит после уплаты подоходного налога?",
        dec(salary * 87 // 100),
        f"{salary} · 0,87 = {salary * 87 // 100}.",
    )


def b15_raise(r):
    old = r.randrange(1000, 6001, 100)
    percent = r.choice([5, 8, 10, 12, 15, 16, 20, 25])
    new = old * (100 + percent) // 100
    return task(
        f"Цена на электрический чайник была повышена на {percent}% и составила {plural(new, 'рубль', 'рубля', 'рублей')}. Сколько рублей стоил чайник до повышения цены?",
        dec(old),
        f"Новая цена это {100 + percent}% старой: {new} : {dec(Fraction(100 + percent, 100))} = {old}.",
    )


def b15_school(r):
    while True:
        pupils = r.choice([400, 500, 600, 800, 1000, 1200])
        primary = r.choice([20, 25, 30, 35, 40])
        german = r.choice([10, 15, 20, 25, 30])
        value = Fraction(pupils * (100 - primary) * german, 10000)
        if value.denominator == 1:
            break
    return task(
        f"В школе {pupils} учеников, из них {primary}% учатся в начальной школе. Среди учеников средней и старшей школы {german}% изучают немецкий язык. "
        "Сколько учеников в школе изучают немецкий язык, если в начальной школе немецкий язык не изучается?",
        dec(value),
        f"В средней и старшей школе {pupils * (100 - primary) // 100} учеников, из них {german}% это {value}.",
    )


def b15_discount(r):
    price = r.choice([20, 24, 30, 40, 50, 60])
    percent = r.choice([10, 15, 20, 25, 30])
    money = r.choice([500, 600, 750, 900, 1000])
    new_price = Fraction(price * (100 - percent), 100)
    return task(
        f"Тетрадь стоит {price} рублей. Какое наибольшее число таких тетрадей можно будет купить на {money} рублей после понижения цены на {percent}%?",
        dec(math.floor(Fraction(money) / new_price)),
        f"Новая цена {dec(new_price)} руб.; {money} : {dec(new_price)} даёт целое число покупок {math.floor(Fraction(money) / new_price)}.",
    )


def b15_wholesale(r):
    retail = r.choice([120, 150, 180, 200, 240, 250])
    percent = r.choice([10, 15, 20, 25, 30])
    money = r.choice([5000, 8000, 10000, 12000])
    wholesale = Fraction(retail * (100 - percent), 100)
    return task(
        f"Розничная цена учебника {retail} рублей, а оптовая цена на {percent}% ниже розничной. Какое наибольшее число таких учебников можно купить "
        f"по оптовой цене на {money} рублей?",
        dec(math.floor(Fraction(money) / wholesale)),
        f"Оптовая цена {dec(wholesale)} руб.; целое число учебников равно {math.floor(Fraction(money) / wholesale)}.",
    )


# ---------------------------------------------------------------- №17 Простейшие уравнения


def b17_linear(r):
    a = r.choice([n for n in range(-9, 10) if n not in (0, 1)])
    x = r.randint(-15, 15)
    b = r.randint(-30, 30)
    return task(
        f"Найдите корень уравнения {poly([(a, 'x'), (b, '')])} = {a * x + b}.",
        dec(x),
        f"{a}x = {a * x}, x = {x}.",
    )


def b17_irrational(r):
    a = r.choice([n for n in range(-9, 10) if n != 0])
    c = r.randint(2, 11)
    x = r.randint(-20, 20)
    b = c * c - a * x
    return task(
        f"Найдите корень уравнения √({poly([(a, 'x'), (b, '')])}) = {c}.",
        dec(x),
        f"Возводим в квадрат: {poly([(a, 'x'), (b, '')])} = {c * c}, откуда x = {x}.",
    )


# ---------------------------------------------------------------- №18 Неравенства


def b18_exponential(r):
    base = r.choice([2, 3, 5])
    items = [
        (f"{base}ˣ ≥ {base}", "x ≥ 1"), (f"(1/{base})ˣ ≥ {base}", "x ≤ -1"),
        (f"(1/{base})ˣ ≤ {base}", "x ≥ -1"), (f"{base}ˣ ≤ {base}", "x ≤ 1"),
    ]
    order = list(range(4))
    r.shuffle(order)
    shown = list(range(4))
    r.shuffle(shown)
    made = matching(
        "Каждому из четырёх неравенств в левом столбце соответствует одно из решений в правом столбце. Установите соответствие между неравенствами и их решениями.",
        [items[i][0] for i in order], [items[i][1] for i in shown],
        "".join(str(shown.index(i) + 1) for i in order),
        f"При основании больше 1 знак неравенства сохраняется, при основании меньше 1 меняется на противоположный; (1/{base})ˣ = {base}⁻ˣ.",
    )
    made["key"] = f"exp:{base}:{order}:{shown}"
    return made


def b18_quadratic(r):
    a, b = sorted(r.sample(range(-6, 9), 2))
    left_a = poly([(1, "x"), (-a, "")])
    left_b = poly([(1, "x"), (-b, "")])
    items = [
        (f"({left_a})({left_b}) < 0", f"{a} < x < {b}"),
        (f"({left_a})({left_b}) > 0", f"x < {a} или x > {b}"),
        (f"({left_a})² · ({left_b}) < 0", f"x < {b}, x ≠ {a}"),
        (f"({left_a})² · ({left_b}) > 0", f"x > {b}"),
    ]
    order = list(range(4))
    r.shuffle(order)
    shown = list(range(4))
    r.shuffle(shown)
    made = matching(
        "Каждому из четырёх неравенств в левом столбце соответствует одно из решений в правом столбце. Установите соответствие между неравенствами и их решениями.",
        [items[i][0] for i in order], [items[i][1] for i in shown],
        "".join(str(shown.index(i) + 1) for i in order),
        "Решаем методом интервалов: множитель в квадрате не меняет знак произведения, но обращает его в ноль.",
    )
    made["key"] = f"quad:{a}:{b}:{order}:{shown}"
    return made


def b18_number_line(r):
    # Четыре числа в «неудобной» записи нужно расположить на прямой.
    pool = [
        ("log₂ 10", math.log2(10)), ("7/3", 7 / 3), ("√26", math.sqrt(26)), ("(3/5)⁻¹", 5 / 3), ("√7", math.sqrt(7)), ("log₃ 30", math.log(30, 3)),
        ("π", math.pi), ("√15", math.sqrt(15)), ("11/4", 2.75), ("log₂ 3", math.log2(3)), ("√2", math.sqrt(2)), ("(2/3)⁻²", 2.25),
        ("√40", math.sqrt(40)), ("log₅ 100", math.log(100, 5)), ("9/2", 4.5), ("√30", math.sqrt(30)),
    ]
    while True:
        picked = r.sample(pool, 4)
        values = sorted(v for _, v in picked)
        if all(b - a > 0.3 for a, b in zip(values, values[1:])):
            break
    by_value = sorted(picked, key=lambda item: item[1])
    fig = Fig(420, 90)
    low, high = 0, 7

    def px(x):
        return 20 + (x - low) * 380 / (high - low)

    fig.line(15, 45, 405, 45, 1)
    for tick in range(low, high + 1):
        fig.line(px(tick), 40, px(tick), 50, 1)
        fig.text(px(tick), 64, tick)
    for letter, (_, value) in zip("ABCD", by_value):
        fig.circle(px(value), 45, 4, 2)
        fig.text(px(value), 26, letter)
    shown = picked[:]
    r.shuffle(shown)
    answer = "".join(str(shown.index(item) + 1) for item in by_value)
    made = matching(
        "На координатной прямой отмечены точки A, B, C и D. Каждой точке соответствует одно из чисел в правом столбце. Установите соответствие между точками и числами. "
        "Буквам А, Б, В, Г отвечают точки A, B, C, D.",
        [f"точка {letter}" for letter in "ABCD"], [name for name, _ in shown], answer,
        "Приближённые значения: " + ", ".join(f"{name} ≈ {dec(round_half_up(Fraction(value).limit_denominator(1000), 2))}" for name, value in by_value) + ".",
    )
    made["figure"] = fig.data()
    return made


# ---------------------------------------------------------------- №19 Числа и их свойства


def digits_of(number):
    return [int(ch) for ch in str(number)]


def some_number(text, solutions, explanation):
    solutions = sorted(solutions)
    made = task(text + " В ответе укажите какое-нибудь одно такое число.", str(solutions[0]),
                explanation + " Подходят, например: " + ", ".join(str(n) for n in solutions[:4]) + ".")
    made["answers"] = [str(n) for n in solutions]
    made["kind"] = "exact"
    return made


def b19_remainders(r):
    while True:
        low = r.choice([200, 300, 400, 500, 600])
        divisors = r.choice([(4, 5, 6), (3, 4, 5), (2, 5, 7), (3, 5, 8), (4, 6, 7)])
        remainder = r.randint(1, 2)
        solutions = [n for n in range(low + 1, 1000) if all(n % d == remainder for d in divisors) and len(set(digits_of(n))) == 2]
        if 1 <= len(solutions) <= 30:
            break
    return some_number(
        f"Найдите трёхзначное натуральное число, большее {low}, которое при делении на {divisors[0]}, на {divisors[1]} и на {divisors[2]} даёт в остатке {remainder} "
        "и в записи которого есть только две различные цифры.",
        solutions, "Число на " + str(remainder) + " больше числа, кратного всем трём делителям.")


def b19_product(r):
    while True:
        divisor = r.choice([11, 12, 15, 18, 22, 25, 33, 45])
        product = r.choice([12, 16, 18, 20, 24, 30, 36, 40, 48, 60, 72])
        solutions = [n for n in range(1000, 10000) if n % divisor == 0 and math.prod(digits_of(n)) == product]
        if 1 <= len(solutions) <= 30:
            break
    return some_number(
        f"Найдите четырёхзначное число, кратное {divisor}, произведение цифр которого равно {product}.",
        solutions, f"Цифры подбираются из разложения числа {product} на множители с учётом делимости на {divisor}.")


def b19_cross_out(r):
    while True:
        number = "".join(str(r.randint(1, 9)) for _ in range(8))
        divisor = r.choice([12, 15, 18, 22, 24, 36])
        remove = 3
        solutions = set()
        for i in range(8):
            for j in range(i + 1, 8):
                for k in range(j + 1, 8):
                    rest = int("".join(ch for index, ch in enumerate(number) if index not in (i, j, k)))
                    if rest % divisor == 0:
                        solutions.add(rest)
        if 1 <= len(solutions) <= 30:
            break
    made = task(
        f"Вычеркните в числе {number} три цифры так, чтобы получившееся число делилось на {divisor}. В ответе укажите какое-нибудь одно получившееся число.",
        str(sorted(solutions)[0]),
        f"Используем признаки делимости на множители числа {divisor}. Подходят, например: " + ", ".join(str(n) for n in sorted(solutions)[:4]) + ".",
    )
    made["answers"] = [str(n) for n in sorted(solutions)]
    made["kind"] = "exact"
    return made


def b19_digit_sum(r):
    while True:
        total = r.randint(15, 24)
        divisor, not_divisor = r.choice([(3, 9), (2, 4), (5, 25)])
        solutions = [n for n in range(100, 1000) if sum(digits_of(n)) == total
                     and sum(d * d for d in digits_of(n)) % divisor == 0 and sum(d * d for d in digits_of(n)) % not_divisor != 0]
        if 1 <= len(solutions) <= 40:
            break
    return some_number(
        f"Найдите трёхзначное число, сумма цифр которого равна {total}, а сумма квадратов цифр делится на {divisor}, но не делится на {not_divisor}.",
        solutions, "Перебираем наборы цифр с нужной суммой и проверяем сумму квадратов.")


# ---------------------------------------------------------------- №21 Задачи на смекалку


def b21_snail(r):
    up, down = r.randint(3, 7), r.randint(1, 3)
    if up <= down:
        return b21_snail(r)
    height = r.randint(up + 3, 30)
    days, position = 0, 0
    while True:
        days += 1
        position += up
        if position >= height:
            break
        position -= down
    return task(
        f"Улитка за день заползает вверх по дереву на {up} м, а за ночь сползает на {down} м. Высота дерева {height} м. "
        "За сколько дней улитка впервые доползёт до вершины дерева?",
        dec(days),
        f"За сутки улитка поднимается на {up - down} м, но в последний день ей достаточно подняться на {up} м без спуска. Получается дней: {days}.",
    )


def b21_coins(r):
    k = r.choice([2, 4, 6, 8, 10, 12, 20])
    return task(
        "В обменном пункте можно совершить одну из двух операций: за 2 золотые монеты получить 3 серебряные и одну медную; за 5 серебряных монет получить 3 золотые и одну медную. "
        f"У Николая были только серебряные монеты. После нескольких посещений обменного пункта серебряных монет у него стало меньше, золотых не появилось, зато появилось {5 * k} медных. "
        "На сколько уменьшилось количество серебряных монет у Николая?",
        dec(k),
        f"Золотых не осталось, значит первых операций было 3n, вторых 2n. Медных монет 5n = {5 * k}, n = {k}. Серебряных: +9n - 10n = -{k}.",
    )


def b21_stick(r):
    red, yellow, green = r.sample(range(3, 16), 3)
    return task(
        f"На палке отмечены поперечные линии красного, жёлтого и зелёного цвета. Если распилить палку по красным линиям, получится {red} кусков, "
        f"если по жёлтым, то {yellow} кусков, а если по зелёным, то {green} кусков. Сколько кусков получится, если распилить палку по линиям всех трёх цветов?",
        dec(red + yellow + green - 2),
        f"Линий: {red - 1} красных, {yellow - 1} жёлтых и {green - 1} зелёных, всего {red + yellow + green - 3}. Кусков на один больше: {red + yellow + green - 2}.",
    )


def b21_mushrooms(r):
    total = r.randint(25, 60)
    a = r.randint(8, total - 10)
    first_any = total - a + 1
    second_any = a + 1
    return task(
        f"В корзине лежит {plural(total, 'гриб', 'гриба', 'грибов')}: рыжики и грузди. Известно, что среди любых {first_any} грибов имеется хотя бы один рыжик, "
        f"а среди любых {second_any} грибов хотя бы один груздь. Сколько рыжиков в корзине?",
        dec(a),
        f"Груздей не больше {first_any - 1}, рыжиков не больше {second_any - 1}; в сумме их {total}, значит рыжиков ровно {a}.",
    )


def b21_grasshopper(r):
    jumps = r.randint(5, 20)
    return task(
        f"Кузнечик прыгает вдоль координатной прямой в любом направлении на единичный отрезок за один прыжок. Сколько существует различных точек на координатной прямой, "
        f"в которых кузнечик может оказаться, сделав ровно {jumps} прыжков, начиная прыгать из начала координат?",
        dec(jumps + 1),
        f"Чётность координаты совпадает с чётностью числа прыжков. Подходят точки от -{jumps} до {jumps} через одну: их {jumps + 1}.",
    )


def b21_flat(r):
    while True:
        floors = r.choice([5, 7, 9, 10, 12])
        per_floor = r.randint(3, 8)
        entrance = r.randint(3, 9)
        floor = r.randint(1, floors)
        flat = (entrance - 1) * floors * per_floor + (floor - 1) * per_floor + r.randint(1, per_floor)
        # Задача корректна, если по номеру квартиры и подъезду этаж определяется однозначно.
        fits = {(flat - (entrance - 1) * floors * k - 1) // k + 1 for k in range(1, 20)
                if (entrance - 1) * floors * k < flat <= entrance * floors * k}
        if fits == {floor}:
            break
    return task(
        f"Саша пригласил Петю в гости, сказав, что живёт в {entrance}-м подъезде в квартире № {flat}, а этаж сказать забыл. Подойдя к дому, Петя обнаружил, "
        f"что дом {floors}-этажный. На каком этаже живёт Саша? На всех этажах число квартир одинаково, номера квартир в доме начинаются с единицы.",
        dec(floor),
        f"Подбираем число квартир на этаже так, чтобы квартира {flat} попала в {entrance}-й подъезд; при любом подходящем варианте этаж получается {floor}.",
    )


NUMBERS = [
    Entry(1, "Простейшие текстовые задачи", 1, [b1_packs, b1_boats, b1_promo, b1_floor, b1_bags]),
    Entry(2, "Размеры и единицы измерения", 1, [b2_units]),
    Entry(3, "Чтение графиков и диаграмм", 1, [b3_bar_chart, b3_line_chart, b3_price_graph]),
    Entry(4, "Преобразования выражений", 1, [b4_formula]),
    Entry(5, "Начала теории вероятностей", 1, [b5_taxi, b5_pen, b5_topics, prof.pr_sportsmen, prof.pr_defect, prof.pr_tickets, prof.pr_coin]),
    Entry(6, "Выбор оптимального варианта", 1, [b6_carriers, b6_internet, b6_route]),
    Entry(7, "Анализ графиков и диаграмм", 1, [b7_function_points, b7_speed_intervals]),
    Entry(8, "Анализ утверждений", 1, [b8_clubs, b8_order, b8_implication]),
    Entry(9, "Задачи на квадратной решётке", 1, [b9_triangle, b9_trapezoid, b9_rhombus, b9_plan]),
    Entry(10, "Прикладная геометрия", 1, [b10_fence, b10_wheel, b10_stairs, b10_clock, b10_parquet, b10_shadow]),
    Entry(11, "Прикладная стереометрия", 1, [b11_aquarium, b11_detail, b11_faces, b11_mugs, b11_pour]),
    Entry(12, "Планиметрия", 1, [prof.p1_right_triangle, prof.p1_isosceles, prof.p1_parallelogram, prof.p1_trapezoid, prof.p1_circle_angles, prof.p1_incircle]),
    Entry(13, "Задачи по стереометрии", 1, [prof.s_cube, prof.s_box, prof.s_pyramid, prof.s_cylinder, prof.s_cone, prof.s_sphere]),
    Entry(14, "Вычисления", 1, [b14_decimals, b14_fractions]),
    Entry(15, "Простейшие текстовые задачи: проценты", 1, [b15_tax, b15_raise, b15_school, b15_discount, b15_wholesale]),
    Entry(16, "Вычисления и преобразования", 1, [prof.t_powers, prof.t_roots, prof.t_logs, prof.t_trig]),
    Entry(17, "Простейшие уравнения", 1, [b17_linear, prof.e_quadratic, b17_irrational, prof.e_exponential, prof.e_logarithm]),
    Entry(18, "Неравенства", 1, [b18_exponential, b18_quadratic, b18_number_line]),
    Entry(19, "Числа и их свойства", 1, [b19_remainders, b19_product, b19_cross_out, b19_digit_sum]),
    Entry(20, "Текстовые задачи", 1, [prof.w_boat, prof.w_cyclist, prof.w_pipes, prof.w_alloy, prof.w_solution, prof.w_percent, prof.w_train]),
    Entry(21, "Задачи на смекалку", 1, [b21_snail, b21_coins, b21_stick, b21_mushrooms, b21_grasshopper, b21_flat]),
]
