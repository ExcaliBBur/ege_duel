"""Физика: задания №1-20 (первая часть) по структуре ЕГЭ 2026.

№5, 9, 14, 18: выбор всех верных утверждений (2 балла). №6, 10, 15, 17: изменение величин
или соответствие (2 балла). №19: показания прибора с погрешностью. №20: выбор установок для опыта.
"""

from fractions import Fraction

import figures
from exam_common import Entry, changes, choose, formulas, is_finite_decimal, pick_statements, table_figure
from figures import Fig
from generators import dec, poly, sub, sup, task

G = "Ускорение свободного падения считайте равным 10 м/с²."
NO_AIR = "Сопротивлением воздуха пренебрегите."


def times(factor) -> str:
    """«в 2 раза», «в 5 раз», «в 1,5 раза»."""
    factor = Fraction(factor)
    word = "раза" if factor.denominator != 1 or (factor.numerator % 10 in (2, 3, 4) and factor.numerator % 100 not in (12, 13, 14)) else "раз"
    return f"в {dec(factor)} {word}"


def nuclide(mass, charge, symbol) -> str:
    return f"{sup(mass)}{sub(charge)}{symbol}"


# ---------------------------------------------------------------- №1 Кинематика


def k_law(r):
    x0, v0 = r.randint(-20, 20), r.choice([n for n in range(-12, 13) if n != 0])
    a, t = r.choice([-6, -4, -2, 2, 4, 6]), r.randint(1, 6)
    law = "x(t) = " + poly([(x0, ""), (v0, "t"), (Fraction(a, 2), "t²")])
    if r.random() < 0.3:
        return task(
            f"Координата тела, движущегося вдоль оси Ox, меняется по закону {law}, где все величины выражены в единицах СИ. "
            "Чему равна проекция ускорения тела на ось Ox? Ответ дайте в м/с².",
            dec(a), f"Коэффициент при t² равен половине ускорения: a = {a} м/с².")
    return task(
        f"Координата тела, движущегося вдоль оси Ox, меняется по закону {law}, где все величины выражены в единицах СИ. "
        f"Чему равна проекция скорости тела на ось Ox в момент времени t = {t} с? Ответ дайте в м/с.",
        dec(v0 + a * t), f"v = v₀ + a · t, где v₀ = {v0} м/с, a = {a} м/с²; при t = {t} с получаем {v0 + a * t} м/с.")


def k_circular(r):
    while True:
        speed = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
        radius = Fraction(r.choice([5, 10, 20, 25, 40, 50, 80, 100, 200, 250, 500]), 10)
        acceleration = Fraction(speed * speed) / radius
        if is_finite_decimal(acceleration) and acceleration <= 100:
            break
    return task(
        f"Материальная точка равномерно движется по окружности радиусом {dec(radius)} м со скоростью {speed} м/с. "
        "Чему равно центростремительное ускорение точки? Ответ дайте в м/с².",
        dec(acceleration), f"a = v² : R = {speed * speed} : {dec(radius)} = {dec(acceleration)} м/с².")


def k_relative(r):
    first, second = r.sample(range(40, 121, 5), 2)
    if r.random() < 0.5:
        return task(
            f"Два автомобиля движутся по прямому шоссе навстречу друг другу: первый со скоростью {first} км/ч, второй со скоростью {second} км/ч. "
            "Чему равен модуль скорости первого автомобиля в системе отсчёта, связанной со вторым автомобилем? Ответ дайте в км/ч.",
            dec(first + second), f"При встречном движении скорости складываются: {first} + {second} = {first + second} км/ч.")
    return task(
        f"Два автомобиля движутся по прямому шоссе в одном направлении: первый со скоростью {first} км/ч, второй со скоростью {second} км/ч. "
        "Чему равен модуль скорости первого автомобиля в системе отсчёта, связанной со вторым автомобилем? Ответ дайте в км/ч.",
        dec(abs(first - second)), f"При движении в одну сторону скорости вычитаются: |{first} - {second}| = {abs(first - second)} км/ч.")


def k_average(r):
    first, second, average = r.choice([(40, 60, 48), (30, 60, 40), (20, 30, 24), (60, 90, 72), (40, 120, 60), (30, 70, 42), (50, 75, 60), (20, 80, 32), (45, 90, 60)])
    if r.random() < 0.5:
        first, second = second, first
    if r.random() < 0.5:
        return task(
            f"Первую половину пути автомобиль проехал со скоростью {first} км/ч, а вторую половину пути со скоростью {second} км/ч. "
            "Найдите среднюю скорость автомобиля на всём пути. Ответ дайте в км/ч.",
            dec(average), f"vср = 2 · v₁ · v₂ : (v₁ + v₂) = 2 · {first} · {second} : {first + second} = {average} км/ч.")
    return task(
        f"Первую половину времени движения автомобиль ехал со скоростью {first} км/ч, а вторую половину времени со скоростью {second} км/ч. "
        "Найдите среднюю скорость автомобиля за всё время движения. Ответ дайте в км/ч.",
        dec(Fraction(first + second, 2)), f"При равных промежутках времени vср = (v₁ + v₂) : 2 = {dec(Fraction(first + second, 2))} км/ч.")


def k_throw(r):
    speed, height = r.choice([(10, 5), (20, 20), (30, 45), (40, 80), (6, Fraction(18, 10)), (8, Fraction(32, 10)), (12, Fraction(72, 10)), (4, Fraction(8, 10)), (16, Fraction(128, 10))])
    kind = r.choice(["height", "time", "speed"])
    if kind == "height":
        return task(
            f"Тело брошено вертикально вверх с начальной скоростью {speed} м/с. На какую максимальную высоту оно поднимется? {G} {NO_AIR} Ответ дайте в метрах.",
            dec(height), f"h = v₀² : (2g) = {speed * speed} : 20 = {dec(height)} м.")
    if kind == "time":
        return task(
            f"Тело брошено вертикально вверх с начальной скоростью {speed} м/с. Через какое время после броска оно достигнет высшей точки траектории? {G} {NO_AIR} Ответ дайте в секундах.",
            dec(Fraction(speed, 10)), f"t = v₀ : g = {speed} : 10 = {dec(Fraction(speed, 10))} с.")
    return task(
        f"Тело свободно падает без начальной скорости с высоты {dec(height)} м. Чему равна скорость тела в момент падения на землю? {G} {NO_AIR} Ответ дайте в м/с.",
        dec(speed), f"v = √(2gh) = √(20 · {dec(height)}) = {speed} м/с.")


# ---------------------------------------------------------------- №2 Динамика


def d_resultant(r):
    while True:
        scale, mass = r.randint(1, 8), r.choice([1, 2, 4, 5, 8, 10, 20, 25])
        acceleration = Fraction(5 * scale, mass)
        if is_finite_decimal(acceleration) and acceleration <= 20:
            break
    return task(
        f"На тело массой {mass} кг действуют две силы, направленные перпендикулярно друг другу: {3 * scale} Н и {4 * scale} Н. "
        "С каким ускорением движется тело? Ответ дайте в м/с².",
        dec(acceleration), f"Равнодействующая равна √({3 * scale}² + {4 * scale}²) = {5 * scale} Н, a = F : m = {dec(acceleration)} м/с².")


def d_friction(r):
    mass = Fraction(r.choice([5, 10, 15, 20, 25, 40, 50, 80]), 10)
    mu = Fraction(r.choice([1, 2, 3, 4, 5]), 10)
    return task(
        f"Брусок массой {dec(mass)} кг скользит по горизонтальной поверхности. Коэффициент трения между бруском и поверхностью равен {dec(mu)}. "
        f"Чему равна сила трения скольжения, действующая на брусок? {G} Ответ дайте в ньютонах.",
        dec(mu * mass * 10), f"Fтр = μ · m · g = {dec(mu)} · {dec(mass)} · 10 = {dec(mu * mass * 10)} Н.")


def d_spring(r):
    stiffness = r.choice([50, 100, 200, 250, 400, 500])
    first, second = r.sample([1, 2, 3, 4, 5, 6, 8], 2)
    force_first, force_second = Fraction(stiffness * first, 100), Fraction(stiffness * second, 100)
    kind = r.choice(["stiffness", "second", "force"])
    if kind == "stiffness":
        return task(
            f"Под действием силы {dec(force_first)} Н пружина удлинилась на {first} см. Чему равна жёсткость пружины? Ответ дайте в Н/м.",
            dec(stiffness), f"k = F : x = {dec(force_first)} : {dec(Fraction(first, 100))} = {stiffness} Н/м.")
    if kind == "second":
        return task(
            f"Под действием силы {dec(force_first)} Н пружина удлинилась на {first} см. На сколько сантиметров удлинится эта пружина под действием силы {dec(force_second)} Н?",
            dec(second), f"Удлинение пропорционально силе: x = {first} · {dec(force_second)} : {dec(force_first)} = {second} см.")
    return task(
        f"Жёсткость пружины равна {stiffness} Н/м. Какая сила упругости возникает в пружине при её растяжении на {first} см? Ответ дайте в ньютонах.",
        dec(force_first), f"F = k · x = {stiffness} · {dec(Fraction(first, 100))} = {dec(force_first)} Н.")


def d_gravity(r):
    farther, heavier = r.choice([2, 3, 4]), r.choice([1, 2, 3, 4])
    force = farther * farther * r.randint(1, 9)
    change = f"расстояние между их центрами увеличить {times(farther)}" + ("" if heavier == 1 else f", а массу одного из шаров увеличить {times(heavier)}")
    return task(
        f"Два однородных шара притягиваются друг к другу с силой {force} мкН. Какой станет сила притяжения, если {change}? Ответ дайте в мкН.",
        dec(Fraction(force * heavier, farther * farther)),
        f"Сила пропорциональна массам и обратно пропорциональна квадрату расстояния: {force} · {heavier} : {farther * farther} = {dec(Fraction(force * heavier, farther * farther))} мкН.")


def d_elevator(r):
    mass, acceleration = r.choice([40, 50, 60, 70, 80]), r.choice([1, 2, 3, 4])
    up = r.random() < 0.5
    weight = mass * (10 + acceleration if up else 10 - acceleration)
    return task(
        f"Человек массой {mass} кг стоит в лифте, который движется с ускорением {acceleration} м/с², направленным {'вверх' if up else 'вниз'}. "
        f"Чему равен вес человека? {G} Ответ дайте в ньютонах.",
        dec(weight), f"P = m · (g {'+' if up else '-'} a) = {mass} · {10 + acceleration if up else 10 - acceleration} = {weight} Н.")


def d_second_law(r):
    mass = r.choice([2, 4, 5, 8, 10])
    first, second = r.sample([1, 2, 3, 4, 5, 6], 2)
    return task(
        f"Под действием силы {mass * first} Н тело движется с ускорением {first} м/с². С каким ускорением будет двигаться это тело под действием силы {mass * second} Н? Ответ дайте в м/с².",
        dec(second), f"Масса тела равна {mass * first} : {first} = {mass} кг, a = {mass * second} : {mass} = {second} м/с².")


# ---------------------------------------------------------------- №3 Законы сохранения в механике


def z_inelastic(r):
    while True:
        first, second, common = r.randint(1, 6), r.randint(1, 6), r.randint(1, 8)
        if common * (first + second) % first == 0 and common * (first + second) // first <= 20:
            break
    speed = common * (first + second) // first
    return task(
        f"Тележка массой {first} кг, движущаяся со скоростью {speed} м/с, сталкивается с неподвижной тележкой массой {second} кг и сцепляется с ней. "
        "С какой скоростью будут двигаться тележки после сцепки? Ответ дайте в м/с.",
        dec(common), f"По закону сохранения импульса {first} · {speed} = ({first} + {second}) · u, откуда u = {common} м/с.")


def z_rebound(r):
    mass, speed = r.choice([50, 100, 200, 250, 400, 500]), r.choice([2, 4, 5, 6, 8, 10, 12])
    return task(
        f"Мяч массой {mass} г, летящий со скоростью {speed} м/с перпендикулярно стене, упруго отскакивает от неё с такой же по модулю скоростью. "
        "Чему равен модуль изменения импульса мяча? Ответ дайте в кг·м/с.",
        dec(Fraction(2 * mass * speed, 1000)), f"Импульс меняет направление на противоположное: Δp = 2 · m · v = 2 · {dec(Fraction(mass, 1000))} · {speed} = {dec(Fraction(2 * mass * speed, 1000))} кг·м/с.")


def z_energy_height(r):
    speed, height = r.choice([(10, Fraction(5, 2)), (20, 10), (30, Fraction(45, 2)), (40, 40), (4, Fraction(4, 10)), (8, Fraction(16, 10)), (12, Fraction(36, 10))])
    return task(
        f"Камень брошен вертикально вверх с начальной скоростью {speed} м/с. На какой высоте кинетическая энергия камня будет равна его потенциальной энергии? "
        f"Потенциальную энергию отсчитывайте от уровня броска. {G} {NO_AIR} Ответ дайте в метрах.",
        dec(height), f"m · v₀² : 2 = 2 · m · g · h, откуда h = v₀² : (4g) = {speed * speed} : 40 = {dec(height)} м.")


