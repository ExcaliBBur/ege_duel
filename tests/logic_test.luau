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
equal(last(anna).phase, "countdown", "оба согласны: новый отсчёт")
equal(last(anna).lotTime, false, "при реванше жребия нет")
equal(last(anna).time, countdown.time, "при реванше те же настройки")
advance(3.1)
equal(last(anna).phase, "exam", "реванш начался")

-- Время вышло: работы сдаются сами.
act(boris, "answer", { index = 1, value = rightAnswer(last(boris).tasks[1]) })
advance(countdown.time * 60 + 2)
equal(last(anna).phase, "results", "по окончании времени показаны итоги")
equal(last(anna).outcome, "lose", "0 баллов против 2: поражение")
equal(last(anna).me.elapsed, countdown.time * 60, "несданная работа: полное время")

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
equal(last(fedor).phase, "countdown", "реванш с тестовым соперником")
advance(3.1)
act(fedor, "submit")
equal(last(fedor).phase, "results", "после сдачи тестовый соперник не заставляет ждать")
act(fedor, "leave")
equal(last(fedor).phase, "none", "игрок встал")
advance(60)
equal(t2.status, "Свободно", "тестовый соперник уходит вместе с игроком")
check(t2.prompts[2].Enabled, "место тестового соперника снова свободно")

-- Проверка заданий при загрузке банка.
local goodFigure = { w = 420, h = 260, items = { { "line", 0, 0, 10, 10, 1 }, { "text", 5, 5, "А", "c" }, { "circle", 5, 5, 3, 2 } } }
local cleaned = M.RealBank.sanitize({
	{ text = "Вопрос", answers = { "1" }, points = 2, kind = "set", explanation = "п", figure = goodFigure },
	{ text = "Вопрос 2", answers = { "1" }, figure = { w = 10, h = 10, items = { { "line", 0, 0, "x", 10, 1 } } } },
	{ text = "Вопрос 3", answers = { "1" }, figure = { w = 10, h = 10, items = { { "bomb", 1, 2 } } } },
	{ text = "", answers = { "1" } },
	{ text = "Без ответа", answers = {} },
	"мусор",
})
equal(#cleaned, 3, "банк отбрасывает задания без текста и без ответа")
equal(#cleaned[1].figure.items, 3, "корректный рисунок сохраняется")
equal(cleaned[1].points, 2, "баллы задания сохраняются")
equal(cleaned[2].figure, nil, "рисунок с нечисловой координатой отбрасывается")
equal(cleaned[3].figure, nil, "рисунок с неизвестной фигурой отбрасывается")
equal(cleaned[2].kind, "exact", "вид проверки по умолчанию")

print(string.format("Тестов пройдено: %d, провалено: %d", passed, failed))
if failed > 0 then
	error("есть проваленные тесты")
end
