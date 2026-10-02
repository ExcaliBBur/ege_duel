-- Проверка ответов и подсчёт баллов. Модуль не использует API Roblox, поэтому его можно тестировать отдельно.
local Text = require(script.Parent.Text)

local Scoring = {}

local function toNumber(s: string): number?
	return tonumber((string.gsub(s, ",", ".")))
end

local function gradeSet(given: string, expected: string, points: number): number
	local givenSet, expectedSet = {}, {}
	for _, ch in Text.chars(given) do
		givenSet[ch] = true
	end
	for _, ch in Text.chars(expected) do
		expectedSet[ch] = true
	end
	local missing, extra = 0, 0
	for ch in expectedSet do
		if not givenSet[ch] then
			missing += 1
		end
	end
	for ch in givenSet do
		if not expectedSet[ch] then
			extra += 1
		end
	end
	local errors = math.max(missing, extra)
	if errors == 0 then
		return points
	elseif points >= 2 then
		-- Как в ЕГЭ: каждая ошибка снимает один балл.
		return math.max(0, points - errors)
	end
	return 0
end

local function gradeOrder(given: string, expected: string, points: number): number
	if given == expected then
		return points
	end
	if points < 2 then
		return 0
	end
	local a, b = Text.chars(given), Text.chars(expected)
	if #a ~= #b then
		return 0
	end
	local mismatches = 0
	for index = 1, #a do
		if a[index] ~= b[index] then
			mismatches += 1
		end
	end
	return math.max(0, points - mismatches)
end

-- Сколько баллов даёт ответ rawAnswer на задание task.
-- Виды заданий: exact (точное совпадение), number (число), set (цифры в любом порядке), order (последовательность).
function Scoring.grade(task, rawAnswer: string?): number
	local given = Text.normalize(rawAnswer or "")
	if given == "" then
		return 0
	end
	local kind = task.kind or "exact"
	local points = task.points or 1
	local best = 0
	for _, accepted in task.answers do
		local expected = Text.normalize(accepted)
		local earned = 0
		if kind == "number" then
			local x, y = toNumber(given), toNumber(expected)
			if x and y then
				if math.abs(x - y) < 1e-9 then
					earned = points
				end
			elseif given == expected then
				earned = points
			end
		elseif kind == "set" then
			earned = gradeSet(given, expected, points)
		elseif kind == "order" then
			earned = gradeOrder(given, expected, points)
		elseif given == expected then
			earned = points
		end
		best = math.max(best, earned)
	end
	return best
end

-- Итог по работе: баллы, число верных и частично верных ответов.
function Scoring.summarize(tasks, answers)
	local summary = {
		earned = 0,
		max = 0,
		correct = 0,
		partial = 0,
		answered = 0,
		total = #tasks,
		perTask = {},
	}
	for index, task in tasks do
		local points = task.points or 1
		local answer = answers[index]
		local earned = Scoring.grade(task, answer)
		summary.max += points
		summary.earned += earned
		summary.perTask[index] = earned
		if answer ~= nil and Text.normalize(answer) ~= "" then
			summary.answered += 1
		end
		if earned == points then
			summary.correct += 1
		elseif earned > 0 then
			summary.partial += 1
		end
	end
	return summary
end

function Scoring.percent(earned: number, max: number): number
	if max <= 0 then
		return 0
	end
	return math.floor(earned / max * 100 + 0.5)
end

-- Исход матча для игрока a против игрока b.
-- Поля: earned, max, elapsed (секунд до сдачи работы), left (вышел из игры во время матча).
-- Возвращает "win" | "lose" | "draw" и причину "score" | "time" | "walkover".
function Scoring.decide(a, b): (string, string)
	if b.left and not a.left then
		return "win", "walkover"
	elseif a.left and not b.left then
		return "lose", "walkover"
	end
	-- Сравниваем доли earned/max без деления, чтобы не зависеть от округления.
	local left, right = a.earned * b.max, b.earned * a.max
	if left > right then
		return "win", "score"
	elseif left < right then
		return "lose", "score"
	end
	if a.elapsed < b.elapsed then
		return "win", "time"
	elseif a.elapsed > b.elapsed then
		return "lose", "time"
	end
	return "draw", "score"
end

return Scoring
