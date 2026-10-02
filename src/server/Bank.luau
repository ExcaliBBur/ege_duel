-- Банк заданий. Сначала берётся копия, встроенная в игру (ServerStorage.Bank),
-- затем, если задан Config.bankBaseUrl, предметы обновляются свежими файлами из интернета.
local HttpService = game:GetService("HttpService")
local ServerStorage = game:GetService("ServerStorage")

local Shared = game:GetService("ReplicatedStorage"):WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Config = require(script.Parent.Config)

local Bank = {}

local tasksBySubject: { [string]: { any } } = {}

local VALID_KINDS = { exact = true, number = true, set = true, order = true, essay = true }
local MAX_POINTS = 25 -- сочинение по русскому языку оценивается в 22 балла
local MAX_CRITERIA = 12

local FIGURE_FIELDS = { line = 6, rect = 6, circle = 5, text = 5 } -- вид фигуры и число полей
local FIGURE_MAX_ITEMS = 240

-- Рисунок к заданию: размеры и список простых фигур. Некорректный рисунок отбрасывается целиком.
local function sanitizeFigure(raw: any): any
	if type(raw) ~= "table" or type(raw.w) ~= "number" or type(raw.h) ~= "number" or type(raw.items) ~= "table" then
		return nil
	end
	if #raw.items == 0 or #raw.items > FIGURE_MAX_ITEMS then
		return nil
	end
	local items = {}
	for _, shape in raw.items do
		if type(shape) ~= "table" or FIGURE_FIELDS[shape[1]] ~= #shape then
			return nil
		end
		-- Все поля, кроме вида фигуры и текста подписи, должны быть числами.
		for index = 2, #shape do
			local isLabel = shape[1] == "text" and index >= 4
			if type(shape[index]) ~= (if isLabel then "string" else "number") then
				return nil
			end
		end
		table.insert(items, table.clone(shape))
	end
	return { w = math.clamp(raw.w, 50, 800), h = math.clamp(raw.h, 50, 600), items = items }
end

-- Критерии оценивания развёрнутого ответа: список строк.
local function sanitizeCriteria(raw: any): { string }?
	if type(raw) ~= "table" then
		return nil
	end
	local criteria = {}
	for _, line in raw do
		if type(line) == "string" and line ~= "" and #criteria < MAX_CRITERIA then
			table.insert(criteria, line)
		end
	end
	return if #criteria > 0 then criteria else nil
end