def z_power(r):
    force, speed = r.choice([1, 2, 3, 4, 5, 6, 8]), r.choice([10, 15, 20, 25, 30])
    return task(
        f"Автомобиль движется равномерно со скоростью {speed} м/с, сила тяги двигателя равна {force} кН. Какую мощность развивает двигатель? Ответ дайте в кВт.",
        dec(force * speed), f"N = F · v = {force} кН · {speed} м/с = {force * speed} кВт.")


def z_kinetic_change(r):
    energy, factor = r.randint(2, 30), r.choice([2, 3, 4])
    if r.random() < 0.5:
        return task(
            f"Кинетическая энергия тела равна {energy} Дж. Чему станет равна кинетическая энергия тела, если его скорость увеличить {times(factor)}? Ответ дайте в джоулях.",
            dec(energy * factor * factor), f"Энергия пропорциональна квадрату скорости: {energy} · {factor * factor} = {energy * factor * factor} Дж.")
    return task(
        f"Кинетическая энергия тела равна {energy * factor * factor} Дж. Чему станет равна кинетическая энергия тела, если его скорость уменьшить {times(factor)}? Ответ дайте в джоулях.",
        dec(energy), f"Энергия пропорциональна квадрату скорости: {energy * factor * factor} : {factor * factor} = {energy} Дж.")


def z_spring_energy(r):
    stiffness, stretch = r.choice([100, 200, 400, 500, 800, 1000]), r.choice([2, 4, 5, 10, 20])
    energy = Fraction(stiffness * stretch * stretch, 20000)
    return task(
        f"Пружину жёсткостью {stiffness} Н/м растянули на {stretch} см. Чему равна потенциальная энергия упругой деформации пружины? Ответ дайте в джоулях.",
        dec(energy), f"E = k · x² : 2 = {stiffness} · {dec(Fraction(stretch, 100))}² : 2 = {dec(energy)} Дж.")


def z_work(r):
    mass, height = r.randint(2, 40), r.randint(2, 15)
    seconds = r.choice([2, 4, 5, 10, 20])
    power = Fraction(mass * 10 * height, seconds)
    return task(
        f"Подъёмник равномерно поднимает груз массой {mass} кг на высоту {height} м за {seconds} с. Какую полезную мощность он развивает? {G} Ответ дайте в ваттах.",
        dec(power), f"N = m · g · h : t = {mass} · 10 · {height} : {seconds} = {dec(power)} Вт.")


# ---------------------------------------------------------------- №4 Статика. Механические колебания и волны


def s_lever(r):
    while True:
        force, arm, other_arm = r.randint(2, 30), r.choice([10, 15, 20, 25, 30, 40, 50, 60]), r.choice([10, 15, 20, 25, 30, 40, 50, 60])
        other = Fraction(force * arm, other_arm)
        if arm != other_arm and other.denominator == 1:
            break
    return task(
        f"Рычаг находится в равновесии под действием двух сил. Первая сила равна {force} Н, её плечо {arm} см. Плечо второй силы равно {other_arm} см. "
        "Чему равна вторая сила? Ответ дайте в ньютонах.",
        dec(other), f"F₁ · l₁ = F₂ · l₂, откуда F₂ = {force} · {arm} : {other_arm} = {dec(other)} Н.")


def s_depth(r):
    liquid, density = r.choice([("воды", 1000), ("керосина", 800), ("морской воды", 1030), ("масла", 900)])
    depth = r.choice([2, 4, 5, 10, 20, 25, 40, 50])
    return task(
        f"Чему равно давление, которое создаёт столб {liquid} высотой {depth} м? Плотность {liquid} равна {density} кг/м³. {G} Ответ дайте в килопаскалях.",
        dec(Fraction(density * 10 * depth, 1000)), f"p = ρ · g · h = {density} · 10 · {depth} = {density * 10 * depth} Па = {dec(Fraction(density * 10 * depth, 1000))} кПа.")


def s_archimedes(r):
    volume = r.choice([2, 4, 5, 10, 20, 25, 50])
    if r.random() < 0.5:
        return task(
            f"Тело объёмом {volume} дм³ полностью погружено в воду. Чему равна действующая на него сила Архимеда? Плотность воды 1000 кг/м³. {G} Ответ дайте в ньютонах.",
            dec(10 * volume), f"F = ρ · g · V = 1000 · 10 · {dec(Fraction(volume, 1000))} = {10 * volume} Н.")
    mass = Fraction(r.choice([2, 4, 5, 8, 12, 15, 25, 30]), 10)
    return task(
        f"Деревянный брусок массой {dec(mass)} кг плавает на поверхности воды. Чему равна действующая на него сила Архимеда? {G} Ответ дайте в ньютонах.",
        dec(mass * 10), f"Брусок плавает, значит сила Архимеда равна силе тяжести: {dec(mass)} · 10 = {dec(mass * 10)} Н.")


def s_period_scaling(r):
    period = Fraction(r.choice([2, 4, 5, 6, 8, 10, 12, 15]), 10)
    factor, root = r.choice([(4, 2), (9, 3), (16, 4)])
    kind = r.choice(["mass_up", "stiffness_up", "length_up"])
    if kind == "mass_up":
        return task(
            f"Период колебаний груза на пружине равен {dec(period)} с. Каким станет период колебаний, если массу груза увеличить {times(factor)}? Ответ дайте в секундах.",
            dec(period * root), f"Период пропорционален √m: {dec(period)} · {root} = {dec(period * root)} с.")
    if kind == "stiffness_up":
        return task(
            f"Период колебаний груза на пружине равен {dec(period * root)} с. Каким станет период колебаний, если пружину заменить другой, жёсткость которой {times(factor)} больше? Ответ дайте в секундах.",
            dec(period), f"Период обратно пропорционален √k: {dec(period * root)} : {root} = {dec(period)} с.")
    return task(
        f"Период колебаний математического маятника равен {dec(period)} с. Каким станет период колебаний, если длину нити увеличить {times(factor)}? Ответ дайте в секундах.",
        dec(period * root), f"Период пропорционален √l: {dec(period)} · {root} = {dec(period * root)} с.")


def s_count(r):
    count, period = r.choice([10, 20, 25, 40, 50]), Fraction(r.choice([2, 4, 5, 8, 16, 20, 25]), 10)
    seconds = count * period
    if r.random() < 0.5:
        return task(
            f"Маятник совершает {count} колебаний за {dec(seconds)} с. Чему равен период колебаний маятника? Ответ дайте в секундах.",
            dec(period), f"T = t : N = {dec(seconds)} : {count} = {dec(period)} с.")
    return task(
        f"Маятник совершает {count} колебаний за {dec(seconds)} с. Чему равна частота колебаний маятника? Ответ дайте в герцах.",
        dec(1 / period), f"ν = N : t = {count} : {dec(seconds)} = {dec(1 / period)} Гц.")


def s_wave(r):
    length, period = r.choice([2, 3, 4, 5, 6, 8, 10, 12]), r.choice([1, 2, 4, 5])
    if r.random() < 0.5:
        return task(
            f"Расстояние между соседними гребнями волны на поверхности воды равно {length} м, период колебаний частиц в волне {period} с. "
            "С какой скоростью распространяется волна? Ответ дайте в м/с.",
            dec(Fraction(length, period)), f"v = λ : T = {length} : {period} = {dec(Fraction(length, period))} м/с.")
    speed, frequency = r.choice([(340, 170), (340, 85), (340, 680), (340, 1700), (1500, 500), (1500, 750), (1500, 3000), (5000, 2500), (5000, 1000)])
    return task(
        f"Звуковая волна частотой {frequency} Гц распространяется в среде со скоростью {speed} м/с. Чему равна длина волны? Ответ дайте в метрах.",
        dec(Fraction(speed, frequency)), f"λ = v : ν = {speed} : {frequency} = {dec(Fraction(speed, frequency))} м.")


# ---------------------------------------------------------------- №5 Механика: анализ процессов


def a_throw(r):
    speed = r.choice([10, 20, 30, 40])
    mass = Fraction(r.choice([1, 2, 5, 10, 20]), 10)
    top, height, energy = speed // 10, speed * speed // 20, mass * speed * speed / 2
    pool = [
        [(f"Тело достигло высшей точки траектории через {top} с после броска.", True), (f"Тело достигло высшей точки траектории через {2 * top} с после броска.", False)],
        [(f"Максимальная высота подъёма тела равна {height} м.", True), (f"Максимальная высота подъёма тела равна {2 * height} м.", False)],
        [(f"Начальная кинетическая энергия тела равна {dec(energy)} Дж.", True), (f"Начальная кинетическая энергия тела равна {dec(2 * energy)} Дж.", False)],
        ("В высшей точке траектории ускорение тела равно нулю.", False),
        ("В высшей точке траектории импульс тела равен нулю.", True),
        ("Полная механическая энергия тела в процессе движения не изменяется.", True),
        (f"Через {2 * top} с после броска тело вернулось в точку броска.", True),
        ("При подъёме тела сила тяжести совершает положительную работу.", False),
        ("Потенциальная энергия тела в высшей точке, отсчитанная от уровня броска, меньше его начальной кинетической энергии.", False),
    ]
    texts, flags = pick_statements(r, pool)
    return choose(
        f"Тело массой {dec(mass)} кг бросили вертикально вверх с начальной скоростью {speed} м/с. {NO_AIR} {G} Выберите все верные утверждения о движении тела.",
        texts, flags, f"Время подъёма v₀ : g = {top} с, высота подъёма v₀² : (2g) = {height} м, начальная кинетическая энергия {dec(energy)} Дж.")


def a_graph(r):
    while True:
        first, steady, last = r.choice([2, 3, 4, 5]), r.choice([2, 3, 4]), r.choice([1, 2, 4])
        speed = r.choice([4, 6, 8, 10, 12])
        if is_finite_decimal(Fraction(speed, first)) and first != last and first + steady + last <= 12:
            break
    second, end = first + steady, first + steady + last
    fig = Fig()
    px = figures.axes(fig, 46, 228, 28, 15, 12, 13, "t, с", "v, м/с", 1, 2)
    for (x1, y1), (x2, y2) in [((0, 0), (first, speed)), ((first, speed), (second, speed)), ((second, speed), (end, 0))]:
        fig.line(*px(x1, y1), *px(x2, y2), 2)
    start_acceleration = Fraction(speed, first)
    total = Fraction(speed * first, 2) + speed * steady + Fraction(speed * last, 2)
    pool = [
        [(f"В интервале времени от 0 до {first} с тело двигалось с ускорением {dec(start_acceleration)} м/с².", True),
         (f"В интервале времени от 0 до {first} с тело двигалось с ускорением {speed} м/с².", False)],
        [(f"В интервале времени от {first} до {second} с тело прошло путь {speed * steady} м.", True),
         (f"В интервале времени от {first} до {second} с тело прошло путь {dec(Fraction(speed * steady, 2))} м.", False)],
        (f"В интервале времени от {second} до {end} с тело двигалось в направлении, противоположном первоначальному.", False),
        (f"В интервале времени от {first} до {second} с равнодействующая сил, действующих на тело, равна нулю.", True),
        (f"Модуль ускорения тела в интервале от {second} до {end} с больше, чем в интервале от 0 до {first} с.", last < first),
        [(f"За всё время движения тело прошло путь {dec(total)} м.", True), (f"За всё время движения тело прошло путь {speed * end} м.", False)],
        (f"Кинетическая энергия тела в момент времени {first} с меньше, чем в момент времени {first - 1} с.", False),
        (f"В момент времени {end} с тело остановилось.", True),
    ]
    texts, flags = pick_statements(r, pool)
    made = choose(
        "На рисунке показан график зависимости проекции скорости тела, движущегося вдоль оси Ox, от времени. Выберите все верные утверждения о движении тела.",
        texts, flags, f"Ускорение на первом участке {dec(start_acceleration)} м/с², путь равен площади под графиком: всего {dec(total)} м.")
    made["figure"] = fig.data()
    return made


def a_pendulum(r):
    count, period = r.choice([10, 20, 25, 40, 50]), Fraction(r.choice([2, 4, 5, 8, 16, 20, 25]), 10)
    seconds, frequency = count * period, 1 / period
    pool = [
        [(f"Период колебаний маятника равен {dec(period)} с.", True), (f"Период колебаний маятника равен {dec(frequency)} с.", False)],
        [(f"Частота колебаний маятника равна {dec(frequency)} Гц.", True), (f"Частота колебаний маятника равна {dec(2 * frequency)} Гц.", False)],
        ("Если длину нити увеличить в 4 раза, период колебаний увеличится в 2 раза.", True),
        ("Если массу груза увеличить в 4 раза, период колебаний увеличится в 2 раза.", False),
        ("При прохождении положения равновесия скорость груза максимальна.", True),
        ("В точках максимального отклонения кинетическая энергия груза максимальна.", False),
        ("В точках максимального отклонения потенциальная энергия груза максимальна.", True),
        ("Если амплитуду малых колебаний уменьшить в 2 раза, период колебаний тоже уменьшится в 2 раза.", False),
        (f"За {dec(6 * period)} с маятник совершает 6 полных колебаний.", True),
    ]
    texts, flags = pick_statements(r, pool)
    return choose(
        f"Математический маятник совершает малые свободные колебания: {count} полных колебаний за {dec(seconds)} с. Выберите все верные утверждения.",
        texts, flags, f"T = {dec(seconds)} : {count} = {dec(period)} с, ν = {dec(frequency)} Гц. Период зависит только от длины нити и ускорения свободного падения.")


