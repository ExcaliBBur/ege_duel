-- Банк заданий. Сначала берётся копия, встроенная в игру (ServerStorage.Bank),
-- затем, если задан Config.bankBaseUrl, предметы обновляются свежими файлами из интернета.
local HttpService = game:GetService("HttpService")
local ServerStorage = game:GetService("ServerStorage")

local Shared = game:GetService("ReplicatedStorage"):WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Config = require(script.Parent.Config)

local Bank = {}

local tasksBySubject: { [string]: { any } } = {}

local VALID_KINDS = { exact = true, number = true, set = true, order = true }

local FIGURE_FIELDS = { line = 6, rect = 6, circle = 5, text = 5 } -- вид фигуры и число полей
local FIGURE_MAX_ITEMS = 150

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
			local points = if raw.points == 2 then 2 else 1
			local kind = if VALID_KINDS[raw.kind] then raw.kind else "exact"
			if #answers > 0 then
				table.insert(result, {
					id = tostring(raw.id or #result + 1),
					group = if type(raw.group) == "string" then raw.group else nil,
					text = raw.text,
					answers = answers,
					points = points,
					kind = kind,
					explanation = if type(raw.explanation) == "string" then raw.explanation else "",
					figure = sanitizeFigure(raw.figure),
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

-- Случайное задание без рисунка из любого предмета, для доски «Задача дня».
function Bank.randomTextTask()
	local candidates = {}
	for _, subject in Subjects.list do
		for _, task in Bank.getTasks(subject.id) do
			if not task.figure then
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
