-- Тесты игровой логики. Запускаются через tests/run_luau_tests.py, который склеивает
-- mock_roblox.luau, модули игры (таблица M) и этот файл в один сценарий.

local Text, Scoring, Variant, Duel = M.Text, M.Scoring, M.Variant, M.Duel

local passed, failed = 0, 0

local function check(condition, message)
	if condition then
		passed += 1
	else
		failed += 1
		print("ПРОВАЛ: " .. message)
	end
end

local function equal(actual, expected, message)
	check(actual == expected, string.format("%s: ожидалось %s, получено %s", message, tostring(expected), tostring(actual)))
end

-- ---------------------------------------------------------------- Text

equal(Text.normalize(" Спустя  Рукава "), "спустярукава", "normalize убирает пробелы и регистр")
equal(Text.normalize("ЁЖ"), "еж", "normalize приравнивает ё к е")
equal(Text.normalize("−3"), "-3", "normalize заменяет типографский минус")
equal(Text.normalize("Was Written"), "waswritten", "normalize работает с латиницей")
equal(Text.upper("пребывать ёж abc"), "ПРЕБЫВАТЬ ЁЖ ABC", "upper для кириллицы и латиницы")
equal(Text.length("привет"), 6, "length считает символы, а не байты")
equal(Text.truncate("абвгдежз", 3), "абв", "truncate режет по символам")
equal(#Text.chars("аб1"), 3, "chars делит строку на символы")
equal(Text.normalize("\255\254"), "", "битая строка не роняет normalize")

-- ---------------------------------------------------------------- Scoring.grade

local function grade(kind, points, answers, given)
	return Scoring.grade({ kind = kind, points = points, answers = answers }, given)
end

equal(grade("exact", 1, { "носков" }, " НОСКОВ "), 1, "exact: регистр и пробелы не важны")
equal(grade("exact", 1, { "носков" }, "носок"), 0, "exact: неверное слово")
equal(grade("exact", 1, { "хлоропласты", "хлоропласт" }, "Хлоропласт"), 1, "exact: любой из допустимых ответов")
equal(grade("exact", 1, { "+6", "6" }, "6"), 1, "exact: степень окисления без знака")
equal(grade("exact", 1, { "-2" }, "−2"), 1, "exact: типографский минус")
equal(grade("exact", 1, { "2" }, ""), 0, "пустой ответ даёт 0")
equal(grade("exact", 1, { "2" }, nil), 0, "отсутствующий ответ даёт 0")

equal(grade("number", 1, { "0,5" }, "0.5"), 1, "number: точка вместо запятой")
equal(grade("number", 1, { "0,5" }, "0,50"), 1, "number: лишний ноль")
equal(grade("number", 1, { "-41" }, "-41"), 1, "number: отрицательное число")
equal(grade("number", 1, { "12" }, "12,0"), 1, "number: целое как дробь")
equal(grade("number", 1, { "12" }, "13"), 0, "number: неверное число")
equal(grade("number", 1, { "12" }, "abc"), 0, "number: текст вместо числа")

equal(grade("set", 2, { "135" }, "531"), 2, "set: порядок цифр не важен")
equal(grade("set", 2, { "135" }, "13"), 1, "set: одна пропущенная цифра даёт 1 балл")
equal(grade("set", 2, { "135" }, "1345"), 1, "set: одна лишняя цифра даёт 1 балл")
equal(grade("set", 2, { "135" }, "24"), 0, "set: всё неверно")
equal(grade("set", 2, { "135" }, "1"), 0, "set: две пропущенные цифры")
equal(grade("set", 1, { "135" }, "13"), 0, "set на 1 балл: частичного балла нет")

equal(grade("order", 2, { "213" }, "213"), 2, "order: точное совпадение")
equal(grade("order", 2, { "213" }, "211"), 1, "order: одна ошибка даёт 1 балл")
equal(grade("order", 2, { "213" }, "123"), 0, "order: две ошибки")
equal(grade("order", 2, { "213" }, "21"), 0, "order: не та длина")
equal(grade("order", 1, { "2413" }, "2431"), 0, "order на 1 балл: только точное совпадение")
equal(grade("order", 3, { "2413" }, "2431"), 1, "order на 3 балла: две ошибки дают 1 балл")
equal(grade("order", 3, { "2413" }, "2414"), 2, "order на 3 балла: одна ошибка даёт 2 балла")
equal(grade("set", 3, { "135" }, "13"), 2, "set на 3 балла: одна ошибка даёт 2 балла")
equal(grade("exact", 1, { "722", "272" }, "272"), 1, "exact: задание с несколькими подходящими числами")

-- ---------------------------------------------------------------- Scoring.summarize и decide

local sampleTasks = {
	{ kind = "exact", points = 1, answers = { "2" } },
	{ kind = "set", points = 2, answers = { "135" } },
	{ kind = "number", points = 1, answers = { "7" } },
}
local summary = Scoring.summarize(sampleTasks, { [1] = "2", [2] = "13" })
equal(summary.earned, 2, "summarize: баллы")
equal(summary.max, 4, "summarize: максимум")
equal(summary.correct, 1, "summarize: полностью верных")
equal(summary.partial, 1, "summarize: частично верных")
equal(summary.answered, 2, "summarize: дано ответов")
equal(summary.total, 3, "summarize: всего заданий")
equal(Scoring.percent(2, 4), 50, "percent")
equal(Scoring.percent(1, 3), 33, "percent округляет")
equal(Scoring.percent(0, 0), 0, "percent при пустом варианте")

local function decide(a, b)
	local outcome, reason = Scoring.decide(a, b)
	return outcome .. "/" .. reason
end
equal(decide({ earned = 12, max = 16, elapsed = 100 }, { earned = 8, max = 14, elapsed = 50 }), "win/score", "decide: 75% против 57%")
equal(decide({ earned = 8, max = 14, elapsed = 50 }, { earned = 12, max = 16, elapsed = 100 }), "lose/score", "decide: обратный случай")
equal(decide({ earned = 6, max = 12, elapsed = 90 }, { earned = 8, max = 16, elapsed = 100 }), "win/time", "decide: равные доли, быстрее сдал")
equal(decide({ earned = 6, max = 12, elapsed = 100 }, { earned = 8, max = 16, elapsed = 100 }), "draw/score", "decide: ничья")
equal(decide({ earned = 0, max = 12, elapsed = 100 }, { earned = 9, max = 12, elapsed = 100, left = true }), "win/walkover", "decide: соперник вышел")

-- ---------------------------------------------------------------- Variant

local pool = {}
for group = 1, 5 do
	for n = 1, 4 do
		table.insert(pool, { id = group .. "-" .. n, group = "g" .. group })
	end
end
local first = Variant.pick(pool, 12, 777)
local again = Variant.pick(pool, 12, 777)
local other = Variant.pick(pool, 12, 778)
equal(#first, 12, "Variant: нужное число заданий")
local same, seen, unique = true, {}, true
for index, task in first do
	same = same and again[index].id == task.id
	unique = unique and not seen[task.id]
	seen[task.id] = true
end
check(same, "Variant: один seed даёт один вариант")
check(unique, "Variant: задания не повторяются")
local groupsInFirstFive = {}
for index = 1, 5 do
	groupsInFirstFive[first[index].group] = true
end
local distinct = 0
for _ in groupsInFirstFive do
	distinct += 1
end
equal(distinct, 5, "Variant: первые задания из разных тем")
local differs = false
for index, task in first do
	differs = differs or other[index].id ~= task.id
end
check(differs, "Variant: другой seed даёт другой вариант")
equal(#Variant.pick(pool, 50, 1), 20, "Variant: не больше, чем есть в банке")
equal(#Variant.pick({}, 8, 1), 0, "Variant: пустой банк")
equal(#Variant.pick(pool, 0, 1), 20, "Variant: без номеров вся часть это 20 заданий")

-- Банк, разбитый по номерам ЕГЭ: номера 1-12, кроме пропущенного 7, по три задания на номер.
local numbered = {}
for number = 12, 1, -1 do
	if number ~= 7 then
		for n = 1, 3 do
			table.insert(numbered, { id = number .. "-" .. n, number = number })
		end
	end
end
local function numbersIn(variant)
	local list = {}
	for _, task in variant do
		table.insert(list, task.number)
	end
	return table.concat(list, " ")
end
equal(numbersIn(Variant.pick(numbered, 0, 5)), "1 2 3 4 5 6 8 9 10 11 12", "Variant: вся первая часть по порядку номеров")
equal(numbersIn(Variant.pick(numbered, 16, 5)), "1 2 3 4 5 6 8 9 10 11 12", "Variant: просят больше, чем есть номеров")
local short = Variant.pick(numbered, 4, 5)
equal(#short, 4, "Variant: сокращённый вариант нужной длины")
local ascending, spread = true, true
for index, task in short do
	ascending = ascending and (index == 1 or short[index - 1].number < task.number)
end
-- 11 номеров на 4 группы: границы групп после 2-го, 5-го и 8-го номера по счёту.
spread = short[1].number <= 2 and short[2].number >= 3 and short[2].number <= 5 and short[4].number >= 10
check(ascending, "Variant: в сокращённом варианте номера идут по возрастанию")
check(spread, "Variant: сокращённый вариант охватывает экзамен от начала до конца")
equal(numbersIn(Variant.pick(numbered, 4, 5)), numbersIn(short), "Variant: один seed даёт те же номера")
local variety = {}
for seed = 1, 40 do
	variety[numbersIn(Variant.pick(numbered, 4, seed))] = true
	variety[Variant.pick(numbered, 0, seed)[1].id] = true
end
local kinds = 0
for _ in variety do
	kinds += 1
end
check(kinds > 6, "Variant: разные seed дают разные номера и разные задания")
equal(table.concat(Variant.numbersOf(numbered), " "), "1 2 3 4 5 6 8 9 10 11 12", "Variant.numbersOf: номера по возрастанию")

-- Задания к одному тексту: номера 1-3 относятся к семейству "reading", номера 5-6 к семейству "story".
local withTexts = {}
for number = 1, 6 do
	for text = 1, 4 do
		for copy = 1, 2 do
			local family = if number <= 3 then "reading" elseif number >= 5 then "story" else nil
			table.insert(withTexts, { id = number .. "-" .. text .. "-" .. copy, number = number, context = if family then family .. ":" .. text else nil })
		end
	end
end
local sameText = true
for seed = 1, 60 do
	local variant = Variant.pick(withTexts, 0, seed)
	sameText = sameText and variant[1].context == variant[2].context and variant[2].context == variant[3].context
		and variant[5].context == variant[6].context and variant[4].context == nil
end
check(sameText, "Variant: задания к одному тексту попадают в вариант вместе")
local textKinds = {}
for seed = 1, 60 do
	textKinds[Variant.pick(withTexts, 0, seed)[1].context] = true
end
local textCount = 0
for _ in textKinds do
	textCount += 1
end
check(textCount >= 3, "Variant: в разных вариантах встречаются разные тексты")

-- ---------------------------------------------------------------- Duel: матч целиком

local function makeTasks(prefix, count, points)
	local tasks = {}
	for index = 1, count do
		table.insert(tasks, {
			id = prefix .. index,
			group = "g" .. (index % 4),
			text = prefix .. " вопрос " .. index,
			answers = { tostring(index) },
			points = points,
			kind = "number",
			explanation = "пояснение",
			figure = if prefix == "физ" then { w = 100, h = 80, items = { { "line", 0, 0, 10, 10, 1 } } } else nil,
		})
	end
	return tasks
end
mockTasks.russian = makeTasks("рус", 30, 1)
mockTasks.physics = makeTasks("физ", 30, 2)

local world = { newWorldTable(1), newWorldTable(2) }
local scoreboardText = ""
Duel.start(world, function(text)
	scoreboardText = text
end)
check(string.find(scoreboardText, "Пока никто не сыграл") ~= nil, "доска побед пуста в начале")
local t1 = world[1]
equal(t1.status, "Свободно", "парта свободна в начале")

local anna, boris = newPlayer("Anna"), newPlayer("Boris")

-- Правильный ответ записан в конце текста задания: "рус вопрос 7" -> "7".
local function rightAnswer(task)
	return string.match(task.text, "(%d+)$")
end

t1.prompts[1].Triggered:Fire(anna)
equal(last(anna).phase, "waiting", "первый севший ждёт соперника")
equal(t1.status, "Ждёт соперника", "табличка: ждёт соперника")
check(not t1.prompts[1].Enabled and t1.prompts[2].Enabled, "занятое место нельзя выбрать, свободное можно")

t1.seats[2]:Sit(boris.Character.humanoid)
equal(last(anna).phase, "setup", "двое за партой: настройка у первого")
equal(last(boris).phase, "setup", "двое за партой: настройка у второго")
equal(last(anna).rival.name, "Boris", "в настройке видно имя соперника")
equal(last(anna).counts.russian, 30, "в настройке есть размер банка")
equal(last(anna).counts.history, 0, "пустой предмет помечен")

act(anna, "ready", true)
equal(last(anna).me.ready, false, "без предмета нельзя стать готовым")
act(anna, "setSubject", "history")
equal(last(anna).me.subject, nil, "пустой предмет выбрать нельзя")
act(anna, "setSubject", "russian")
act(boris, "setSubject", "physics")
equal(last(boris).rival.subject, "russian", "соперник видит выбранный предмет")
act(anna, "voteTime", 10)
act(boris, "voteTime", 30)
act(anna, "voteTime", 999)
equal(last(boris).rival.time, 10, "недопустимое время отклонено")
act(anna, "voteCount", 8)
act(boris, "voteCount", 8)

act(anna, "ready", true)
equal(last(boris).rival.ready, true, "соперник видит готовность")
act(boris, "voteCount", 12)
equal(last(anna).me.ready, false, "смена настроек сбрасывает готовность")
act(boris, "voteCount", 8)
act(anna, "ready", true)
act(boris, "ready", true)

local countdown = last(anna)
equal(countdown.phase, "countdown", "оба готовы: отсчёт")
equal(countdown.lotTime, true, "время не совпало: жребий")
equal(countdown.lotCount, false, "число заданий совпало: без жребия")
check(countdown.time == 10 or countdown.time == 30, "жребий выбирает один из двух голосов")
equal(countdown.count, 8, "число заданий из голосов")

advance(5.1)
local examA, examB = last(anna), last(boris)
equal(examA.phase, "exam", "после отсчёта начинается экзамен")
equal(#examA.tasks, 8, "заданий столько, сколько выбрано")
equal(examA.tasks[1].answers, nil, "правильные ответы клиенту не отправляются")
equal(examA.tasks[1].explanation, nil, "пояснения клиенту не отправляются")
equal(examA.endsAt - examA.startedAt, countdown.time * 60, "длительность равна выбранному времени")
equal(examA.rival.subject, "physics", "виден предмет соперника")
check(string.find(examA.tasks[1].text, "рус") ~= nil, "первому игроку достался его предмет")
check(string.find(examB.tasks[1].text, "физ") ~= nil, "второму игроку достался его предмет")
equal(examA.tasks[1].figure, nil, "задание без рисунка приходит без рисунка")
check(examB.tasks[1].figure ~= nil and examB.tasks[1].figure.items[1][1] == "line", "рисунок задания доходит до игрока")
equal(t1.lamp, true, "настольная лампа горит во время экзамена")

-- Анна отвечает верно на 6 из 8, Борис на 4 из 8.
for index = 1, 6 do
	act(anna, "answer", { index = index, value = rightAnswer(examA.tasks[index]) })
end
act(anna, "answer", { index = 7, value = "не знаю" })
equal(lastRival(boris).answered, 7, "соперник видит число ответов")
act(anna, "answer", { index = 99, value = "1" })
act(anna, "answer", { index = 1.5, value = "1" })
act(anna, "answer", "мусор")
act(anna, "answer", { index = 8, value = string.rep("я", 300) })
equal(lastRival(boris).answered, 7, "некорректные ответы отброшены")
for index = 1, 4 do
	act(boris, "answer", { index = index, value = rightAnswer(examB.tasks[index]) })
end

advance(60)
check(string.find(t1.status, "Решено 7 и 4") ~= nil, "табличка показывает прогресс: " .. t1.status)
act(anna, "submit")
equal(last(anna).phase, "exam", "после сдачи первым матч продолжается")
equal(lastRival(boris).submitted, true, "соперник видит, что работа сдана")
act(anna, "answer", { index = 8, value = rightAnswer(examA.tasks[8]) })
act(boris, "submit")

local resA, resB = last(anna), last(boris)
equal(resA.phase, "results", "оба сдали: итоги")
equal(resA.outcome, "win", "6 из 8 против 4 из 8: победа")
equal(resB.outcome, "lose", "проигравший видит поражение")
equal(resA.me.correct, 6, "итоги: число верных ответов у себя")
equal(resA.rival.correct, 4, "итоги: число верных ответов у соперника")
equal(resA.me.total, 8, "итоги: всего заданий")
equal(resA.me.answered, 7, "ответ после сдачи не принят")
equal(resA.me.percent, 75, "итоги: процент")
equal(resB.me.earned, 8, "двухбалльные задания считаются по 2")
equal(resB.me.max, 16, "максимум по двухбалльным заданиям")
equal(math.floor(resA.me.elapsed), 60, "время сдачи")
equal(resA.review[7].your, "не знаю", "разбор: свой ответ")
equal(resA.review[7].correct, rightAnswer(examA.tasks[7]), "разбор: верный ответ")
equal(resA.review[1].earned, 1, "разбор: баллы за задание")
equal(#resB.review, 8, "разбор только своей работы")
check(resB.review[1].figure ~= nil, "в разборе есть рисунок задания")
equal(t1.lamp, false, "после экзамена настольная лампа гаснет")
equal(t1.celebrated, 1, "салют над местом победителя")
check(string.find(scoreboardText, "1. Anna: побед 1 из 1", 1, true) ~= nil, "доска побед: победитель: " .. scoreboardText)
check(string.find(scoreboardText, "2. Boris: побед 0 из 1", 1, true) ~= nil, "доска побед: проигравший")

-- Реванш.
act(anna, "rematch")
equal(last(boris).phase, "resultsUpdate", "соперник узнаёт о предложении реванша")
equal(last(boris).rematch.rival, true, "флаг реванша соперника")
act(boris, "rematch")
equal(last(anna).phase, "setup", "оба согласны на реванш: снова экран настройки")
equal(last(anna).me.subject, "russian", "при реванше прошлый предмет остаётся выбранным")
equal(last(anna).me.ready, false, "при реванше готовность сброшена")
act(anna, "setSubject", "physics")
equal(last(boris).rival.subject, "physics", "при реванше предмет можно выбрать заново")
act(anna, "setSubject", "russian")
act(boris, "voteTime", 10)
act(anna, "ready", true)
act(boris, "ready", true)
equal(last(anna).phase, "countdown", "после настройки начинается новый отсчёт")
equal(last(anna).lotTime, false, "голоса совпали: жребия нет")
equal(last(anna).time, 10, "время из новых голосов")
advance(3.1)
equal(last(anna).phase, "exam", "реванш начался")

-- Время вышло: работы сдаются сами.
act(boris, "answer", { index = 1, value = rightAnswer(last(boris).tasks[1]) })
advance(10 * 60 + 2)
equal(last(anna).phase, "results", "по окончании времени показаны итоги")
equal(last(anna).outcome, "lose", "0 баллов против 2: поражение")
equal(last(anna).me.elapsed, 10 * 60, "несданная работа: полное время")

-- Соперник встаёт на экране итогов.
act(boris, "leave")
equal(last(boris).phase, "none", "вставший получает пустой экран")
equal(last(anna).phase, "resultsUpdate", "оставшийся узнаёт, что соперник ушёл")
equal(last(anna).rivalPresent, false, "флаг ухода соперника")
equal(t1.seats[2].Occupant, nil, "место освобождено")
equal(t1.status, "Ждёт соперника", "табличка после ухода соперника")
act(anna, "rematch")
equal(last(anna).phase, "resultsUpdate", "реванш без соперника невозможен")
advance(1)

-- Новый соперник, одинаковый предмет: вариант общий.
local clara = newPlayer("Clara")
t1.prompts[2].Triggered:Fire(clara)
equal(last(anna).phase, "setup", "новый соперник: снова настройка")
equal(last(anna).me.subject, "russian", "прошлый предмет сохранён")
act(clara, "setSubject", "russian")
act(clara, "voteTime", 10)
act(anna, "voteTime", 10)
act(clara, "voteCount", 12)
act(anna, "voteCount", 12)
act(anna, "ready", true)
act(clara, "ready", true)
equal(last(anna).lotTime, false, "голоса совпали: жребия нет")
advance(3.1)
local sameVariant = #last(anna).tasks == 12
for index, task in last(anna).tasks do
	sameVariant = sameVariant and last(clara).tasks[index].text == task.text
end
check(sameVariant, "одинаковый предмет: одинаковый вариант у обоих")

-- Во время экзамена встать нельзя, выход соперника из игры даёт победу.
act(anna, "leave")
equal(last(anna).phase, "exam", "во время экзамена встать нельзя")
removePlayer(clara, t1.seats[2])
equal(lastRival(anna).left, true, "оставшийся видит, что соперник вышел")
equal(last(anna).phase, "exam", "оставшийся может дорешать работу")
act(anna, "answer", { index = 1, value = rightAnswer(last(anna).tasks[1]) })
act(anna, "submit")
equal(last(anna).phase, "results", "итоги после выхода соперника")
equal(last(anna).outcome, "win", "выход соперника: победа")
equal(last(anna).reason, "walkover", "причина победы: соперник вышел")
equal(last(anna).rivalPresent, false, "в итогах отмечено, что соперника нет")
equal(last(anna).me.correct, 1, "итоги считаются и при выходе соперника")

-- Вторая парта не зависит от первой; уход во время настройки.
local t2 = world[2]
local dima, eva = newPlayer("Dima"), newPlayer("Eva")
t2.prompts[1].Triggered:Fire(dima)
t2.prompts[2].Triggered:Fire(eva)
equal(last(dima).phase, "setup", "вторая парта: настройка")
equal(last(dima).tableId, 2, "вторая парта: свой номер")
t1.prompts[2].Triggered:Fire(dima)
equal(t1.seats[2].Occupant, nil, "игрок за партой не может занять второе место")
act(eva, "leave")
equal(last(dima).phase, "waiting", "соперник ушёл во время настройки: ожидание")
removePlayer(dima, t2.seats[1])
advance(1)
equal(t2.status, "Свободно", "парта освобождается, когда все ушли")

-- Тестовый соперник: только в Studio.
local fedor = newPlayer("Fedor")
t2.prompts[1].Triggered:Fire(fedor)
equal(last(fedor).canAddBot, true, "в Studio предлагается тестовый соперник")
RunService.studio = false
act(fedor, "addBot")
equal(last(fedor).phase, "waiting", "вне Studio тестовый соперник недоступен")
RunService.studio = true
act(fedor, "addBot")
equal(last(fedor).phase, "setup", "тестовый соперник садится напротив")
equal(last(fedor).rival.ready, true, "тестовый соперник сразу готов")
check(last(fedor).rival.subject ~= nil, "тестовый соперник выбрал предмет")
check(not t2.prompts[2].Enabled, "место тестового соперника занято")
act(fedor, "voteTime", 10)
act(fedor, "voteCount", 8)
equal(last(fedor).rival.time, 10, "тестовый соперник соглашается со временем")
equal(last(fedor).rival.count, 8, "тестовый соперник соглашается с числом заданий")
act(fedor, "setSubject", "russian")
act(fedor, "ready", true)
equal(last(fedor).phase, "countdown", "матч с тестовым соперником стартует")
equal(last(fedor).lotTime, false, "с тестовым соперником жребия нет")
advance(3.1)
equal(last(fedor).phase, "exam", "экзамен с тестовым соперником")
act(fedor, "answer", { index = 1, value = "1.50" })
advance(4.1)
equal(lastRival(fedor).answered, 1, "тестовый соперник отвечает на задания")
advance(8 * 4 + 5)
equal(lastRival(fedor).submitted, true, "тестовый соперник сдаёт работу")
act(fedor, "submit")
equal(last(fedor).phase, "results", "итоги матча с тестовым соперником")
equal(last(fedor).rival.total, 8, "в итогах есть работа тестового соперника")
equal(last(fedor).review[1].your, "1,50", "точка в ответе заменяется на запятую")
check(string.find(scoreboardText, "Fedor") == nil, "матчи с тестовым соперником не попадают на доску побед")
equal(last(fedor).rematch.rival, true, "тестовый соперник согласен на реванш")
act(fedor, "rematch")
equal(last(fedor).phase, "setup", "реванш с тестовым соперником ведёт к настройке")
equal(last(fedor).rival.ready, true, "тестовый соперник готов к реваншу")
act(fedor, "ready", true)
equal(last(fedor).phase, "countdown", "реванш с тестовым соперником")
advance(3.1)
act(fedor, "submit")
equal(last(fedor).phase, "results", "после сдачи тестовый соперник не заставляет ждать")
act(fedor, "leave")
equal(last(fedor).phase, "none", "игрок встал")
advance(60)
equal(t2.status, "Свободно", "тестовый соперник уходит вместе с игроком")
check(t2.prompts[2].Enabled, "место тестового соперника снова свободно")

-- Предмет, разбитый по номерам ЕГЭ: вся первая часть.
local numberedTasks = {}
for number = 1, 12 do
	for n = 1, 3 do
		table.insert(numberedTasks, {
			id = "мат" .. number .. "-" .. n,
			number = number,
			topic = "Тема " .. number,
			text = "мат вопрос " .. number,
			answers = { tostring(number) },
			points = 1,
			kind = "number",
			explanation = "пояснение",
		})
	end
end
mockTasks.math_prof = numberedTasks
t2.prompts[1].Triggered:Fire(fedor)
act(fedor, "addBot")
equal(last(fedor).fullCounts.math_prof, 12, "в настройке есть размер первой части")
equal(last(fedor).fullCounts.russian, 0, "у предмета без номеров размер первой части не указан")
act(fedor, "setSubject", "math_prof")
act(fedor, "voteTime", 90)
act(fedor, "voteCount", 20)
equal(last(fedor).me.count ~= 20, true, "старое число заданий 20 отклонено")
act(fedor, "voteCount", 0)
equal(last(fedor).rival.count, 0, "тестовый соперник соглашается на всю первую часть")
act(fedor, "ready", true)
advance(3.1)
equal(last(fedor).phase, "exam", "экзамен по всей первой части")
equal(#last(fedor).tasks, 12, "вся первая часть: по заданию на каждый номер")
local inOrder = true
for index, task in last(fedor).tasks do
	inOrder = inOrder and task.number == index and task.topic == "Тема " .. index
end
check(inOrder, "задания идут по номерам ЕГЭ и несут тему")
equal(last(fedor).tasks[1].answers, nil, "ответы не уходят клиенту")
act(fedor, "answer", { index = 3, value = "3" })
act(fedor, "submit")
equal(last(fedor).review[3].number, 3, "в разборе указан номер ЕГЭ")
equal(last(fedor).me.correct, 1, "верный ответ по номеру засчитан")
act(fedor, "leave")
advance(60)

-- ---------------------------------------------------------------- вторая часть и взаимная проверка

-- Предмет с тремя номерами первой части и тремя номерами второй: №4 расчётная задача, №5 и №6 развёрнутые ответы.
local partTasks = {}
for number = 1, 3 do
	table.insert(partTasks, { id = "о" .. number, number = number, text = "общ вопрос " .. number, answers = { tostring(number) }, points = 1, kind = "number", explanation = "п" })
end
table.insert(partTasks, { id = "о4", number = 4, part = 2, text = "задача 4", answers = { "4" }, points = 3, kind = "number", explanation = "решение" })
table.insert(partTasks, { id = "о5", number = 5, part = 2, text = "вопрос 5", answers = { "см. эталон" }, points = 3, kind = "essay", explanation = "эталон 5",
	criteria = { "3 балла: всё верно", "0 баллов: неверно" } })
table.insert(partTasks, { id = "о6", number = 6, part = 2, text = "вопрос 6", answers = { "см. эталон" }, points = 4, kind = "essay", explanation = "эталон 6",
	criteria = { "4 балла: всё верно" } })
mockTasks.social = partTasks

equal(#Variant.pick(partTasks, 0, 3), 3, "Variant: без второй части в варианте только первая")
equal(#Variant.pick(partTasks, 0, 3, true), 6, "Variant: вторая часть добавляется в конец")
equal(Variant.pick(partTasks, 2, 3, true)[3].number, 4, "Variant: после сокращённой первой части идёт вся вторая")
equal(#Variant.numbersOf(partTasks), 3, "Variant.numbersOf считает только первую часть")
equal(#Variant.partTwoNumbersOf(partTasks), 3, "Variant.partTwoNumbersOf считает вторую часть")

local essaySummary = Scoring.summarize(partTasks, { [4] = "4", [5] = "текст", [6] = "текст" }, { [5] = 2, [6] = false })
equal(essaySummary.earned, 5, "summarize: балл за расчётную задачу и оценка соперника")
equal(essaySummary.max, 9, "summarize: задание, которое не удалось показать, в максимум не входит")
equal(essaySummary.void[6], true, "summarize: такое задание помечено")
equal(Scoring.summarize(partTasks, { [5] = "текст" }, { [5] = 99 }).earned, 3, "summarize: оценка не больше максимума за задание")
equal(Scoring.grade(partTasks[5], "текст"), 0, "grade: развёрнутый ответ сам не оценивается")

local gena, hanna = newPlayer("Gena"), newPlayer("Hanna")
t2.prompts[1].Triggered:Fire(gena)
t2.prompts[2].Triggered:Fire(hanna)
equal(last(gena).partTwoCounts.social, 3, "в настройке есть размер второй части")
equal(last(gena).partTwoCounts.russian, 0, "у предмета без второй части он нулевой")
equal(last(gena).me.part, false, "по умолчанию вторая часть выключена")
for _, player in { gena, hanna } do
	act(player, "setSubject", "social")
	act(player, "voteCount", 0)
	act(player, "voteTime", 180)
end
act(gena, "votePart", "да")
equal(last(gena).me.part, false, "голос за вторую часть должен быть логическим")
act(gena, "votePart", true)
equal(last(hanna).rival.part, true, "соперник видит голос за вторую часть")
act(hanna, "votePart", true)
act(gena, "ready", true)
act(hanna, "ready", true)
equal(last(gena).part, true, "в отсчёте указано, что вторая часть включена")
equal(last(gena).lotPart, false, "голоса за вторую часть совпали: без жребия")
equal(last(gena).time, 180, "время 180 минут доступно")
advance(3.1)
equal(#last(gena).tasks, 6, "с второй частью в варианте шесть заданий")
equal(last(gena).tasks[5].essay, true, "развёрнутое задание помечено")
equal(last(gena).tasks[4].essay, nil, "расчётная задача второй части остаётся с кратким ответом")
equal(last(gena).tasks[4].part, 2, "у задания второй части указана часть")
equal(last(gena).tasks[5].criteria, nil, "критерии до сдачи не отправляются")

act(gena, "answer", { index = 4, value = "4" })
act(gena, "answer", { index = 5, value = "Мой ответ. Написано плохо, но по делу.\nВторая строка" })
act(gena, "answer", { index = 5, value = string.rep("я", 20000) })
act(hanna, "answer", { index = 5, value = "Ответ Ханны" })
act(hanna, "answer", { index = 6, value = "Второй ответ" })
equal(lastRival(hanna).answered, 2, "развёрнутый ответ считается данным ответом")
act(gena, "grade", { index = 5, score = 3 })
act(gena, "submit")
equal(last(gena).phase, "exam", "пока соперник не сдал, проверка не начинается")
act(hanna, "submit")
equal(last(gena).phase, "review", "после сдачи начинается взаимная проверка")
equal(t2.status, "Проверяют работы друг друга", "табличка: идёт проверка")
equal(#last(gena).items, 2, "Гена проверяет два ответа соперника")
equal(#last(hanna).items, 1, "Ханна проверяет один ответ: пустой не показывается")
equal(last(hanna).items[1].answer, "Мой ответ. Написано #####, но по делу.\nВторая строка", "текст проходит фильтр, точки и переносы сохраняются")
equal(last(hanna).items[1].solution, "эталон 5", "проверяющий видит эталон")
equal(#last(hanna).items[1].criteria, 2, "проверяющий видит критерии")
equal(last(gena).items[2].points, 4, "проверяющий видит максимальный балл")
equal(last(gena).waitingForMe, 1, "игрок знает, сколько его ответов проверяют")
equal(last(gena).endsAt - Workspace:GetServerTimeNow(), 240, "время на проверку зависит от числа работ")
act(gena, "leave")
equal(last(gena).phase, "review", "во время проверки встать нельзя")

act(hanna, "grade", { index = 6, score = 1 })
act(hanna, "grade", { index = 5, score = 9 })
act(hanna, "reviewDone")
equal(last(hanna).done, false, "нельзя закончить проверку, не поставив все оценки")
act(hanna, "grade", { index = 5, score = 2 })
act(gena, "grade", { index = 5, score = 3 })
act(gena, "grade", { index = 6, score = 1 })
act(hanna, "reviewDone")
equal(last(hanna).phase, "review", "проверка идёт, пока не закончат оба")
equal(last(gena).rivalDone, true, "игрок видит, что соперник закончил проверку")
act(hanna, "grade", { index = 5, score = 0 })
act(gena, "reviewDone")
equal(last(gena).phase, "results", "оба закончили проверку: итоги")
equal(last(gena).me.earned, 5, "баллы: расчётная задача и оценка соперника")
equal(last(gena).me.max, 13, "максимум с учётом второй части")
equal(last(gena).review[5].earned, 2, "оценку после завершения проверки изменить нельзя")
equal(last(gena).review[5].essay, true, "в разборе отмечен развёрнутый ответ")
equal(#last(gena).review[5].criteria, 2, "в разборе есть критерии")
equal(last(gena).review[6].earned, 0, "пустой развёрнутый ответ даёт 0")
equal(last(hanna).me.earned, 4, "баллы соперника: две оценки")
equal(last(hanna).outcome, "lose", "победитель определяется с учётом второй части")

-- Проверяющий не успел: автор получает полный балл.
act(gena, "rematch")
act(hanna, "rematch")
act(gena, "ready", true)
act(hanna, "ready", true)
advance(3.1)
act(gena, "answer", { index = 5, value = "Ещё один ответ" })
act(gena, "submit")
act(hanna, "submit")
equal(last(hanna).phase, "review", "реванш: снова проверка")
equal(last(gena).done, true, "тому, кому нечего проверять, остаётся ждать")
advance(M.Settings.reviewSeconds(1) + 2)
equal(last(gena).phase, "results", "время проверки вышло: итоги")
equal(last(gena).review[5].earned, 3, "ответ без оценки засчитан полностью")

-- Фильтр недоступен: ответ никому не показывается и в счёт не идёт.
TextService.fail = true
act(gena, "rematch")
act(hanna, "rematch")
act(gena, "ready", true)
act(hanna, "ready", true)
advance(3.1)
act(gena, "answer", { index = 5, value = "Ответ, который не пройдёт фильтр" })
act(gena, "submit")
act(hanna, "submit")
equal(last(gena).phase, "results", "если показывать нечего, проверки нет")
equal(last(gena).review[5].void, true, "ответ, не прошедший фильтр, помечен")
equal(last(gena).me.max, 10, "такое задание не входит в максимум")
TextService.fail = false

-- Соперник выходит во время проверки.
act(gena, "rematch")
act(hanna, "rematch")
act(gena, "ready", true)
act(hanna, "ready", true)
advance(3.1)
act(gena, "answer", { index = 5, value = "Ответ перед уходом соперника" })
act(hanna, "answer", { index = 5, value = "Ответ Ханны" })
act(gena, "submit")
act(hanna, "submit")
removePlayer(hanna, t2.seats[2])
equal(last(gena).phase, "results", "соперник вышел во время проверки: итоги")
equal(last(gena).outcome, "win", "вышедший во время проверки проигрывает")
equal(last(gena).review[5].earned, 3, "непроверенный ответ оставшегося засчитан")
act(gena, "leave")
advance(1)

-- Тестовый соперник пишет развёрнутые ответы и сам ставит оценки.
local ivan = newPlayer("Ivan")
mockTasks.russian, mockTasks.physics, mockTasks.math_prof = nil, nil, nil
t2.prompts[1].Triggered:Fire(ivan)
act(ivan, "addBot")
act(ivan, "setSubject", "social")
act(ivan, "voteCount", 0)
act(ivan, "votePart", true)
equal(last(ivan).rival.part, true, "тестовый соперник соглашается на вторую часть")
act(ivan, "ready", true)
advance(3.1)
act(ivan, "answer", { index = 5, value = "Ответ для тестового соперника" })
advance(4 * 6 + 1)
act(ivan, "submit")
equal(last(ivan).phase, "review", "с тестовым соперником тоже есть проверка")
equal(#last(ivan).items, 2, "тестовый соперник написал оба развёрнутых ответа")
equal(last(ivan).rivalDone, true, "тестовый соперник проверяет сразу")
for _, item in last(ivan).items do
	act(ivan, "grade", { index = item.index, score = item.points })
end
act(ivan, "reviewDone")
equal(last(ivan).phase, "results", "итоги после проверки тестового соперника")
equal(last(ivan).review[5].earned, 2, "тестовый соперник ставит половину баллов")
equal(last(ivan).rival.earned >= 7, true, "оценки игрока вошли в баллы тестового соперника")
act(ivan, "leave")
advance(60)

-- Калькулятор из справочных материалов.
local function calc(keys)
	local press = M.Calculator.new()
	local shown = "0"
	for _, key in keys do
		shown = press(key)
	end
	return shown
end
equal(calc({ "2", "+", "3", "=" }), "5", "калькулятор: сложение")
equal(calc({ "2", "+", "3", "×", "4", "=" }), "20", "калькулятор: действия выполняются по порядку ввода")
equal(calc({ "7", "-", "1", "0", "=" }), "-3", "калькулятор: отрицательный результат")
equal(calc({ "1", ",", "5", "×", "4", "=" }), "6", "калькулятор: дробь через запятую")
equal(calc({ "1", "÷", "4", "=" }), "0,25", "калькулятор: результат с запятой")
equal(calc({ "1", "÷", "0", "=" }), "ошибка", "калькулятор: деление на ноль")
equal(calc({ "1", "÷", "0", "=", "5" }), "ошибка", "калькулятор: после ошибки нужен сброс")
equal(calc({ "1", "÷", "0", "=", "C", "5" }), "5", "калькулятор: сброс")
equal(calc({ "1", "4", "4", "√" }), "12", "калькулятор: корень")
equal(calc({ "9", "±", "√" }), "ошибка", "калькулятор: корень из отрицательного")
equal(calc({ "1", "2", "3", "←" }), "12", "калькулятор: стирание цифры")
equal(calc({ "5", "+", "×", "3", "=" }), "15", "калькулятор: замена действия")
equal(calc({ "2", "×", "3", "=", "+", "1", "=" }), "7", "калькулятор: продолжение после результата")
equal(calc({ ",", "5", "+", ",", "5", "=" }), "1", "калькулятор: число начинается с запятой")
equal(M.Calculator.format(1 / 3), "0,3333333333", "калькулятор: не больше 10 значащих цифр")

-- Проверка заданий при загрузке банка.
local goodFigure = { w = 420, h = 260, items = { { "line", 0, 0, 10, 10, 1 }, { "text", 5, 5, "А", "c" }, { "circle", 5, 5, 3, 2 } } }
local cleaned = M.RealBank.sanitize({
	{ text = "Вопрос", answers = { "1" }, points = 2, kind = "set", explanation = "п", figure = goodFigure, number = 3, topic = "Тема", context = "reading:1" },
	{ text = "Вопрос 2", answers = { "1" }, figure = { w = 10, h = 10, items = { { "line", 0, 0, "x", 10, 1 } } } },
	{ text = "Вопрос 3", answers = { "1" }, figure = { w = 10, h = 10, items = { { "bomb", 1, 2 } } } },
	{ text = "", answers = { "1" } },
	{ text = "Без ответа", answers = {} },
	"мусор",
})
equal(#cleaned, 3, "банк отбрасывает задания без текста и без ответа")
equal(#cleaned[1].figure.items, 3, "корректный рисунок сохраняется")
equal(cleaned[1].points, 2, "баллы задания сохраняются")
equal(cleaned[1].number, 3, "номер ЕГЭ сохраняется")
equal(cleaned[1].context, "reading:1", "общий текст задания сохраняется")
equal(cleaned[2].number, nil, "у задания без номера номера нет")
equal(cleaned[2].figure, nil, "рисунок с нечисловой координатой отбрасывается")
equal(cleaned[3].figure, nil, "рисунок с неизвестной фигурой отбрасывается")
equal(cleaned[2].kind, "exact", "вид проверки по умолчанию")

print(string.format("Тестов пройдено: %d, провалено: %d", passed, failed))
if failed > 0 then
	error("есть проваленные тесты")
end