# ---------------------------------------------------------------- №6 Механика: изменение величин, соответствие

INCREASE_LEAD = "Как изменятся при этом"

MECHANICS_CHANGES = [
    ("Искусственный спутник Земли перешёл с одной круговой орбиты на другую, более высокую.", INCREASE_LEAD,
     {"скорость спутника": 2, "период обращения спутника": 1, "центростремительное ускорение спутника": 2, "сила притяжения спутника к Земле": 2,
      "потенциальная энергия спутника в поле тяжести Земли": 1},
     "С ростом радиуса орбиты скорость √(GM/R), ускорение и сила притяжения уменьшаются, период и потенциальная энергия растут."),
    ("Груз пружинного маятника заменили грузом большей массы, пружину и амплитуду колебаний оставили прежними.", INCREASE_LEAD,
     {"период колебаний": 1, "частота колебаний": 2, "максимальная потенциальная энергия пружины": 3, "жёсткость пружины": 3, "максимальная скорость груза": 2},
     "T = 2π√(m/k) растёт, частота падает. Энергия kA²/2 не меняется, а максимальная скорость A√(k/m) уменьшается."),
    ("Длину нити математического маятника уменьшили, массу груза и угол максимального отклонения не изменили.", INCREASE_LEAD,
     {"период колебаний": 2, "частота колебаний": 1, "максимальная высота подъёма груза над положением равновесия": 2, "максимальная скорость груза": 2},
     "T = 2π√(l/g) уменьшается, частота растёт. Высота подъёма l(1 - cos α) и скорость √(2gh) уменьшаются."),
    ("Камень бросают под углом к горизонту. Начальную скорость броска увеличили, угол броска оставили прежним. Сопротивление воздуха пренебрежимо мало.", INCREASE_LEAD,
     {"время полёта камня": 1, "максимальная высота подъёма камня": 1, "дальность полёта камня": 1, "ускорение камня в полёте": 3},
     "Время, высота и дальность полёта растут вместе с начальной скоростью, ускорение всегда равно g."),
    ("Брусок скользит вниз по шероховатой наклонной плоскости. Угол наклона плоскости к горизонту увеличили.", INCREASE_LEAD,
     {"сила нормальной реакции опоры": 2, "сила трения скольжения": 2, "ускорение бруска": 1, "сила тяжести, действующая на брусок": 3},
     "N = mg cos α и Fтр = μN уменьшаются, ускорение g(sin α - μ cos α) растёт, сила тяжести не меняется."),
    ("Мяч бросили вертикально вверх. Сопротивление воздуха пренебрежимо мало.", "Как изменяются по мере подъёма мяча",
     {"кинетическая энергия мяча": 2, "потенциальная энергия мяча": 1, "полная механическая энергия мяча": 3, "модуль импульса мяча": 2, "ускорение мяча": 3},
     "Скорость при подъёме падает, высота растёт; полная энергия сохраняется, ускорение равно g."),
    ("Деревянный шарик плавает в пресной воде. Его перенесли в солёную воду, плотность которой больше; шарик по-прежнему плавает.", INCREASE_LEAD,
     {"сила Архимеда, действующая на шарик": 3, "объём погружённой части шарика": 2, "сила тяжести, действующая на шарик": 3},
     "Плавающее тело: сила Архимеда равна силе тяжести и не меняется, а погружённый объём m/ρ уменьшается."),
    ("Автомобиль проходит закругление дороги с постоянной по модулю скоростью. Скорость прохождения того же закругления увеличили.", INCREASE_LEAD,
     {"центростремительное ускорение автомобиля": 1, "кинетическая энергия автомобиля": 1, "радиус траектории автомобиля": 3, "равнодействующая сил, действующих на автомобиль": 1},
     "a = v²/R растёт, вместе с ним растёт равнодействующая ma; радиус закругления прежний."),
]

MECHANICS_FORMULAS = [
    ("Тело массой m брошено вертикально вверх с начальной скоростью v₀. Сопротивление воздуха пренебрежимо мало, ускорение свободного падения равно g.",
     [("максимальная высота подъёма", "v₀² / (2g)"), ("время подъёма до высшей точки", "v₀ / g"), ("начальная кинетическая энергия", "mv₀² / 2"), ("модуль начального импульса", "mv₀")],
     ["2v₀ / g", "v₀² / g"]),
    ("Груз массой m на пружине жёсткостью k совершает свободные колебания с амплитудой A.",
     [("период колебаний", "2π√(m / k)"), ("максимальная потенциальная энергия пружины", "kA² / 2"), ("максимальная сила упругости", "kA"), ("максимальная скорость груза", "A√(k / m)")],
     ["2π√(k / m)", "kA / 2"]),
    ("Спутник массой m движется по круговой орбите радиусом R вокруг планеты массой M. Гравитационная постоянная равна G.",
     [("скорость спутника", "√(GM / R)"), ("сила притяжения спутника к планете", "GMm / R²"), ("центростремительное ускорение спутника", "GM / R²"), ("период обращения спутника", "2π√(R³ / (GM))")],
     ["GMm / R", "√(GM / R³)"]),
    ("Брусок массой m покоится на шероховатой наклонной плоскости с углом наклона α. Ускорение свободного падения равно g.",
     [("сила нормальной реакции опоры", "mg cos α"), ("сила трения покоя", "mg sin α"), ("сила тяжести", "mg")],
     ["mg tg α", "mg / cos α"]),
    ("Тело массой m равномерно движется по окружности радиусом R со скоростью v.",
     [("центростремительное ускорение", "v² / R"), ("период обращения", "2πR / v"), ("кинетическая энергия тела", "mv² / 2"), ("равнодействующая сил, действующих на тело", "mv² / R")],
     ["v / R", "2πv / R"]),
]


def from_changes(table):
    def generator(r):
        scenario, lead, quantities, explanation = r.choice(table)
        return changes(r, scenario, lead, quantities, explanation)
    return generator


def from_formulas(table):
    def generator(r):
        scenario, pairs, extra = r.choice(table)
        return formulas(r, scenario, pairs, extra)
    return generator


mechanics_changes = from_changes(MECHANICS_CHANGES)
mechanics_changes.__name__ = "mechanics_changes"
mechanics_formulas = from_formulas(MECHANICS_FORMULAS)
mechanics_formulas.__name__ = "mechanics_formulas"


# ---------------------------------------------------------------- №7 Молекулярная физика


def m_isothermal(r):
    pressure, factor = r.randrange(40, 301, 20), r.choice([2, 3, 4, 5])
    if r.random() < 0.5:
        return task(
            f"Давление идеального газа в цилиндре под поршнем равно {pressure} кПа. Объём газа изотермически уменьшили {times(factor)}. Каким стало давление газа? Ответ дайте в кПа.",
            dec(pressure * factor), f"При постоянной температуре pV = const: {pressure} · {factor} = {pressure * factor} кПа.")
    return task(
        f"Давление идеального газа в цилиндре под поршнем равно {pressure * factor} кПа. Объём газа изотермически увеличили {times(factor)}. Каким стало давление газа? Ответ дайте в кПа.",
        dec(pressure), f"При постоянной температуре pV = const: {pressure * factor} : {factor} = {pressure} кПа.")


def m_isochoric(r):
    cold, hot, factor = r.choice([(27, 327, 2), (27, 627, 3), (-73, 127, 2), (-73, 327, 3), (127, 527, 2), (27, 177, Fraction(3, 2)), (-23, 227, 2),
                                  (-73, 27, Fraction(3, 2)), (127, 327, Fraction(3, 2)), (227, 727, 2), (27, 477, Fraction(5, 2))])
    if r.random() < 0.5:
        return task(
            f"Идеальный газ в закрытом сосуде нагрели от {cold} °C до {hot} °C. Во сколько раз увеличилось давление газа?",
            dec(factor), f"Абсолютная температура выросла с {cold + 273} К до {hot + 273} К, то есть {times(factor)}; при постоянном объёме давление выросло во столько же раз.")
    pressure = r.choice([40, 60, 80, 100, 120, 200])
    return task(
        f"Идеальный газ в закрытом сосуде при температуре {cold} °C имеет давление {pressure} кПа. Каким станет давление газа, если его нагреть до {hot} °C? Ответ дайте в кПа.",
        dec(pressure * factor), f"p₂ = p₁ · T₂ : T₁ = {pressure} · {hot + 273} : {cold + 273} = {dec(pressure * factor)} кПа.")


def m_concentration(r):
    while True:
        up, down = r.choice([2, 3, 4, 5, 6]), r.choice([2, 3, 4])
        if up != down and Fraction(up, down) > 1 and is_finite_decimal(Fraction(up, down)):
            break
    if r.random() < 0.5:
        return task(
            f"Концентрацию молекул идеального газа увеличили {times(up)}, а его абсолютную температуру уменьшили {times(down)}. Во сколько раз увеличилось давление газа?",
            dec(Fraction(up, down)), f"p = nkT: давление увеличилось {times(Fraction(up, down))}.")
    return task(
        f"Абсолютную температуру идеального газа увеличили {times(up)}, а концентрацию его молекул уменьшили {times(down)}. Во сколько раз увеличилось давление газа?",
        dec(Fraction(up, down)), f"p = nkT: давление увеличилось {times(Fraction(up, down))}.")


def m_humidity(r):
    saturated = Fraction(r.choice([12, 16, 20, 24, 32, 40]), 10)
    humidity = r.choice([25, 30, 40, 50, 60, 75, 80])
    partial = saturated * humidity / 100
    if r.random() < 0.5:
        return task(
            f"Парциальное давление водяного пара в воздухе равно {dec(partial)} кПа, давление насыщенного пара при этой температуре равно {dec(saturated)} кПа. "
            "Чему равна относительная влажность воздуха? Ответ дайте в процентах.",
            dec(humidity), f"φ = p : pн · 100% = {dec(partial)} : {dec(saturated)} · 100% = {humidity}%.")
    factor = r.choice([2, 3, 4])
    after = min(100, humidity * factor)
    return task(
        f"Относительная влажность воздуха в цилиндре под поршнем равна {humidity}%. Объём воздуха изотермически уменьшили {times(factor)}. "
        "Какой стала относительная влажность воздуха? Ответ дайте в процентах.",
        dec(after), f"Давление пара выросло бы {times(factor)}, но не может превысить давление насыщенного пара: влажность {after}%.")


def m_energy(r):
    energy, factor = Fraction(r.randint(20, 80), 10), r.choice([2, 3, Fraction(3, 2)])
    return task(
        f"Средняя кинетическая энергия поступательного движения молекул идеального газа равна {dec(energy)}·10⁻²¹ Дж. Абсолютную температуру газа увеличили {times(factor)}. "
        "Чему стала равна средняя кинетическая энергия молекул? Ответ дайте в единицах 10⁻²¹ Дж.",
        dec(energy * factor), f"E = 3kT/2, энергия пропорциональна температуре: {dec(energy)} · {dec(factor)} = {dec(energy * factor)}.")


def m_isobaric(r):
    cold, hot, factor = r.choice([(27, 327, 2), (-73, 127, 2), (27, 177, Fraction(3, 2)), (127, 527, 2), (-23, 227, 2), (27, 627, 3), (-73, 27, Fraction(3, 2))])
    volume = r.choice([2, 4, 6, 8, 10, 12])
    return task(
        f"Идеальный газ постоянной массы занимает объём {volume} л при температуре {cold} °C. Какой объём займёт этот газ при температуре {hot} °C и прежнем давлении? Ответ дайте в литрах.",
        dec(volume * factor), f"V₂ = V₁ · T₂ : T₁ = {volume} · {hot + 273} : {cold + 273} = {dec(volume * factor)} л.")


# ---------------------------------------------------------------- №8 МКТ и термодинамика


def t_first_law(r):
    heat, work = r.randrange(200, 901, 50), r.randrange(50, 601, 50)
    kind = r.choice(["energy", "outer", "heat"])
    if kind == "energy":
        return task(
            f"Идеальный газ получил количество теплоты {heat} Дж и совершил работу {work} Дж. На сколько изменилась внутренняя энергия газа? "
            "Ответ дайте в джоулях с учётом знака.",
            dec(heat - work), f"ΔU = Q - A = {heat} - {work} = {heat - work} Дж.")
    if kind == "outer":
        return task(
            f"Внешние силы совершили над идеальным газом работу {work} Дж, при этом газ отдал окружающей среде количество теплоты {heat} Дж. "
            "На сколько изменилась внутренняя энергия газа? Ответ дайте в джоулях с учётом знака.",
            dec(work - heat), f"ΔU = Aвнеш - Qотд = {work} - {heat} = {work - heat} Дж.")
    return task(
        f"Внутренняя энергия идеального газа увеличилась на {heat} Дж, при этом газ совершил работу {work} Дж. Какое количество теплоты получил газ? Ответ дайте в джоулях.",
        dec(heat + work), f"Q = ΔU + A = {heat} + {work} = {heat + work} Дж.")


