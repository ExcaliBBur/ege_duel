"""Предметы, банк которых разбит по номерам заданий ЕГЭ.

EXAMS: предмет -> список номеров первой части (Entry). Вариант в игре собирается по этим номерам.
PART_ONE: сколько номеров в первой части экзамена 2026 года.
SKIPPED: номера первой части, которые нельзя перенести в игру, и причина.
"""

import exam_biology
import exam_chemistry
import exam_english
import exam_geography
import exam_history
import exam_informatics
import exam_literature
import exam_math_base
import exam_math_prof
import exam_physics
import exam_russian
import exam_social

EXAMS = {
    "russian": exam_russian.NUMBERS,
    "math_base": exam_math_base.NUMBERS,
    "math_prof": exam_math_prof.NUMBERS,
    "physics": exam_physics.NUMBERS,
    "informatics": exam_informatics.NUMBERS,
    "social": exam_social.NUMBERS,
    "history": exam_history.NUMBERS,
    "chemistry": exam_chemistry.NUMBERS,
    "biology": exam_biology.NUMBERS,
    "geography": exam_geography.NUMBERS,
    "literature": exam_literature.NUMBERS,
    "english": exam_english.NUMBERS,
}

# Сколько разных заданий должно набираться на каждый номер. В предметах с вычисляемыми заданиями это 20,
# а там, где задания привязаны к авторским текстам, их меньше.
MINIMUM = {"russian": 4, "social": 12, "biology": 12, "geography": 6, "literature": 10, "english": 3}
DEFAULT_MINIMUM = 20

# Сколько заданий в первой части (с кратким ответом) у каждого предмета.
PART_ONE = {
    "russian": 26, "math_base": 21, "math_prof": 12, "physics": 20, "chemistry": 28, "biology": 21,
    "informatics": 27, "history": 12, "social": 16, "geography": 22, "literature": 8, "english": 36,
}

SKIPPED = {
    "informatics": {3: "нужен файл базы данных", 9: "нужен файл электронной таблицы", 17: "нужен файл с числами",
                    18: "нужен файл с таблицей", 22: "нужен файл", 24: "нужен файл со строкой",
                    25: "нужна программа", 26: "нужен файл", 27: "нужны файлы и программа"},
    "history": {8: "нужны фотографии и плакаты", 9: "нужна историческая карта", 10: "нужна историческая карта",
                11: "нужна историческая карта", 12: "нужна историческая карта"},
    "english": {number: "аудирование, нужна звукозапись" for number in range(1, 10)},
    "literature": {4: "развёрнутый ответ"},
}