-- Оставляет только корректные задания, чтобы битый файл из интернета не сломал матч.
local function sanitize(rawTasks: any): { any }
	local result = {}
	if type(rawTasks) ~= "table" then
		return result
	end
	for _, raw in rawTasks do
		if type(raw) == "table" and type(raw.text) == "string" and raw.text ~= "" and type(raw.answers) == "table" then
			local answers = {}
			for _, answer in raw.answers do
				if type(answer) == "string" and answer ~= "" then
					table.insert(answers, answer)
				end
			end
			local points = if type(raw.points) == "number" and raw.points % 1 == 0 and raw.points >= 1 and raw.points <= MAX_POINTS
				then raw.points
				else 1
			local kind = if VALID_KINDS[raw.kind] then raw.kind else "exact"
			local criteria = sanitizeCriteria(raw.criteria)
			-- Развёрнутый ответ без критериев сопернику оценить нечем, такое задание отбрасывается.
			if #answers > 0 and (kind ~= "essay" or criteria) then
				table.insert(result, {
					id = tostring(raw.id or #result + 1),
					group = if type(raw.group) == "string" then raw.group else nil,
					text = raw.text,
					answers = answers,
					points = points,
					kind = kind,
					explanation = if type(raw.explanation) == "string" then raw.explanation else "",
					figure = sanitizeFigure(raw.figure),
					-- Номер задания в ЕГЭ и его тема. У предметов без разбивки по номерам этих полей нет.
					number = if type(raw.number) == "number" and raw.number % 1 == 0 and raw.number > 0 then raw.number else nil,
					topic = if type(raw.topic) == "string" then raw.topic else nil,
					-- Общий текст для нескольких заданий, например "reading:2": такие задания вариант берёт вместе.
					context = if type(raw.context) == "string" then raw.context else nil,
					-- Вторая часть экзамена и критерии оценивания развёрнутого ответа.
					part = if raw.part == 2 then 2 else nil,
					criteria = criteria,
				})
			end
		end
	end
	return result
end

-- Встроенная копия хранится не модулями Luau, а текстом: папка предмета с кусками JSON в StringValue.
-- Большие модули Studio разбирает как код, и частота кадров от этого падает в несколько раз.
local function readEmbedded(folder: Instance): string
	local chunks = folder:GetChildren()
	table.sort(chunks, function(a, b)
		return a.Name < b.Name
	end)
	local parts = {}
	for _, chunk in chunks do
		if chunk:IsA("StringValue") then
			table.insert(parts, chunk.Value)
		end
	end
	return table.concat(parts)
end

local function loadBuiltIn()
	local folder = ServerStorage:FindFirstChild("Bank")
	if not folder then
		warn("[Bank] В ServerStorage нет папки Bank, банк пуст")
		return
	end
	for _, subject in Subjects.list do
		local subjectFolder = folder:FindFirstChild(subject.id)
		if subjectFolder then
			local ok, data = pcall(function()
				return HttpService:JSONDecode(readEmbedded(subjectFolder))
			end)
			if ok and type(data) == "table" then
				tasksBySubject[subject.id] = sanitize(data.tasks)
			else
				warn("[Bank] Не удалось прочитать встроенную копию предмета " .. subject.id)
			end
		end
	end
end

local function fetchJson(url: string): any?
	local ok, body = pcall(function()
		return HttpService:GetAsync(url, true)
	end)
	if not ok then
		return nil
	end
	local decoded, data = pcall(function()
		return HttpService:JSONDecode(body)
	end)
	return if decoded then data else nil
end

local function loadOnline()
	local base = Config.bankBaseUrl
	if base == "" then
		return
	end
	local index = fetchJson(base .. "/index.json")
	if type(index) ~= "table" or type(index.subjects) ~= "table" then
		warn("[Bank] Не удалось скачать index.json, остаётся встроенный банк")
		return
	end
	local updated = 0
	for _, subject in Subjects.list do
		local entry = index.subjects[subject.id]
		if type(entry) == "table" and type(entry.file) == "string" then
			local data = fetchJson(base .. "/" .. entry.file)
			local tasks = if type(data) == "table" then sanitize(data.tasks) else {}
			if #tasks > 0 then
				tasksBySubject[subject.id] = tasks
				updated += 1
			end
		end
	end
	print(string.format("[Bank] Из интернета обновлено предметов: %d", updated))
end

function Bank.load()
	loadBuiltIn()
	-- Скачивание не должно задерживать запуск сервера.
	task.spawn(loadOnline)
end

function Bank.getTasks(subjectId: string): { any }
	return tasksBySubject[subjectId] or {}
end

function Bank.count(subjectId: string): number
	return #Bank.getTasks(subjectId)
end

-- Сколько заданий в полном варианте предмета: число номеров первой части, для которых есть задания.
-- Для предмета без разбивки по номерам возвращает 0.
function Bank.fullCount(subjectId: string): number
	local seen, count = {}, 0
	for _, task in Bank.getTasks(subjectId) do
		if task.number and task.part ~= 2 and not seen[task.number] then
			seen[task.number] = true
			count += 1
		end
	end
	return count
end

-- Сколько номеров во второй части предмета. Ноль означает, что второй части в банке нет.
function Bank.partTwoCount(subjectId: string): number
	local seen, count = {}, 0
	for _, task in Bank.getTasks(subjectId) do
		if task.number and task.part == 2 and not seen[task.number] then
			seen[task.number] = true
			count += 1
		end
	end
	return count
end

-- Случайное задание без рисунка из любого предмета, для доски «Задача дня».
function Bank.randomTextTask()
	local candidates = {}
	for _, subject in Subjects.list do
		for _, task in Bank.getTasks(subject.id) do
			-- Доске нужны короткие задания с однозначным ответом.
			if not task.figure and task.kind ~= "essay" and task.part ~= 2 and not task.context and #task.text < 600 then
				table.insert(candidates, { subject = subject.name, task = task })
			end
		end
	end
	if #candidates == 0 then
		return nil
	end
	return candidates[math.random(#candidates)]
end

-- Проверка одного задания: используется тестами.
Bank.sanitize = sanitize

return Bank