def t_efficiency(r):
    efficiency = r.choice([20, 25, 30, 40, 50, 60])
    received = r.choice([200, 400, 500, 800, 1000, 2000])
    work = received * efficiency // 100
    kind = r.choice(["efficiency", "work", "cold"])
    if kind == "efficiency":
        return task(
            f"Тепловая машина за цикл получает от нагревателя количество теплоты {received} Дж и отдаёт холодильнику {received - work} Дж. Чему равен КПД машины? Ответ дайте в процентах.",
            dec(efficiency), f"η = (Q₁ - Q₂) : Q₁ = {work} : {received} = {efficiency}%.")
    if kind == "work":
        return task(
            f"КПД тепловой машины равен {efficiency}%. За цикл она получает от нагревателя количество теплоты {received} Дж. Какую работу машина совершает за цикл? Ответ дайте в джоулях.",
            dec(work), f"A = η · Q₁ = {dec(Fraction(efficiency, 100))} · {received} = {work} Дж.")
    return task(
        f"КПД тепловой машины равен {efficiency}%. За цикл она совершает работу {work} Дж. Какое количество теплоты машина отдаёт за цикл холодильнику? Ответ дайте в джоулях.",
        dec(received - work), f"Q₁ = A : η = {received} Дж, Q₂ = Q₁ - A = {received - work} Дж.")


def t_carnot(r):
    hot, cold, efficiency = r.choice([(400, 300, 25), (500, 300, 40), (600, 300, 50), (500, 400, 20), (800, 200, 75), (600, 450, 25), (1000, 400, 60),
                                      (750, 300, 60), (400, 320, 20), (500, 350, 30), (800, 480, 40), (1200, 300, 75), (1000, 300, 70), (1000, 650, 35)])
    return task(
        f"Температура нагревателя идеальной тепловой машины равна {hot} К, температура холодильника {cold} К. Чему равен КПД машины? Ответ дайте в процентах.",
        dec(efficiency), f"η = 1 - T₂ : T₁ = 1 - {cold} : {hot} = {efficiency}%.")


def t_heating(r):
    name, capacity = r.choice([("воды", 4200), ("алюминия", 900), ("железа", 460), ("меди", 380), ("свинца", 130), ("льда", 2100)])
    mass, change = r.choice([1, 2, 4, 5, 10]), r.choice([10, 20, 50, 100]) if name != "льда" else r.choice([5, 10, 20])
    heat = Fraction(capacity * mass * change, 1000)
    return task(
        f"Какое количество теплоты необходимо, чтобы нагреть {mass} кг {name} на {change} °C? Удельная теплоёмкость {name} равна {capacity} Дж/(кг·°C). Ответ дайте в килоджоулях.",
        dec(heat), f"Q = c · m · Δt = {capacity} · {mass} · {change} = {capacity * mass * change} Дж = {dec(heat)} кДж.")


def t_melting(r):
    name, fusion = r.choice([("льда", 330), ("свинца", 25), ("олова", 59), ("алюминия", 390), ("меди", 210)])
    mass = Fraction(r.choice([1, 2, 4, 5, 10, 20, 30]), 10)
    return task(
        f"Какое количество теплоты необходимо для плавления {dec(mass)} кг {name}, взятого при температуре плавления? Удельная теплота плавления {name} равна {fusion} кДж/кг. Ответ дайте в килоджоулях.",
        dec(mass * fusion), f"Q = λ · m = {fusion} · {dec(mass)} = {dec(mass * fusion)} кДж.")


def t_isobaric_work(r):
    pressure, change = r.choice([100, 150, 200, 250, 300, 400]), r.choice([2, 4, 5, 8, 10, 20])
    work = pressure * change
    if r.random() < 0.6:
        return task(
            f"Идеальный газ расширяется при постоянном давлении {pressure} кПа, его объём увеличивается на {change} л. Какую работу совершает газ? Ответ дайте в джоулях.",
            dec(work), f"A = p · ΔV = {pressure} кПа · {change} л = {work} Дж.")
    return task(
        f"Одноатомный идеальный газ при изобарном расширении совершил работу {work} Дж. На сколько увеличилась его внутренняя энергия? Ответ дайте в джоулях.",
        dec(Fraction(3 * work, 2)), f"При изобарном процессе для одноатомного газа ΔU = 3/2 · A = {dec(Fraction(3 * work, 2))} Дж.")


# ---------------------------------------------------------------- №9 МКТ и термодинамика: анализ процессов


def h_melting_graph(r):
    while True:
        start, melting = r.choice([20, 40, 60]), r.choice([80, 100, 120, 140, 160])
        heat_time, melt_time, liquid_time = r.choice([2, 3, 4]), r.choice([2, 3, 4]), r.choice([2, 3, 4])
        finish = melting + r.choice([40, 60, 80])
        solid_slope, liquid_slope = Fraction(melting - start, heat_time), Fraction(finish - melting, liquid_time)
        if solid_slope != liquid_slope and finish <= 240:
            break
    melt_start, melt_end, end = heat_time, heat_time + melt_time, heat_time + melt_time + liquid_time
    fig = Fig()
    px = figures.axes(fig, 46, 228, 28, 15, 12, 13, "t, мин", "T, °C", 1, 2, 1, 20)
    for (x1, y1), (x2, y2) in [((0, start), (melt_start, melting)), ((melt_start, melting), (melt_end, melting)), ((melt_end, melting), (end, finish))]:
        fig.line(*px(x1, y1 / 20), *px(x2, y2 / 20), 2)
    middle = dec(Fraction(2 * melt_start + melt_time, 2))
    pool = [
        [(f"Температура плавления вещества равна {melting} °C.", True), (f"Температура плавления вещества равна {finish} °C.", False)],
        [(f"Плавление вещества продолжалось {melt_time} мин.", True), (f"Плавление вещества продолжалось {melt_end} мин.", False)],
        (f"В момент времени {middle} мин часть вещества находилась в твёрдом состоянии, а часть в жидком.", True),
        [("В процессе плавления внутренняя энергия вещества не изменялась.", False), ("В процессе плавления внутренняя энергия вещества увеличивалась.", True)],
        ("Удельная теплоёмкость вещества в твёрдом состоянии больше, чем в жидком.", solid_slope < liquid_slope),
        (f"Через {end} мин после начала нагревания вещество находилось в твёрдом состоянии.", False),
        ("В начальный момент времени вещество находилось в твёрдом состоянии.", True),
        (f"В интервале времени от {melt_start} до {melt_end} мин вещество не получало теплоты.", False),
    ]
    texts, flags = pick_statements(r, pool)
    made = choose(
        "Твёрдое кристаллическое вещество нагревают в сосуде нагревателем постоянной мощности. На рисунке показан график зависимости температуры вещества от времени. "
        "Потерями теплоты можно пренебречь. Выберите все верные утверждения.",
        texts, flags,
        f"Горизонтальный участок соответствует плавлению при {melting} °C в течение {melt_time} мин. Чем круче наклон графика, тем меньше теплоёмкость.")
    made["figure"] = fig.data()
    return made


def h_isobaric(r):
    cold, factor = r.choice([200, 250, 300, 400]), r.choice([2, 3, Fraction(3, 2)])
    pool = [
        [(f"Объём газа увеличился {times(factor)}.", True), (f"Объём газа уменьшился {times(factor)}.", False)],
        ("Внутренняя энергия газа увеличилась.", True),
        ("Газ совершил положительную работу.", True),
        ("Давление газа увеличилось.", False),
        ("Концентрация молекул газа уменьшилась.", True),
        ("Средняя кинетическая энергия теплового движения молекул газа не изменилась.", False),
        [("Плотность газа уменьшилась.", True), ("Плотность газа увеличилась.", False)],
        ("Газ отдал окружающим телам некоторое количество теплоты.", False),
    ]
    texts, flags = pick_statements(r, pool)
    return choose(
        f"Идеальный газ постоянной массы изобарно нагрели от температуры {cold} К до температуры {dec(cold * factor)} К. Выберите все верные утверждения об этом процессе.",
        texts, flags, f"При постоянном давлении объём пропорционален температуре, он вырос {times(factor)}; газ получил теплоту, совершил работу, его внутренняя энергия выросла.")


def h_cycle(r):
    low, high = r.choice([(1, 2), (1, 3), (2, 3), (2, 4), (1, 4)])
    small, large = r.choice([(1, 2), (1, 3), (2, 4), (2, 6), (3, 6), (2, 5), (1, 4)])
    fig = Fig()
    px = figures.axes(fig, 46, 228, 44, 38, 7, 5, "V, л", "p, кПа", 1, 1, 1, 100)
    corners = [(small, high), (large, high), (large, low), (small, low)]
    for index in range(4):
        figures.arrow(fig, *px(*corners[index]), *px(*corners[(index + 1) % 4]), 2)
    for label, (x, y), (dx, dy) in zip("1234", corners, [(-10, -10), (10, -10), (10, 10), (-10, 10)]):
        fig.circle(*px(x, y), 3.5, 2)
        fig.text(px(x, y)[0] + dx, px(x, y)[1] + dy, label)
    work = (high - low) * 100 * (large - small)
    pool = [
        ("В процессе 1-2 газ совершает положительную работу.", True),
        ("В процессе 2-3 газ совершает положительную работу.", False),
        [(f"Работа газа за цикл равна {work} Дж.", True), (f"Работа газа за цикл равна {high * 100 * (large - small)} Дж.", False)],
        ("В процессе 2-3 внутренняя энергия газа уменьшается.", True),
        ("В процессе 4-1 газ отдаёт количество теплоты.", False),
        ("Температура газа в состоянии 2 больше, чем в остальных отмеченных состояниях.", True),
        ("Температура газа в состоянии 1 равна температуре газа в состоянии 3.", high * small == low * large),
        ("В процессе 3-4 внешние силы совершают над газом положительную работу.", True),
        ("В процессе 1-2 температура газа не изменяется.", False),
    ]
    texts, flags = pick_statements(r, pool)
    made = choose(
        "На рисунке в координатах p-V показан циклический процесс 1-2-3-4-1, совершаемый идеальным газом постоянной массы. Выберите все верные утверждения.",
        texts, flags,
        f"Работа за цикл равна площади прямоугольника: {(high - low) * 100} кПа · {large - small} л = {work} Дж. Температура пропорциональна произведению pV.")
    made["figure"] = fig.data()
    return made


# ---------------------------------------------------------------- №10 МКТ и термодинамика: изменение величин

THERMAL_CHANGES = [
    ("Идеальный газ постоянной массы в цилиндре под поршнем изотермически сжимают.", INCREASE_LEAD,
     {"давление газа": 1, "внутренняя энергия газа": 3, "концентрация молекул газа": 1, "средняя кинетическая энергия молекул газа": 3, "плотность газа": 1},
     "При постоянной температуре внутренняя энергия и энергия молекул не меняются, а давление, концентрация и плотность растут."),
    ("Идеальный газ нагревают в закрытом сосуде постоянного объёма.", INCREASE_LEAD,
     {"давление газа": 1, "плотность газа": 3, "внутренняя энергия газа": 1, "концентрация молекул газа": 3, "средняя квадратичная скорость молекул газа": 1},
     "Объём и масса постоянны, поэтому плотность и концентрация не меняются; давление, энергия и скорость молекул растут с температурой."),
    ("Идеальный газ постоянной массы изобарно охлаждают.", INCREASE_LEAD,
     {"объём газа": 2, "плотность газа": 1, "внутренняя энергия газа": 2, "давление газа": 3, "концентрация молекул газа": 1},
     "При постоянном давлении объём пропорционален температуре: объём и внутренняя энергия падают, плотность и концентрация растут."),
    ("Идеальный газ в теплоизолированном цилиндре с поршнем расширяется, совершая работу.", INCREASE_LEAD,
     {"температура газа": 2, "внутренняя энергия газа": 2, "давление газа": 2, "объём газа": 1},
     "При адиабатном расширении работа совершается за счёт внутренней энергии: температура и давление падают."),
    ("Температуру нагревателя идеальной тепловой машины увеличили, температуру холодильника оставили прежней. Количество теплоты, получаемое от нагревателя за цикл, не изменилось.",
     INCREASE_LEAD,
     {"КПД тепловой машины": 1, "работа, совершаемая машиной за цикл": 1, "количество теплоты, отдаваемое холодильнику за цикл": 2},
     "η = 1 - T₂/T₁ растёт, поэтому при том же Q₁ работа увеличивается, а отданная теплота уменьшается."),
    ("В цилиндре под поршнем находятся вода и её насыщенный пар. Объём под поршнем медленно уменьшают при постоянной температуре; в конце опыта в цилиндре по-прежнему есть и вода, и пар.",
     INCREASE_LEAD,
     {"давление пара": 3, "масса пара": 2, "масса воды": 1, "концентрация молекул пара": 3},
     "Давление и концентрация насыщенного пара зависят только от температуры; при сжатии часть пара конденсируется."),
    ("Из закрытого сосуда постоянного объёма выпустили часть идеального газа; температура газа в сосуде осталась прежней.", INCREASE_LEAD,
     {"давление газа в сосуде": 2, "плотность газа в сосуде": 2, "средняя кинетическая энергия молекул газа": 3, "концентрация молекул газа": 2, "внутренняя энергия газа в сосуде": 2},
     "Молекул стало меньше при той же температуре: давление, плотность, концентрация и внутренняя энергия уменьшились."),
    ("Воздух в закрытой комнате имеет относительную влажность 50%. Температуру воздуха в комнате повысили.", INCREASE_LEAD,
     {"давление насыщенного водяного пара": 1, "относительная влажность воздуха": 2, "плотность водяного пара в комнате": 3},
     "Масса пара и объём комнаты прежние, а давление насыщенного пара с ростом температуры растёт, поэтому относительная влажность падает."),
]

THERMAL_FORMULAS = [
    ("Одноатомный идеальный газ в количестве ν моль изобарно нагревают при давлении p; его объём увеличивается на ΔV, а температура на ΔT. Универсальная газовая постоянная равна R.",
     [("работа газа", "pΔV"), ("изменение внутренней энергии газа", "3νRΔT / 2"), ("количество теплоты, полученное газом", "5νRΔT / 2")],
     ["νRΔT / 2", "3pΔV"]),
    ("Тепловая машина за цикл получает от нагревателя количество теплоты Q₁ и отдаёт холодильнику количество теплоты Q₂.",
     [("работа машины за цикл", "Q₁ - Q₂"), ("КПД машины", "(Q₁ - Q₂) / Q₁"), ("отношение отданной теплоты к полученной", "Q₂ / Q₁")],
     ["Q₁ / Q₂", "Q₁ + Q₂"]),
]

thermal_changes = from_changes(THERMAL_CHANGES)
thermal_changes.__name__ = "thermal_changes"
thermal_formulas = from_formulas(THERMAL_FORMULAS)
thermal_formulas.__name__ = "thermal_formulas"


# ---------------------------------------------------------------- №11 Электрическое поле. Законы постоянного тока


def e_coulomb(r):
    closer, charge = r.choice([2, 3, 4]), r.choice([1, 2, 3, 4])
    force = r.randint(1, 9)
    if r.random() < 0.5:
        change = f"расстояние между ними уменьшить {times(closer)}" + ("" if charge == 1 else f", а один из зарядов увеличить {times(charge)}")
        return task(
            f"Два точечных заряда взаимодействуют с силой {force} мкН. Какой станет сила взаимодействия, если {change}? Ответ дайте в мкН.",
            dec(force * closer * closer * charge), f"F ~ q₁q₂ / r²: {force} · {closer * closer} · {charge} = {force * closer * closer * charge} мкН.")
    start = force * closer * closer
    return task(
        f"Два точечных заряда взаимодействуют с силой {start} мкН. Какой станет сила взаимодействия, если расстояние между ними увеличить {times(closer)}? Ответ дайте в мкН.",
        dec(force), f"F ~ 1 / r²: {start} : {closer * closer} = {force} мкН.")


def e_power(r):
    resistance, current = r.choice([2, 4, 5, 8, 10, 20, 25, 50]), r.choice([1, 2, 3, 4, 5, 6])
    voltage = resistance * current
    kind = r.choice(["voltage", "current", "heat"])
    if kind == "voltage":
        return task(
            f"Резистор сопротивлением {resistance} Ом подключён к источнику постоянного напряжения {voltage} В. Какая мощность выделяется на резисторе? Ответ дайте в ваттах.",
            dec(voltage * current), f"P = U² : R = {voltage}² : {resistance} = {voltage * current} Вт.")
    if kind == "current":
        return task(
            f"По резистору сопротивлением {resistance} Ом течёт ток {current} А. Какая мощность выделяется на резисторе? Ответ дайте в ваттах.",
            dec(voltage * current), f"P = I² · R = {current}² · {resistance} = {voltage * current} Вт.")
    seconds = r.choice([10, 20, 30, 60])
    return task(
        f"По резистору сопротивлением {resistance} Ом течёт ток {current} А. Какое количество теплоты выделится на резисторе за {seconds} с? Ответ дайте в джоулях.",
        dec(voltage * current * seconds), f"Q = I² · R · t = {current}² · {resistance} · {seconds} = {voltage * current * seconds} Дж.")


def e_capacitor(r):
    capacity, voltage = r.choice([2, 4, 5, 10, 20, 50]), r.choice([10, 20, 40, 50, 100, 200])
    if r.random() < 0.5:
        return task(
            f"Конденсатор ёмкостью {capacity} мкФ заряжен до напряжения {voltage} В. Чему равен заряд конденсатора? Ответ дайте в мкКл.",
            dec(capacity * voltage), f"q = C · U = {capacity} · {voltage} = {capacity * voltage} мкКл.")
    energy = Fraction(capacity * voltage * voltage, 2000)
    return task(
        f"Конденсатор ёмкостью {capacity} мкФ заряжен до напряжения {voltage} В. Чему равна энергия электрического поля конденсатора? Ответ дайте в мДж.",
        dec(energy), f"W = C · U² : 2 = {capacity}·10⁻⁶ · {voltage}² : 2 = {dec(energy)} мДж.")


def e_source(r):
    while True:
        emf, inner, outer = r.choice([6, 9, 12, 15, 18, 24]), r.choice([1, 2, Fraction(1, 2)]), r.choice([2, 3, 4, 5, 7, 8, 10, 11])
        current = Fraction(emf) / (inner + outer)
        if is_finite_decimal(current):
            break
    if r.random() < 0.5:
        return task(
            f"К источнику тока с ЭДС {emf} В и внутренним сопротивлением {dec(inner)} Ом подключён резистор сопротивлением {outer} Ом. Чему равна сила тока в цепи? Ответ дайте в амперах.",
            dec(current), f"I = ε : (R + r) = {emf} : {dec(inner + outer)} = {dec(current)} А.")
    return task(
        f"К источнику тока с ЭДС {emf} В и внутренним сопротивлением {dec(inner)} Ом подключён резистор сопротивлением {outer} Ом. Чему равно напряжение на резисторе? Ответ дайте в вольтах.",
        dec(current * outer), f"I = ε : (R + r) = {dec(current)} А, U = I · R = {dec(current * outer)} В.")


def e_field(r):
    charge, strength = r.choice([1, 2, 4, 5, 10, 20]), r.choice([2, 3, 4, 5, 6, 8, 10])
    return task(
        f"На точечный заряд {charge} мкКл в электрическом поле действует сила {charge * strength} мН. Чему равна напряжённость поля в точке, где находится заряд? Ответ дайте в кВ/м.",
        dec(strength), f"E = F : q = {charge * strength}·10⁻³ : ({charge}·10⁻⁶) = {strength}·10³ В/м.")


# ---------------------------------------------------------------- №12 Магнитное поле. Электромагнитная индукция


def b_ampere(r):
    induction, current, length = Fraction(r.choice([1, 2, 4, 5, 8, 10]), 10), r.choice([2, 4, 5, 10, 20]), Fraction(r.choice([1, 2, 4, 5, 8, 10]), 10)
    force = induction * current * length
    if r.random() < 0.6:
        return task(
            f"Прямой проводник длиной {dec(length)} м с током {current} А расположен в однородном магнитном поле с индукцией {dec(induction)} Тл перпендикулярно линиям индукции. "
            "Чему равна сила Ампера, действующая на проводник? Ответ дайте в ньютонах.",
            dec(force), f"F = B · I · l = {dec(induction)} · {current} · {dec(length)} = {dec(force)} Н.")
    return task(
        f"Прямой проводник длиной {dec(length)} м с током {current} А расположен в однородном магнитном поле с индукцией {dec(induction)} Тл под углом 30° к линиям индукции. "
        "Чему равна сила Ампера, действующая на проводник? Ответ дайте в ньютонах.",
        dec(force / 2), f"F = B · I · l · sin 30° = {dec(force)} · 0,5 = {dec(force / 2)} Н.")


def b_induction(r):
    flux, seconds = r.choice([2, 4, 6, 8, 10, 12, 20, 30]), Fraction(r.choice([1, 2, 4, 5, 10, 20]), 10)
    emf = Fraction(flux) / seconds
    if not is_finite_decimal(emf):
        return b_induction(r)
    return task(
        f"Магнитный поток через замкнутый проводящий контур равномерно изменился на {flux} мВб за {dec(seconds)} с. Чему равен модуль ЭДС индукции в контуре? Ответ дайте в мВ.",
        dec(emf), f"ε = ΔΦ : Δt = {flux} : {dec(seconds)} = {dec(emf)} мВ.")


def b_self_induction(r):
    inductance, change, seconds = r.choice([10, 20, 40, 50, 100, 200]), r.choice([1, 2, 3, 4, 5]), Fraction(r.choice([1, 2, 4, 5, 10]), 10)
    emf = Fraction(inductance * change) / seconds / 1000
    if r.random() < 0.5:
        return task(
            f"Сила тока в катушке индуктивностью {inductance} мГн равномерно изменилась на {change} А за {dec(seconds)} с. Чему равен модуль ЭДС самоиндукции? Ответ дайте в вольтах.",
            dec(emf), f"ε = L · ΔI : Δt = {dec(Fraction(inductance, 1000))} · {change} : {dec(seconds)} = {dec(emf)} В.")
    energy = Fraction(inductance * change * change, 2)
    return task(
        f"По катушке индуктивностью {inductance} мГн течёт ток {change} А. Чему равна энергия магнитного поля катушки? Ответ дайте в мДж.",
        dec(energy), f"W = L · I² : 2 = {inductance} · {change * change} : 2 = {dec(energy)} мДж.")


def b_lorentz(r):
    faster, weaker = r.choice([2, 3, 4]), r.choice([2, 3, 5])
    if r.random() < 0.5:
        return task(
            f"Заряженная частица движется по окружности в однородном магнитном поле. Во сколько раз увеличится радиус окружности, если скорость частицы увеличить {times(faster)}, "
            f"а индукцию магнитного поля уменьшить {times(weaker)}?",
            dec(faster * weaker), f"R = mv / (qB): радиус увеличится {times(faster * weaker)}.")
    return task(
        f"Заряженная частица влетает в однородное магнитное поле перпендикулярно линиям индукции. Во сколько раз увеличится сила Лоренца, если скорость частицы увеличить {times(faster)}, "
        f"а индукцию магнитного поля увеличить {times(weaker)}?",
        dec(faster * weaker), f"F = qvB: сила увеличится {times(faster * weaker)}.")


def b_flux(r):
    induction, area = Fraction(r.choice([1, 2, 4, 5, 8]), 10), r.choice([10, 20, 40, 50, 100, 200])
    flux = induction * area / 10
    return task(
        f"Плоская рамка площадью {area} см² находится в однородном магнитном поле с индукцией {dec(induction)} Тл. Плоскость рамки перпендикулярна линиям индукции. "
        "Чему равен магнитный поток через рамку? Ответ дайте в мВб.",
        dec(flux), f"Φ = B · S = {dec(induction)} · {area}·10⁻⁴ = {dec(flux)}·10⁻³ Вб.")


# ---------------------------------------------------------------- №13 Электромагнитные колебания и волны. Оптика


def o_contour(r):
    period = r.choice([2, 4, 5, 6, 8, 10, 20])
    factor, root = r.choice([(4, 2), (9, 3), (16, 4)])
    part = r.choice(["ёмкость конденсатора", "индуктивность катушки"])
    if r.random() < 0.5:
        return task(
            f"Период свободных электромагнитных колебаний в идеальном колебательном контуре равен {period} мкс. Каким станет период колебаний, если {part} увеличить {times(factor)}? Ответ дайте в мкс.",
            dec(period * root), f"T = 2π√(LC): период вырастет {times(root)} и станет равен {period * root} мкс.")
    return task(
        f"Период свободных электромагнитных колебаний в идеальном колебательном контуре равен {period * root} мкс. Каким станет период колебаний, если {part} уменьшить {times(factor)}? Ответ дайте в мкс.",
        dec(period), f"T = 2π√(LC): период уменьшится {times(root)} и станет равен {period} мкс.")


def o_mirror(r):
    angle = r.randrange(15, 80, 5)
    kind = r.choice(["reflect", "between", "turn"])
    if kind == "reflect":
        return task(
            f"Луч света падает на плоское зеркало. Угол между падающим лучом и поверхностью зеркала равен {angle}°. Чему равен угол отражения? Ответ дайте в градусах.",
            dec(90 - angle), f"Угол падения равен 90° - {angle}° = {90 - angle}°, угол отражения равен углу падения.")
    if kind == "between":
        return task(
            f"Угол падения луча света на плоское зеркало равен {angle}°. Чему равен угол между падающим и отражённым лучами? Ответ дайте в градусах.",
            dec(2 * angle), f"Угол отражения равен углу падения, угол между лучами равен 2 · {angle}° = {2 * angle}°.")
    change = r.choice([5, 10, 15])
    return task(
        f"Угол падения луча света на плоское зеркало увеличили на {change}°. На сколько градусов увеличился угол между падающим и отражённым лучами?",
        dec(2 * change), f"Угол между лучами равен удвоенному углу падения, он вырос на {2 * change}°.")


LENS = [(30, 60, 20), (60, 30, 20), (20, 20, 10), (15, 30, 10), (30, 15, 10), (40, 40, 20), (12, 24, 8), (60, 12, 10), (20, 5, 4), (24, 8, 6), (36, 18, 12), (45, 30, 18), (25, 100, 20)]


def o_lens(r):
    distance, image, focus = r.choice(LENS)
    if r.random() < 0.5:
        return task(
            f"Предмет находится на расстоянии {distance} см от тонкой собирающей линзы с фокусным расстоянием {focus} см. На каком расстоянии от линзы находится действительное изображение предмета? Ответ дайте в сантиметрах.",
            dec(image), f"1/f = 1/F - 1/d = 1/{focus} - 1/{distance}, откуда f = {image} см.")
    return task(
        f"Предмет находится на расстоянии {distance} см от тонкой собирающей линзы, его действительное изображение получилось на расстоянии {image} см от линзы. "
        "Чему равно фокусное расстояние линзы? Ответ дайте в сантиметрах.",
        dec(focus), f"1/F = 1/d + 1/f = 1/{distance} + 1/{image}, откуда F = {focus} см.")


def o_power(r):
    focus, power = r.choice([(10, 10), (20, 5), (25, 4), (40, Fraction(5, 2)), (50, 2), (8, Fraction(25, 2)), (5, 20), (4, 25), (80, Fraction(5, 4))])
    if r.random() < 0.5:
        return task(
            f"Фокусное расстояние тонкой собирающей линзы равно {focus} см. Чему равна оптическая сила линзы? Ответ дайте в диоптриях.",
            dec(power), f"D = 1 : F = 1 : {dec(Fraction(focus, 100))} = {dec(power)} дптр.")
    return task(
        f"Оптическая сила тонкой собирающей линзы равна {dec(power)} дптр. Чему равно фокусное расстояние линзы? Ответ дайте в сантиметрах.",
        dec(focus), f"F = 1 : D = {dec(Fraction(focus, 100))} м = {focus} см.")


def o_wave(r):
    frequency, length = r.choice([(100, 3), (150, 2), (75, 4), (60, 5), (50, 6), (30, 10), (20, 15), (300, 1), (600, Fraction(1, 2)), (1200, Fraction(1, 4)), (25, 12), (15, 20)])
    if r.random() < 0.5:
        return task(
            f"Радиостанция работает на частоте {frequency} МГц. Чему равна длина электромагнитной волны, излучаемой радиостанцией? Скорость света 3·10⁸ м/с. Ответ дайте в метрах.",
            dec(length), f"λ = c : ν = 3·10⁸ : ({frequency}·10⁶) = {dec(length)} м.")
    return task(
        f"Длина электромагнитной волны в вакууме равна {dec(length)} м. Чему равна частота волны? Скорость света 3·10⁸ м/с. Ответ дайте в МГц.",
        dec(frequency), f"ν = c : λ = 3·10⁸ : {dec(length)} = {frequency}·10⁶ Гц.")


def o_index(r):
    index, speed = r.choice([(Fraction(3, 2), 200000), (2, 150000), (Fraction(6, 5), 250000), (Fraction(12, 5), 125000), (Fraction(8, 5), 187500), (Fraction(5, 4), 240000)])
    if r.random() < 0.5:
        return task(
            f"Абсолютный показатель преломления прозрачной среды равен {dec(index)}. Чему равна скорость света в этой среде? Скорость света в вакууме 300 000 км/с. Ответ дайте в км/с.",
            dec(speed), f"v = c : n = 300 000 : {dec(index)} = {speed} км/с.")
    return task(
        f"Скорость света в прозрачной среде равна {speed} км/с. Чему равен абсолютный показатель преломления этой среды? Скорость света в вакууме 300 000 км/с.",
        dec(index), f"n = c : v = 300 000 : {speed} = {dec(index)}.")


def o_transformer(r):
    ratio = r.choice([2, 4, 5, 10, 20])
    secondary = r.choice([20, 50, 60, 100, 120, 200])
    voltage = ratio * r.choice([6, 11, 12, 22, 36, 55])
    return task(
        f"Первичная обмотка трансформатора содержит {secondary * ratio} витков, вторичная {secondary} витков. "
        f"На первичную обмотку подано переменное напряжение {voltage} В. Чему равно напряжение на вторичной обмотке в режиме холостого хода? Ответ дайте в вольтах.",
        dec(voltage // ratio), f"U₂ = U₁ · N₂ : N₁ = {voltage} · {secondary} : {secondary * ratio} = {voltage // ratio} В.")


# ---------------------------------------------------------------- №14 Электродинамика: анализ процессов


def c_series(r):
    while True:
        first, second = r.sample([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20], 2)
        current = r.choice([Fraction(1, 2), 1, 2, 3])
        voltage = current * (first + second)
        if voltage.denominator == 1 and voltage <= 60:
            break
    pool = [
        [(f"Сила тока в цепи равна {dec(current)} А.", True), (f"Сила тока в цепи равна {dec(Fraction(voltage, first))} А.", False)]
        if is_finite_decimal(Fraction(voltage, first)) else (f"Сила тока в цепи равна {dec(current)} А.", True),
        [(f"Напряжение на первом резисторе равно {dec(current * first)} В.", True), (f"Напряжение на первом резисторе равно {voltage} В.", False)],
        ("Мощность, выделяющаяся на первом резисторе, больше мощности, выделяющейся на втором.", first > second),
        [(f"Общая мощность, выделяющаяся в цепи, равна {dec(voltage * current)} Вт.", True), (f"Общая мощность, выделяющаяся в цепи, равна {dec(2 * voltage * current)} Вт.", False)],
        ("Сила тока в первом резисторе больше, чем во втором.", False),
        ("Если второй резистор заменить проводом с пренебрежимо малым сопротивлением, сила тока в цепи увеличится.", True),
        [(f"Общее сопротивление резисторов равно {first + second} Ом.", True), (f"Общее сопротивление резисторов равно {abs(first - second)} Ом.", False)],
        ("Напряжение на втором резисторе больше напряжения на первом.", second > first),
    ]
    texts, flags = pick_statements(r, pool)
    return choose(
        f"Два резистора сопротивлениями {first} Ом (первый) и {second} Ом (второй) соединены последовательно и подключены к источнику постоянного напряжения {voltage} В. "
        "Внутренним сопротивлением источника можно пренебречь. Выберите все верные утверждения.",
        texts, flags, f"R = {first + second} Ом, I = {voltage} : {first + second} = {dec(current)} А; напряжения и мощности пропорциональны сопротивлениям.")


LENS_CASES = [(30, 60, 20), (60, 30, 20), (15, 30, 10), (30, 15, 10), (10, -20, 20), (5, -10, 10), (12, -30, 20), (25, 100, 20), (100, 25, 20), (12, 60, 10), (60, 12, 10), (4, -20, 5), (8, -40, 10)]


def c_lens(r):
    distance, image, focus = r.choice(LENS_CASES)
    real, enlarged = image > 0, abs(image) > distance
    magnification = Fraction(abs(image), distance)
    pool = [
        [("Изображение предмета действительное.", real), ("Изображение предмета мнимое.", not real)],
        [("Изображение предмета перевёрнутое.", real), ("Изображение предмета прямое.", not real)],
        [(f"Изображение находится на расстоянии {abs(image)} см от линзы.", True), (f"Изображение находится на расстоянии {abs(image) + focus} см от линзы.", False)],
        [("Изображение предмета увеличенное.", enlarged), ("Изображение предмета уменьшенное.", not enlarged)],
        [(f"Оптическая сила линзы равна {dec(Fraction(100, focus))} дптр.", True), (f"Оптическая сила линзы равна {dec(Fraction(focus, 100))} дптр.", False)],
        [(f"Размер изображения {times(magnification)} больше размера предмета.", True), (f"Размер изображения {times(magnification + 1)} больше размера предмета.", False)]
        if enlarged and is_finite_decimal(magnification) else ("Изображение и предмет находятся по одну сторону от линзы.", not real),
        ("Изображение предмета можно получить на экране.", real),
    ]
    texts, flags = pick_statements(r, pool)
    return choose(
        f"Предмет расположен перпендикулярно главной оптической оси тонкой собирающей линзы с фокусным расстоянием {focus} см на расстоянии {distance} см от неё. Выберите все верные утверждения.",
        texts, flags,
        f"1/f = 1/{focus} - 1/{distance}, f = {image} см: изображение {'действительное, перевёрнутое' if real else 'мнимое, прямое'}, {'увеличенное' if enlarged else 'уменьшенное'}.")


def c_graph(r):
    first, second = r.choice([(2, 4), (2, 8), (2, 10), (4, 8), (4, 10), (4, 20), (5, 10), (5, 20), (2, 5)])
    fig = Fig()
    px = figures.axes(fig, 46, 228, 34, 38, 10, 5, "U, В", "I, А", 1, 1, 2, 1)
    for label, resistance in (("1", first), ("2", second)):
        end_voltage = min(20, 5 * resistance)
        fig.line(*px(0, 0), *px(end_voltage / 2, end_voltage / resistance), 2)
        fig.text(px(end_voltage / 2, end_voltage / resistance)[0] + 10, px(end_voltage / 2, end_voltage / resistance)[1] - 8, label)
    ratio = Fraction(second, first)
    voltage = r.choice([v for v in (10, 20) if (v * v) % second == 0] or [second])
    parallel = Fraction(first * second, first + second)
    pool = [
        [(f"Сопротивление резистора 1 равно {first} Ом.", True), (f"Сопротивление резистора 1 равно {dec(Fraction(1, first))} Ом.", False)],
        [(f"Сопротивление резистора 2 равно {second} Ом.", True), (f"Сопротивление резистора 2 равно {first} Ом.", False)],
        (f"Сопротивление резистора 2 больше сопротивления резистора 1 {times(ratio)}.", True),
        ("При одинаковом напряжении сила тока в резисторе 1 больше, чем в резисторе 2.", True),
        ("При одинаковой силе тока напряжение на резисторе 1 больше, чем на резисторе 2.", False),
        [(f"При последовательном соединении этих резисторов их общее сопротивление равно {first + second} Ом.", True),
         (f"При параллельном соединении этих резисторов их общее сопротивление равно {first + second} Ом.", False)],
        [(f"При напряжении {voltage} В на резисторе 2 выделяется мощность {dec(Fraction(voltage * voltage, second))} Вт.", True),
         (f"При напряжении {voltage} В на резисторе 2 выделяется мощность {dec(Fraction(voltage * voltage, first))} Вт.", False)],
        ("При параллельном соединении этих резисторов их общее сопротивление меньше сопротивления резистора 1.", parallel < first),
    ]
    texts, flags = pick_statements(r, pool)
    made = choose(
        "На рисунке показаны графики зависимости силы тока от напряжения для двух резисторов, обозначенных цифрами 1 и 2. Выберите все верные утверждения.",
        texts, flags, f"R = U : I. По графикам R₁ = {first} Ом, R₂ = {second} Ом.")
    made["figure"] = fig.data()
    return made


# ---------------------------------------------------------------- №15 Электродинамика: изменение величин

ELECTRIC_CHANGES = [
    ("Плоский воздушный конденсатор подключён к источнику постоянного напряжения. Расстояние между пластинами увеличили, не отключая конденсатор от источника.", INCREASE_LEAD,
     {"ёмкость конденсатора": 2, "заряд конденсатора": 2, "напряжение на конденсаторе": 3, "напряжённость поля между пластинами": 2, "энергия конденсатора": 2},
     "Напряжение задаёт источник. Ёмкость уменьшается, поэтому падают заряд q = CU, напряжённость U/d и энергия CU²/2."),
    ("Плоский воздушный конденсатор зарядили и отключили от источника. Затем расстояние между пластинами увеличили.", INCREASE_LEAD,
     {"ёмкость конденсатора": 2, "заряд конденсатора": 3, "напряжение на конденсаторе": 1, "напряжённость поля между пластинами": 3, "энергия конденсатора": 1},
     "Заряд сохраняется. Ёмкость уменьшается, поэтому напряжение q/C и энергия q²/(2C) растут; напряжённость зависит только от заряда и площади пластин."),
    ("К источнику тока с ЭДС ε и внутренним сопротивлением r подключён реостат. Сопротивление реостата увеличили.", INCREASE_LEAD,
     {"сила тока в цепи": 2, "напряжение на реостате": 1, "мощность, выделяющаяся на внутреннем сопротивлении источника": 2, "ЭДС источника": 3},
     "I = ε / (R + r) уменьшается, напряжение на реостате ε - Ir растёт, мощность I²r падает."),
    ("Заряженная частица влетает в однородное магнитное поле перпендикулярно линиям индукции и движется по окружности. Скорость, с которой частица влетает в поле, увеличили.", INCREASE_LEAD,
     {"радиус окружности": 1, "период обращения частицы": 3, "сила Лоренца, действующая на частицу": 1, "частота обращения частицы": 3},
     "R = mv/(qB) и F = qvB растут, а период 2πm/(qB) от скорости не зависит."),
    ("В идеальном колебательном контуре ёмкость конденсатора увеличили, индуктивность катушки оставили прежней.", INCREASE_LEAD,
     {"период свободных колебаний в контуре": 1, "частота свободных колебаний в контуре": 2, "длина волны, на которую настроен контур": 1},
     "T = 2π√(LC) растёт, частота падает, длина волны cT растёт."),
    ("Световой луч переходит из воздуха в стекло.", "Как изменяются при этом переходе",
     {"частота световой волны": 3, "скорость распространения света": 2, "длина световой волны": 2},
     "Частота при переходе не меняется, скорость c/n и длина волны уменьшаются."),
    ("Предмет расположен перед собирающей линзой на расстоянии, большем фокусного. Предмет приблизили к линзе, но он остался дальше фокуса.", INCREASE_LEAD,
     {"расстояние от линзы до изображения": 1, "размер изображения": 1, "оптическая сила линзы": 3, "фокусное расстояние линзы": 3},
     "Из формулы линзы: при уменьшении d (d > F) расстояние до изображения и его размер растут; свойства линзы не меняются."),
    ("Проволочный резистор подключён к источнику постоянного напряжения, внутренним сопротивлением которого можно пренебречь. "
     "Проволоку заменили другой, из того же материала и той же длины, но с большей площадью поперечного сечения.", INCREASE_LEAD,
     {"сопротивление резистора": 2, "сила тока в цепи": 1, "мощность, выделяющаяся на резисторе": 1, "напряжение на резисторе": 3},
     "R = ρl/S уменьшается, при том же напряжении растут ток U/R и мощность U²/R."),
    ("На дифракционную решётку нормально падает монохроматический свет. Решётку заменили другой, с меньшим периодом.", INCREASE_LEAD,
     {"угол, под которым наблюдается первый дифракционный максимум": 1, "длина волны падающего света": 3, "частота падающего света": 3},
     "d sin φ = λ: при меньшем периоде угол больше; свет остался тем же."),
]

ELECTRIC_FORMULAS = [
    ("Резистор сопротивлением R подключён к источнику тока с ЭДС ε и внутренним сопротивлением r.",
     [("сила тока в цепи", "ε / (R + r)"), ("напряжение на резисторе", "εR / (R + r)"), ("мощность, выделяющаяся на резисторе", "ε²R / (R + r)²")],
     ["ε / R", "εr / (R + r)"]),
    ("Плоский конденсатор ёмкостью C заряжен до напряжения U, расстояние между его пластинами равно d.",
     [("заряд конденсатора", "CU"), ("энергия конденсатора", "CU² / 2"), ("напряжённость поля между пластинами", "U / d")],
     ["C / U", "Ud"]),
    ("Частица массой m с зарядом q движется со скоростью v по окружности в однородном магнитном поле с индукцией B.",
     [("сила Лоренца", "qvB"), ("радиус окружности", "mv / (qB)"), ("период обращения", "2πm / (qB)")],
     ["qB / (mv)", "mv² / (qB)"]),
    ("Идеальный колебательный контур состоит из конденсатора ёмкостью C и катушки индуктивностью L. Максимальный заряд конденсатора равен q, скорость света равна c.",
     [("период свободных колебаний", "2π√(LC)"), ("максимальная энергия конденсатора", "q² / (2C)"), ("длина волны, на которую настроен контур", "2πc√(LC)")],
     ["1 / (2π√(LC))", "q² / (2L)"]),
]

electric_changes = from_changes(ELECTRIC_CHANGES)
electric_changes.__name__ = "electric_changes"
electric_formulas = from_formulas(ELECTRIC_FORMULAS)
electric_formulas.__name__ = "electric_formulas"


# ---------------------------------------------------------------- №16 Ядерная физика

ISOTOPES = [("He", 2, 4), ("Li", 3, 7), ("Be", 4, 9), ("C", 6, 12), ("C", 6, 14), ("N", 7, 14), ("O", 8, 16), ("O", 8, 18), ("Na", 11, 23), ("Al", 13, 27),
            ("P", 15, 31), ("Cl", 17, 35), ("Cl", 17, 37), ("K", 19, 39), ("Ca", 20, 40), ("Fe", 26, 56), ("Co", 27, 60), ("Cu", 29, 63), ("Ag", 47, 108),
            ("I", 53, 131), ("Au", 79, 197), ("Pb", 82, 206), ("Ra", 88, 226), ("U", 92, 235), ("U", 92, 238), ("Pu", 94, 239)]


def n_composition(r):
    symbol, charge, mass = r.choice(ISOTOPES)
    name = nuclide(mass, charge, symbol)
    kind = r.choice(["both", "neutrons", "nucleons"])
    if kind == "both":
        made = task(
            f"Сколько протонов и сколько нейтронов содержит ядро {name}? В ответе запишите число протонов и число нейтронов подряд, без пробелов и запятых.",
            f"{charge}{mass - charge}", f"Протонов {charge} (зарядовое число), нейтронов {mass} - {charge} = {mass - charge}.")
        made["kind"] = "exact"
        return made
    if kind == "neutrons":
        return task(f"Сколько нейтронов содержит ядро {name}?", dec(mass - charge), f"N = A - Z = {mass} - {charge} = {mass - charge}.")
    return task(f"Сколько электронов содержит нейтральный атом, ядро которого обозначается {name}?", dec(charge), f"В нейтральном атоме число электронов равно числу протонов: {charge}.")


def n_half_life(r):
    period, unit = r.choice([(8, "суток"), (5, "лет"), (30, "лет"), (4, "суток"), (12, "часов"), (2, "часов"), (138, "суток"), (28, "лет")])
    count = r.choice([1, 2, 3, 4])
    kind = r.choice(["percent", "mass", "decayed"])
    if kind == "percent":
        return task(
            f"Период полураспада радиоактивного изотопа равен {period} {unit}. Какая доля ядер этого изотопа останется нераспавшейся через {period * count} {unit}? Ответ дайте в процентах.",
            dec(Fraction(100, 2 ** count)), f"Число прошедших периодов полураспада: {count}. Останется 100% : 2{sup(count)} = {dec(Fraction(100, 2 ** count))}%.")
    start = 2 ** count * r.choice([1, 2, 3, 5, 10])
    if kind == "mass":
        return task(
            f"Период полураспада радиоактивного изотопа равен {period} {unit}. В образце содержится {start} мг этого изотопа. Сколько миллиграммов изотопа останется через {period * count} {unit}?",
            dec(start // 2 ** count), f"Число прошедших периодов полураспада: {count}. Останется {start} : 2{sup(count)} = {start // 2 ** count} мг.")
    return task(
        f"Период полураспада радиоактивного изотопа равен {period} {unit}. В образце содержится {start} мг этого изотопа. Сколько миллиграммов изотопа распадётся за {period * count} {unit}?",
        dec(start - start // 2 ** count), f"Останется {start} : 2{sup(count)} = {start // 2 ** count} мг, распадётся {start - start // 2 ** count} мг.")


def n_decay(r):
    symbol, charge, mass = r.choice([("U", 92, 238), ("Th", 90, 232), ("Ra", 88, 226), ("Po", 84, 210), ("Pu", 94, 239), ("U", 92, 235), ("Rn", 86, 222)])
    alphas, betas = r.randint(1, 3), r.randint(0, 2)
    what = f"несколько распадов (α-распадов: {alphas}, электронных β-распадов: {betas})"
    if r.random() < 0.5:
        return task(
            f"Ядро {nuclide(mass, charge, symbol)} испытало {what}. Чему равно зарядовое число получившегося ядра?",
            dec(charge - 2 * alphas + betas), f"Каждый α-распад уменьшает заряд на 2, каждый β-распад увеличивает на 1: {charge} - {2 * alphas} + {betas} = {charge - 2 * alphas + betas}.")
    return task(
        f"Ядро {nuclide(mass, charge, symbol)} испытало {what}. Чему равно массовое число получившегося ядра?",
        dec(mass - 4 * alphas), f"Каждый α-распад уменьшает массовое число на 4, β-распад его не меняет: {mass} - {4 * alphas} = {mass - 4 * alphas}.")


REACTIONS = [
    ([(14, 7, "N"), (4, 2, "He")], [(1, 1, "H")]), ([(9, 4, "Be"), (4, 2, "He")], [(1, 0, "n")]), ([(27, 13, "Al"), (4, 2, "He")], [(1, 0, "n")]),
    ([(7, 3, "Li"), (1, 1, "H")], [(4, 2, "He")]), ([(2, 1, "H"), (3, 1, "H")], [(1, 0, "n")]), ([(10, 5, "B"), (1, 0, "n")], [(4, 2, "He")]),
    ([(6, 3, "Li"), (1, 0, "n")], [(4, 2, "He")]), ([(27, 13, "Al"), (1, 0, "n")], [(4, 2, "He")]), ([(14, 7, "N"), (1, 0, "n")], [(1, 1, "H")]),
    ([(55, 25, "Mn"), (1, 1, "H")], [(1, 0, "n")]), ([(24, 12, "Mg"), (4, 2, "He")], [(1, 0, "n")]), ([(19, 9, "F"), (1, 1, "H")], [(4, 2, "He")]),
]


def n_reaction(r):
    left, right = r.choice(REACTIONS)
    mass = sum(a for a, _, _ in left) - sum(a for a, _, _ in right)
    charge = sum(z for _, z, _ in left) - sum(z for _, z, _ in right)
    equation = " + ".join(nuclide(*item) for item in left) + " → X + " + " + ".join(nuclide(*item) for item in right)
    if r.random() < 0.5:
        return task(f"В результате ядерной реакции {equation} образуется ядро X. Чему равно массовое число ядра X?", dec(mass),
                    f"Сумма массовых чисел сохраняется: {sum(a for a, _, _ in left)} - {sum(a for a, _, _ in right)} = {mass}.")
    return task(f"В результате ядерной реакции {equation} образуется ядро X. Чему равно зарядовое число ядра X?", dec(charge),
                f"Сумма зарядовых чисел сохраняется: {sum(z for _, z, _ in left)} - {sum(z for _, z, _ in right)} = {charge}.")


# ---------------------------------------------------------------- №17 Квантовая физика: изменение величин

PHOTO = "Металлическую пластину освещают монохроматическим светом, при этом наблюдается фотоэффект."

QUANTUM_CHANGES = [
    (f"{PHOTO} Частоту падающего света увеличили.", INCREASE_LEAD,
     {"максимальная кинетическая энергия фотоэлектронов": 1, "работа выхода электронов из металла": 3, "запирающее напряжение": 1,
      "частота, соответствующая красной границе фотоэффекта": 3, "энергия падающих фотонов": 1},
     "hν = A + Eк: энергия фотонов, энергия фотоэлектронов и запирающее напряжение растут; работа выхода и красная граница зависят только от металла."),
    (f"{PHOTO} Интенсивность падающего света увеличили, не меняя его частоты.", INCREASE_LEAD,
     {"число фотоэлектронов, вылетающих из пластины за 1 с": 1, "максимальная кинетическая энергия фотоэлектронов": 3, "сила тока насыщения": 1,
      "энергия одного падающего фотона": 3, "запирающее напряжение": 3},
     "Интенсивность определяет число фотонов и фотоэлектронов, но не их энергию."),
    (f"{PHOTO} Пластину заменили другой, из металла с большей работой выхода; свет не меняли, фотоэффект по-прежнему наблюдается.", INCREASE_LEAD,
     {"максимальная кинетическая энергия фотоэлектронов": 2, "частота, соответствующая красной границе фотоэффекта": 1, "энергия падающих фотонов": 3, "запирающее напряжение": 2},
     "Eк = hν - A уменьшается, красная граница A/h растёт, фотоны прежние."),
    ("Длину волны электромагнитного излучения в вакууме увеличили.", INCREASE_LEAD,
     {"энергия фотона": 2, "импульс фотона": 2, "частота излучения": 2, "скорость фотона": 3},
     "E = hc/λ, p = h/λ, ν = c/λ уменьшаются; скорость фотона в вакууме всегда равна c."),
    ("Ядро атома испытывает α-распад.", "Как изменяются в результате распада",
     {"массовое число ядра": 2, "заряд ядра": 2, "число нейтронов в ядре": 2},
     "α-частица уносит 2 протона и 2 нейтрона."),
    ("Ядро атома испытывает электронный β-распад.", "Как изменяются в результате распада",
     {"массовое число ядра": 3, "заряд ядра": 1, "число нейтронов в ядре": 2, "число протонов в ядре": 1},
     "При β⁻-распаде нейтрон превращается в протон: массовое число прежнее, заряд на единицу больше."),
    ("Атом водорода поглотил фотон и перешёл из основного состояния в возбуждённое.", INCREASE_LEAD,
     {"энергия атома": 1, "радиус орбиты электрона в модели Бора": 1, "заряд ядра атома": 3},
     "В возбуждённом состоянии энергия атома и радиус орбиты больше, ядро не меняется."),
    (f"{PHOTO} Длину волны падающего света уменьшили.", INCREASE_LEAD,
     {"энергия падающих фотонов": 1, "максимальная кинетическая энергия фотоэлектронов": 1, "работа выхода электронов из металла": 3, "импульс падающих фотонов": 1},
     "С уменьшением длины волны растут энергия hc/λ и импульс h/λ фотонов, а вместе с ними энергия фотоэлектронов."),
]

quantum_changes = from_changes(QUANTUM_CHANGES)
quantum_changes.__name__ = "quantum_changes"


# ---------------------------------------------------------------- №18 Физический смысл величин и законов

GENERAL_STATEMENTS = [
    ("При равномерном движении по окружности ускорение тела направлено к центру окружности.", True),
    ("Давление идеального газа при постоянной концентрации молекул прямо пропорционально его абсолютной температуре.", True),
    ("Сила тока в проводнике прямо пропорциональна напряжению на его концах, если сопротивление проводника постоянно.", True),
    ("Период свободных электромагнитных колебаний в контуре увеличивается при увеличении ёмкости конденсатора.", True),
    ("При электронном β-распаде зарядовое число ядра увеличивается на единицу.", True),
    ("Импульс замкнутой системы тел сохраняется при любых взаимодействиях тел системы между собой.", True),
    ("В процессе плавления кристаллического тела его температура не изменяется.", True),
    ("Одноимённые электрические заряды отталкиваются.", True),
    ("Сила Лоренца не совершает работы над заряженной частицей.", True),
    ("Энергия фотона прямо пропорциональна частоте излучения.", True),
    ("При переходе света из воздуха в воду его частота не изменяется.", True),
    ("Сила трения скольжения прямо пропорциональна силе нормальной реакции опоры.", True),
    ("Внутренняя энергия идеального газа постоянной массы зависит только от его температуры.", True),
    ("Звуковые волны не распространяются в вакууме.", True),
    ("Изотопы одного химического элемента различаются числом нейтронов в ядре.", True),
    ("Электромагнитные волны являются поперечными.", True),
    ("При равномерном движении по окружности ускорение тела равно нулю.", False),
    ("Сила тяжести, действующая на тело у поверхности Земли, зависит от скорости его движения.", False),
    ("При изотермическом сжатии идеального газа постоянной массы его давление уменьшается.", False),
    ("Теплота самопроизвольно переходит от холодного тела к горячему.", False),
    ("Общее сопротивление параллельно соединённых резисторов больше сопротивления каждого из них.", False),
    ("Период малых колебаний математического маятника зависит от массы груза.", False),
    ("При α-распаде массовое число ядра не изменяется.", False),
    ("Скорость света в стекле больше скорости света в вакууме.", False),
    ("Максимальная кинетическая энергия фотоэлектронов зависит от интенсивности падающего света.", False),
    ("Разноимённые электрические заряды отталкиваются.", False),
    ("Сила Архимеда, действующая на полностью погружённое тело, зависит от плотности этого тела.", False),
    ("В процессе кипения жидкости при постоянном давлении её температура повышается.", False),
    ("Линии индукции магнитного поля постоянного магнита разомкнуты: они начинаются на одном полюсе и заканчиваются на другом.", False),
    ("Звук в воздухе распространяется быстрее, чем свет.", False),
    ("Вес тела всегда равен действующей на него силе тяжести.", False),
    ("При увеличении расстояния между двумя точечными зарядами в 2 раза сила их взаимодействия уменьшается в 2 раза.", False),
    ("Ядро атома состоит из протонов и электронов.", False),
]


def general_statements(r):
    texts, flags = pick_statements(r, GENERAL_STATEMENTS)
    return choose("Выберите все верные утверждения о физических явлениях, величинах и закономерностях.", texts, flags,
                  "Верны утверждения: " + " ".join(text for text, flag in zip(texts, flags) if flag))


# ---------------------------------------------------------------- №19 Показания измерительных приборов

DEVICES = [("вольтметра", "В"), ("амперметра", "А"), ("термометра", "°C"), ("динамометра", "Н"), ("мензурки", "мл"), ("барометра", "кПа")]
SCALES = [(1, 5), (1, 10), (1, 2), (2, 4), (2, 10), (10, 5), (10, 10), (10, 2), (20, 4), (20, 10), (5, 5), (50, 5), (Fraction(1, 2), 5), (100, 5), (100, 10)]


def fixed(value, digits) -> str:
    """Число с заданным количеством знаков после запятой: fixed(1.5, 2) -> '1,50'."""
    scaled = int(Fraction(value) * 10 ** digits)
    if digits == 0:
        return str(scaled)
    text = str(scaled).rjust(digits + 1, "0")
    return f"{text[:-digits]},{text[-digits:]}"


def i_reading(r):
    device, unit = r.choice(DEVICES)
    major, parts = r.choice(SCALES)
    division = Fraction(major, parts)
    majors = 4 if parts == 10 else 5
    while True:
        ticks = r.randint(1, majors * parts - 1)
        if ticks % parts != 0:
            break
    value = division * ticks
    digits = len(dec(division).split(",")[1]) if "," in dec(division) else 0
    fig = Fig(420, 130)
    left, right, base = 30, 390, 90
    fig.line(left, base, right, base, 1)
    step = (right - left) / (majors * parts)
    for tick in range(majors * parts + 1):
        x = left + tick * step
        if tick % parts == 0:
            fig.line(x, base, x, base - 18, 1)
            fig.text(x, base + 14, dec(Fraction(major) * (tick // parts)))
        else:
            fig.line(x, base, x, base - (13 if parts % 2 == 0 and tick % parts == parts // 2 else 9), 1)
    pointer = left + ticks * step
    figures.arrow(fig, pointer, 24, pointer, base - 20, 2)
    fig.text(right + 4, base - 34, unit, "r")
    made = task(
        f"Определите показания {device} (см. рисунок), если погрешность прямого измерения равна цене деления {device}. "
        "В ответе запишите значение и погрешность слитно, без пробела: например, для (1,4 ± 0,2) нужно записать 1,40,2.",
        fixed(value, digits) + fixed(division, digits),
        f"Цена деления равна {dec(Fraction(major))} : {parts} = {dec(division)} {unit}. Показания: ({fixed(value, digits)} ± {fixed(division, digits)}) {unit}.",
        fig,
    )
    made["kind"] = "exact"
    return made


# ---------------------------------------------------------------- №20 Планирование эксперимента

EXPERIMENTS = [
    ("периода колебаний нитяного маятника", ["от длины нити", "от массы груза", "от материала груза"],
     ["Длина нити", "Масса груза", "Материал груза"], [["0,5 м", "1 м", "1,5 м"], ["100 г", "200 г", "300 г"], ["сталь", "латунь", "алюминий"]]),
    ("сопротивления проводника", ["от его длины", "от площади его поперечного сечения", "от материала проводника"],
     ["Длина", "Сечение", "Материал"], [["1 м", "2 м", "3 м"], ["0,5 мм²", "1 мм²", "2 мм²"], ["медь", "никелин", "железо"]]),
    ("силы трения скольжения", ["от массы бруска", "от материала поверхности", "от площади соприкосновения бруска с поверхностью"],
     ["Масса бруска", "Поверхность", "Площадь грани"], [["100 г", "200 г", "300 г"], ["дерево", "резина", "сталь"], ["20 см²", "40 см²", "60 см²"]]),
    ("выталкивающей силы", ["от объёма тела", "от плотности жидкости", "от материала тела"],
     ["Объём тела", "Жидкость", "Материал тела"], [["20 см³", "40 см³", "60 см³"], ["вода", "керосин", "масло"], ["сталь", "алюминий", "медь"]]),
    ("периода колебаний пружинного маятника", ["от жёсткости пружины", "от массы груза", "от амплитуды колебаний"],
     ["Жёсткость", "Масса груза", "Амплитуда"], [["40 Н/м", "80 Н/м", "120 Н/м"], ["100 г", "200 г", "400 г"], ["2 см", "4 см", "6 см"]]),
    ("ёмкости плоского конденсатора", ["от площади пластин", "от расстояния между пластинами", "от диэлектрика между пластинами"],
     ["Площадь пластин", "Расстояние", "Диэлектрик"], [["50 см²", "100 см²", "200 см²"], ["1 мм", "2 мм", "4 мм"], ["воздух", "слюда", "парафин"]]),
]


def x_setups(r):
    quantity, goals, headers, values = r.choice(EXPERIMENTS)
    studied = r.randrange(3)
    while True:
        setups = [tuple(r.randrange(3) for _ in range(3)) for _ in range(5)]
        if len(set(setups)) < 5:
            continue
        # Подходит пара установок, которые различаются только исследуемым параметром.
        good = [(i, j) for i in range(5) for j in range(i + 1, 5)
                if [k for k in range(3) if setups[i][k] != setups[j][k]] == [studied]]
        if len(good) == 1:
            break
    rows = [["№"] + headers] + [[str(index + 1)] + [values[k][setup[k]] for k in range(3)] for index, setup in enumerate(setups)]
    first, second = good[0]
    made = task(
        f"Необходимо экспериментально обнаружить зависимость {quantity} {goals[studied]}. В таблице приведены характеристики пяти установок. "
        "Какие две установки нужно использовать для такого исследования? В ответе запишите номера выбранных установок без пробелов и запятых.",
        f"{first + 1}{second + 1}",
        f"Установки должны различаться только исследуемой величиной («{headers[studied].lower()}»), остальные характеристики у них должны совпадать: это установки {first + 1} и {second + 1}.",
        table_figure(rows, cell_width=125, cell_height=36, first_width=44),
    )
    made["kind"] = "set"
    return made


NUMBERS = [
    Entry(1, "Кинематика", 1, [k_law, k_circular, k_relative, k_average, k_throw, figures.fig_velocity_graph, figures.fig_xt_graph]),
    Entry(2, "Динамика", 1, [d_resultant, d_friction, d_spring, d_gravity, d_elevator, d_second_law, figures.fig_forces]),
    Entry(3, "Законы сохранения в механике", 1, [z_inelastic, z_rebound, z_energy_height, z_power, z_kinetic_change, z_spring_energy, z_work]),
    Entry(4, "Статика. Механические колебания и волны", 1, [s_lever, s_depth, s_archimedes, s_period_scaling, s_count, s_wave]),
    Entry(5, "Механика: анализ процессов", 2, [a_throw, a_graph, a_pendulum]),
    Entry(6, "Механика: изменение величин, соответствие", 2, [mechanics_changes, mechanics_formulas, mechanics_changes]),
    Entry(7, "Молекулярная физика", 1, [m_isothermal, m_isochoric, m_concentration, m_humidity, m_energy, m_isobaric]),
    Entry(8, "МКТ и термодинамика", 1, [t_first_law, t_efficiency, t_carnot, t_heating, t_melting, t_isobaric_work, figures.fig_pv_work]),
    Entry(9, "МКТ и термодинамика: анализ процессов", 2, [h_melting_graph, h_isobaric, h_cycle]),
    Entry(10, "МКТ и термодинамика: изменение величин, соответствие", 2, [thermal_changes, thermal_changes, thermal_formulas]),
    Entry(11, "Электрическое поле. Законы постоянного тока", 1,
          [e_coulomb, e_power, e_capacitor, e_source, e_field, figures.fig_circuit_series, figures.fig_circuit_parallel, figures.fig_iu_graph]),
    Entry(12, "Магнитное поле. Электромагнитная индукция", 1, [b_ampere, b_induction, b_self_induction, b_lorentz, b_flux]),
    Entry(13, "Электромагнитные колебания и волны. Оптика", 1, [o_contour, o_mirror, o_lens, o_power, o_wave, o_index, o_transformer]),
    Entry(14, "Электродинамика: анализ процессов", 2, [c_series, c_lens, c_graph]),
    Entry(15, "Электродинамика: изменение величин, соответствие", 2, [electric_changes, electric_formulas, electric_changes]),
    Entry(16, "Ядерная физика", 1, [n_composition, n_half_life, n_decay, n_reaction]),
    Entry(17, "Квантовая физика: изменение величин", 2, [quantum_changes]),
    Entry(18, "Физический смысл величин и законов", 2, [general_statements]),
    Entry(19, "Показания измерительных приборов", 1, [i_reading]),
    Entry(20, "Планирование эксперимента", 1, [x_setups]),
]
