-- Матчи за партами. У каждой парты своё состояние:
--   idle       за партой никого или один игрок ждёт соперника
--   setup      двое выбирают предметы и голосуют за время и число заданий
--   countdown  отсчёт перед началом
--   exam       идёт экзамен
--   review     взаимная проверка развёрнутых ответов второй части
--   results    показаны итоги, можно взять реванш
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TextService = game:GetService("TextService")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Settings = require(Shared.Settings)
local Scoring = require(Shared.Scoring)
local Text = require(Shared.Text)
local Bank = require(script.Parent.Bank)
local Variant = require(script.Parent.Variant)

local Duel = {}

local stateEvent: RemoteEvent -- сервер -> клиент: снимок состояния по фазе
local rivalEvent: RemoteEvent -- сервер -> клиент: прогресс соперника во время экзамена
local actionEvent: RemoteEvent -- клиент -> сервер: действия игрока

local tables = {}
local entryByPlayer = {} -- [Player] = { tbl, slot }

local function now(): number
	return Workspace:GetServerTimeNow()
end

local function rivalOf(tbl, slot)
	return tbl.slots[3 - slot.index]
end

local function isPresent(slot): boolean
	if slot == nil or slot.left then
		return false
	end
	return slot.bot or slot.player.Parent ~= nil
end

-- Тестовому сопернику сообщения не отправляются.
local function sendState(slot, payload)
	if isPresent(slot) and not slot.bot then
		stateEvent:FireClient(slot.player, payload)
	end
end

local function sendRival(slot, payload)
	if isPresent(slot) and not slot.bot then
		rivalEvent:FireClient(slot.player, payload)
	end
end

local function newSlot(player: Player, index: number)
	return {
		player = player,
		index = index,
		name = player.DisplayName,
		subject = nil,
		timeVote = Settings.defaultTime,
		countVote = Settings.defaultCount,
		partVote = false,
		ready = false,
		tasks = {},
		answers = {},
		answered = 0,
		submitted = false,
		elapsed = 0,
		left = false,
		rematch = false,
	}
end

-- Тестовый соперник: доступен только в Studio, чтобы проверять игру в одиночку.
local function newBotSlot(index: number)
	return {
		bot = true,
		index = index,
		name = "Тестовый соперник",
		subject = nil,
		timeVote = Settings.defaultTime,
		countVote = Settings.defaultCount,
		partVote = false,
		ready = false,
		tasks = {},
		answers = {},
		answered = 0,
		submitted = false,
		elapsed = 0,
		left = false,
		rematch = false,
	}
end

local function formatClock(seconds: number): string
	seconds = math.max(0, math.floor(seconds))
	return string.format("%02d:%02d", seconds // 60, seconds % 60)
end

local function refreshStatus(tbl)
	local phase = tbl.phase
	if phase == "idle" then
		local hasPlayer = tbl.slots[1] ~= nil or tbl.slots[2] ~= nil
		tbl.setStatus(if hasPlayer then "Ждёт соперника" else "Свободно", false)
	elseif phase == "setup" then
		tbl.setStatus("Выбирают предметы", true)
	elseif phase == "countdown" then
		tbl.setStatus("Матч начинается", true)
	elseif phase == "exam" then
		local a, b = tbl.slots[1], tbl.slots[2]
		tbl.setStatus(
			string.format("Решено %d и %d · осталось %s", a.answered, b.answered, formatClock(tbl.endsAt - now())),
			true
		)
	elseif phase == "review" then
		tbl.setStatus("Проверяют работы друг друга", true)
	elseif phase == "results" then
		tbl.setStatus("Матч окончен", true)
	end
	for index, prompt in tbl.prompts do
		prompt.Enabled = phase == "idle" and tbl.slots[index] == nil
	end
	if tbl.setLamp then
		tbl.setLamp(phase == "exam") -- настольная лампа горит, пока идёт экзамен
	end
end

local function bankCounts()
	local counts = {}
	for _, subject in Subjects.list do
		counts[subject.id] = Bank.count(subject.id)
	end
	return counts
end

-- Размер первой части по предметам, чтобы на экране настройки было видно, сколько заданий в полном варианте.
local function fullCounts()
	local counts = {}
	for _, subject in Subjects.list do
		counts[subject.id] = Bank.fullCount(subject.id)
	end
	return counts
end

-- Сколько номеров во второй части каждого предмета.
local function partTwoCounts()
	local counts = {}
	for _, subject in Subjects.list do
		counts[subject.id] = Bank.partTwoCount(subject.id)
	end
	return counts
end

local function isBlank(answer: string?): boolean
	return answer == nil or Text.normalize(answer) == ""
end

-- Снимок этапа взаимной проверки для одного игрока: работы соперника, которые ему нужно оценить.
local function reviewSnapshot(tbl, slot)
	local rival = tbl.slots[3 - slot.index]
	local items = {}
	for _, taskIndex in slot.reviewItems do
		local task = rival.tasks[taskIndex]
		table.insert(items, {
			index = taskIndex,
			number = task.number,
			topic = task.topic,
			text = task.text,
			figure = task.figure,
			points = task.points,
			solution = task.explanation,
			criteria = task.criteria,
			answer = rival.shown[taskIndex],
			score = slot.grades[taskIndex],
		})
	end
	return {
		phase = "review",
		tableId = tbl.id,
		endsAt = tbl.reviewEndsAt,
		rivalName = rival.name,
		rivalSubject = rival.subject,
		items = items,
		done = slot.reviewDone,
		rivalDone = rival.reviewDone,
		waitingForMe = #rival.reviewItems, -- сколько моих ответов оценивает соперник
	}
end

local function rivalProgress(slot)
	return {
		answered = slot.answered,
		total = #slot.tasks,
		submitted = slot.submitted,
		left = slot.left,
	}
end

local function snapshotFor(tbl, slot)
	local rival = rivalOf(tbl, slot)
	local phase = tbl.phase
	if phase == "idle" then
		return { phase = "waiting", tableId = tbl.id, canAddBot = RunService:IsStudio() }
	elseif phase == "setup" then
		return {
			phase = "setup",
			tableId = tbl.id,
			counts = bankCounts(),
			fullCounts = fullCounts(),
			partTwoCounts = partTwoCounts(),
			me = { subject = slot.subject, time = slot.timeVote, count = slot.countVote, part = slot.partVote, ready = slot.ready },
			rival = {
				name = rival.name,
				subject = rival.subject,
				time = rival.timeVote,
				count = rival.countVote,
				part = rival.partVote,
				ready = rival.ready,
			},
		}
	elseif phase == "countdown" then
		local settings = tbl.settings
		return {
			phase = "countdown",
			tableId = tbl.id,
			startsAt = tbl.startsAt,
			time = settings.time,
			count = settings.count,
			lotTime = settings.lotTime,
			lotCount = settings.lotCount,
			part = settings.part,
			lotPart = settings.lotPart,
			subject = slot.subject,
			rivalName = rival.name,
			rivalSubject = rival.subject,
		}
	elseif phase == "exam" then
		local publicTasks = {}
		for index, task in slot.tasks do
			-- Правильные ответы клиенту не отправляются.
			publicTasks[index] = {
				text = task.text,
				points = task.points,
				figure = task.figure,
				number = task.number,
				topic = task.topic,
				part = task.part,
				essay = task.kind == "essay" or nil, -- развёрнутый ответ: большое поле вместо клеток
			}
		end
		local progress = rivalProgress(rival)
		progress.name = rival.name
		progress.subject = rival.subject
		return {
			phase = "exam",
			tableId = tbl.id,
			subject = slot.subject,
			startedAt = tbl.startedAt,
			endsAt = tbl.endsAt,
			tasks = publicTasks,
			rival = progress,
		}
	elseif phase == "review" then
		return reviewSnapshot(tbl, slot)
	end
	return { phase = "none" }
end

local function push(tbl)
	for _, slot in tbl.slots do
		if isPresent(slot) and not slot.bot then
			sendState(slot, snapshotFor(tbl, slot))
		end
	end
	refreshStatus(tbl)
end

local function standUp(player: Player, seat: Seat)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not humanoid or seat.Occupant ~= humanoid then
		return
	end
	local weld = seat:FindFirstChild("SeatWeld")
	if weld then
		weld:Destroy()
	end
	humanoid.Sit = false
	-- Отодвигаем персонажа в сторону, чтобы он тут же не сел обратно от касания стула.
	task.defer(function()
		if character.Parent then
			character:PivotTo(seat.CFrame * CFrame.new(4.5, 3, 0))
		end
	end)
end

local function reseat(tbl, slot)
	if tbl.slots[slot.index] ~= slot or not isPresent(slot) then
		return
	end
	if tbl.phase ~= "exam" and tbl.phase ~= "countdown" and tbl.phase ~= "review" then
		return
	end
	local seat = tbl.seats[slot.index]
	if seat.Occupant then
		return
	end
	local character = slot.player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if humanoid and humanoid.Health > 0 then
		seat:Sit(humanoid)
	end
end

-- Убирает игрока из-за парты. В фазах exam, review и countdown не вызывается.
local function removeSlot(tbl, index: number)
	local slot = tbl.slots[index]
	if not slot then
		return
	end
	tbl.slots[index] = nil
	if not slot.bot then
		if entryByPlayer[slot.player] and entryByPlayer[slot.player].slot == slot then
			entryByPlayer[slot.player] = nil
		end
		sendState(slot, { phase = "none" })
	end

	local other = tbl.slots[3 - index]
	local previous = tbl.phase
	tbl.phase = "idle"
	if other and other.bot then
		-- Тестовый соперник уходит вместе с игроком.
		tbl.slots[3 - index] = nil
	elseif other then
		other.ready = false
		other.rematch = false
		if previous == "results" then
			-- Оставшийся игрок продолжает смотреть итоги, пока сам не встанет или не придёт новый соперник.
			sendState(other, {
				phase = "resultsUpdate",
				rivalPresent = false,
				rematch = { me = false, rival = false },
			})
		elseif previous == "setup" then
			sendState(other, snapshotFor(tbl, other))
		end
	end
	refreshStatus(tbl)
end

-- Тестовый соперник соглашается с голосами игрока и всегда готов.
local function syncBot(tbl)
	for _, slot in tbl.slots do
		if slot.bot then
			local human = rivalOf(tbl, slot)
			if human then
				slot.timeVote = human.timeVote
				slot.countVote = human.countVote
				slot.partVote = human.partVote
				-- Со второй частью тестовый соперник берёт предмет игрока: так игроку есть что проверять.
				if human.partVote and human.subject and Bank.partTwoCount(human.subject) > 0 then
					slot.subject = human.subject
				end
			end
			slot.ready = slot.subject ~= nil
		end
	end
end

local function enterSetup(tbl)
	tbl.phase = "setup"
	for _, slot in tbl.slots do
		slot.ready = false
		slot.rematch = false
	end
	syncBot(tbl)
	push(tbl)
end

local function buildCard(slot)
	local summary = slot.summary
	return {
		name = slot.name,
		subject = slot.subject,
		earned = summary.earned,
		max = summary.max,
		percent = Scoring.percent(summary.earned, summary.max),
		correct = summary.correct,
		partial = summary.partial,
		answered = summary.answered,
		total = summary.total,
		elapsed = slot.elapsed,
	}
end

local function buildReview(slot)
	local review = {}
	for index, task in slot.tasks do
		review[index] = {
			text = task.text,
			your = slot.answers[index] or "",
			correct = task.answers[1],
			points = task.points,
			earned = slot.summary.perTask[index],
			explanation = task.explanation,
			figure = task.figure,
			number = task.number,
			-- Развёрнутый ответ: оценку поставил соперник по этим критериям.
			essay = task.kind == "essay" or nil,
			criteria = task.criteria,
			void = slot.summary.void[index] or nil,
		}
	end
	return review
end

-- Доска побед: считает матчи между живыми игроками за время работы сервера.
local scores = {} -- [userId] = { name, wins, games }
local showScoreboard: ((string) -> ())? = nil

local function recordResult(slot, rival, outcome: string)
	if slot.bot or rival.bot then
		return
	end
	local userId = slot.player.UserId
	local entry = scores[userId] or { name = slot.name, wins = 0, games = 0 }
	scores[userId] = entry
	entry.games += 1
	if outcome == "win" then
		entry.wins += 1
	end
end

local function refreshScoreboard()
	if not showScoreboard then
		return
	end
	local rows = {}
	for _, entry in scores do
		table.insert(rows, entry)
	end
	table.sort(rows, function(x, y)
		if x.wins ~= y.wins then
			return x.wins > y.wins
		end
		return x.name < y.name
	end)
	local lines = {}
	for place = 1, math.min(#rows, 8) do
		local entry = rows[place]
		table.insert(lines, string.format("%d. %s: побед %d из %d", place, entry.name, entry.wins, entry.games))
	end
	showScoreboard(if #lines > 0 then table.concat(lines, "\n") else "Пока никто не сыграл.\nСтаньте первыми!")
end

-- Оценки, которые получил автор за развёрнутые ответы. Пустой ответ даёт 0. Ответ, который не удалось
-- показать сопернику, в счёт не идёт. Если соперник не успел поставить оценку, автор получает полный балл:
-- так тянуть время с проверкой невыгодно.
local function givenScores(slot, rival)
	local given = {}
	for index, task in slot.tasks do
		if task.kind == "essay" then
			if isBlank(slot.answers[index]) then
				given[index] = 0
			elseif slot.hidden and slot.hidden[index] then
				given[index] = false
			elseif rival.grades and rival.grades[index] ~= nil then
				given[index] = rival.grades[index]
			else
				given[index] = task.points
			end
		end
	end
	return given
end

-- Подводит итоги матча: после экзамена, если проверять нечего, или после взаимной проверки.
local function conclude(tbl)
	tbl.matchId += 1 -- отменяет таймеры экзамена и проверки
	tbl.phase = "results"
	local a, b = tbl.slots[1], tbl.slots[2]
	for _, slot in { a, b } do
		slot.summary = Scoring.summarize(slot.tasks, slot.answers, givenScores(slot, rivalOf(tbl, slot)))
		slot.rematch = slot.bot == true -- тестовый соперник всегда согласен на реванш
	end

	for _, slot in { a, b } do
		local rival = rivalOf(tbl, slot)
		local outcome, reason = Scoring.decide(
			{ earned = slot.summary.earned, max = slot.summary.max, elapsed = slot.elapsed, left = slot.left },
			{ earned = rival.summary.earned, max = rival.summary.max, elapsed = rival.elapsed, left = rival.left }
		)
		recordResult(slot, rival, outcome)
		if outcome == "win" and isPresent(slot) and tbl.celebrate then
			tbl.celebrate(slot.index)
		end
		if isPresent(slot) then
			sendState(slot, {
				phase = "results",
				tableId = tbl.id,
				outcome = outcome,
				reason = reason,
				me = buildCard(slot),
				rival = buildCard(rival),
				review = buildReview(slot),
				rematch = { me = false, rival = rival.rematch },
				rivalPresent = isPresent(rival),
			})
		end
	end

	-- Вышедших из игры убираем, парта освобождается для нового соперника.
	for index = 1, 2 do
		local slot = tbl.slots[index]
		if slot and not isPresent(slot) then
			tbl.slots[index] = nil
			tbl.phase = "idle"
		end
	end
	refreshStatus(tbl)
	refreshScoreboard()
end

-- Текст игрока можно показывать другому игроку только после фильтра Roblox.
local function filterText(text: string, author): string?
	if author.bot then
		return text
	end
	local ok, result = pcall(function()
		return TextService:FilterStringAsync(text, author.player.UserId):GetNonChatStringForBroadcastAsync()
	end)
	return if ok and type(result) == "string" then result else nil
end

local function reviewFinished(tbl): boolean
	for _, slot in tbl.slots do
		if not slot.reviewDone and isPresent(slot) then
			return false
		end
	end
	return true
end

-- Конец экзамена. Если во второй части есть развёрнутые ответы, начинается взаимная проверка, иначе сразу итоги.
local function finish(tbl)
	tbl.matchId += 1 -- отменяет таймер конца экзамена
	local matchId = tbl.matchId
	local a, b = tbl.slots[1], tbl.slots[2]
	local everyoneHere = true
	for _, slot in { a, b } do
		if not slot.submitted then
			slot.submitted = true
			slot.elapsed = tbl.duration
		end
		slot.reviewItems = {}
		slot.grades = {}
		slot.shown = {}
		slot.hidden = {}
		slot.reviewDone = false
		everyoneHere = everyoneHere and isPresent(slot)
	end
	if not everyoneHere then
		conclude(tbl) -- соперник вышел: победа присуждается без проверки
		return
	end

	tbl.phase = "review"
	refreshStatus(tbl)
	for _, author in { a, b } do
		local reviewer = rivalOf(tbl, author)
		for index, task in author.tasks do
			if task.kind == "essay" and not isBlank(author.answers[index]) then
				local shown = filterText(author.answers[index], author) -- может ждать ответа сервиса
				if shown then
					author.shown[index] = shown
					table.insert(reviewer.reviewItems, index)
				else
					author.hidden[index] = true
				end
			end
		end
	end
	if tbl.matchId ~= matchId or tbl.phase ~= "review" then
		return -- пока шла фильтрация, матч закончился иначе (кто-то вышел)
	end
	if #a.reviewItems == 0 and #b.reviewItems == 0 then
		conclude(tbl)
		return
	end

	for _, slot in { a, b } do
		if slot.bot then
			-- Тестовый соперник ставит за каждую работу половину баллов и сразу заканчивает.
			for _, index in slot.reviewItems do
				slot.grades[index] = math.ceil(rivalOf(tbl, slot).tasks[index].points / 2)
			end
			slot.reviewDone = true
		elseif #slot.reviewItems == 0 then
			slot.reviewDone = true -- проверять нечего, игрок просто ждёт
		end
	end
	local seconds = Settings.reviewSeconds(math.max(#a.reviewItems, #b.reviewItems))
	tbl.reviewEndsAt = now() + seconds
	push(tbl)
	if reviewFinished(tbl) then
		conclude(tbl)
		return
	end
	task.delay(seconds + Settings.graceSeconds, function()
		if tbl.matchId == matchId and tbl.phase == "review" then
			conclude(tbl)
		end
	end)
end

local function allDone(tbl): boolean
	for _, slot in tbl.slots do
		if not slot.submitted and not slot.left then
			return false
		end
	end
	return true
end

local function notifyRival(tbl, slot)
	sendRival(rivalOf(tbl, slot), rivalProgress(slot))
end

local BOT_ANSWER_SECONDS = 4
local BOT_CORRECT_CHANCE = 0.6

local function botEssay(botTask, index: number): string
	return string.format("Тестовый развёрнутый ответ соперника на задание №%d.", botTask.number or index)
end

-- Тестовый соперник отвечает на одно задание раз в несколько секунд, затем сдаёт работу.
local function runBot(tbl, slot, matchId: number)
	local function active(): boolean
		return tbl.matchId == matchId and tbl.phase == "exam" and tbl.slots[slot.index] == slot
	end
	for index, botTask in slot.tasks do
		task.wait(BOT_ANSWER_SECONDS)
		if not active() or now() >= tbl.endsAt then
			return
		end
		if botTask.kind == "essay" then
			slot.answers[index] = botEssay(botTask, index)
		else
			slot.answers[index] = if math.random() < BOT_CORRECT_CHANCE then botTask.answers[1] else "0"
		end
		slot.answered = index
		notifyRival(tbl, slot)
	end
	task.wait(BOT_ANSWER_SECONDS)
	if active() and not slot.submitted then
		slot.submitted = true
		slot.elapsed = math.clamp(now() - tbl.startedAt, 0, tbl.duration)
		notifyRival(tbl, slot)
		if allDone(tbl) then
			finish(tbl)
		end
	end
end

local function startExam(tbl)
	local settings = tbl.settings
	local seed = os.time() + math.floor(os.clock() * 1000) + tbl.id * 7919
	local variants = {}
	for _, slot in tbl.slots do
		-- Одинаковый предмет даёт обоим один и тот же вариант.
		if not variants[slot.subject] then
			variants[slot.subject] = Variant.pick(Bank.getTasks(slot.subject), settings.count, seed, settings.part)
		end
		slot.tasks = variants[slot.subject]
		slot.answers = {}
		slot.answered = 0
		slot.submitted = false
		slot.elapsed = 0
		slot.ready = false
		slot.rematch = false
	end

	tbl.matchId += 1
	local matchId = tbl.matchId
	tbl.duration = settings.time * 60
	tbl.startedAt = now()
	tbl.endsAt = tbl.startedAt + tbl.duration
	tbl.phase = "exam"
	push(tbl)

	task.delay(tbl.duration + Settings.graceSeconds, function()
		if tbl.matchId == matchId and tbl.phase == "exam" then
			finish(tbl)
		end
	end)

	for _, slot in tbl.slots do
		if slot.bot then
			task.spawn(runBot, tbl, slot, matchId)
		end
	end
end

-- fixed: настройки прошлого матча при реванше; без них настройки берутся из голосов.
local function startCountdown(tbl, fixed)
	local a, b = tbl.slots[1], tbl.slots[2]
	local settings = { lotTime = false, lotCount = false, lotPart = false }
	if fixed then
		settings.time = fixed.time
		settings.count = fixed.count
		settings.part = fixed.part
	else
		settings.time = a.timeVote
		settings.count = a.countVote
		settings.part = a.partVote
		if a.partVote ~= b.partVote then
			settings.lotPart = true
			settings.part = if math.random(2) == 1 then a.partVote else b.partVote
		end
		if a.timeVote ~= b.timeVote then
			settings.lotTime = true
			settings.time = if math.random(2) == 1 then a.timeVote else b.timeVote
		end
		if a.countVote ~= b.countVote then
			settings.lotCount = true
			settings.count = if math.random(2) == 1 then a.countVote else b.countVote
		end
	end
	tbl.settings = settings

	-- Если был жребий, даём две лишние секунды прочитать его результат.
	local seconds = Settings.countdownSeconds + (if settings.lotTime or settings.lotCount or settings.lotPart then 2 else 0)
	tbl.matchId += 1
	local matchId = tbl.matchId
	tbl.startsAt = now() + seconds
	tbl.phase = "countdown"
	push(tbl)

	task.delay(seconds, function()
		if tbl.matchId == matchId and tbl.phase == "countdown" then
			startExam(tbl)
		end
	end)
end

local function resetReady(tbl)
	for _, slot in tbl.slots do
		slot.ready = false
	end
	syncBot(tbl)
end

local handlers = {}

function handlers.setSubject(tbl, slot, value)
	if tbl.phase ~= "setup" then
		return
	end
	if type(value) ~= "string" or not Subjects.byId[value] or Bank.count(value) == 0 then
		return
	end
	slot.subject = value
	resetReady(tbl)
	push(tbl)
end

function handlers.voteTime(tbl, slot, value)
	if tbl.phase ~= "setup" or not Settings.isTimeOption(value) then
		return
	end
	slot.timeVote = value
	resetReady(tbl)
	push(tbl)
end

function handlers.voteCount(tbl, slot, value)
	if tbl.phase ~= "setup" or not Settings.isCountOption(value) then
		return
	end
	slot.countVote = value
	resetReady(tbl)
	push(tbl)
end

-- Голос за вторую часть экзамена: true включает задания с развёрнутым ответом.
function handlers.votePart(tbl, slot, value)
	if tbl.phase ~= "setup" or type(value) ~= "boolean" then
		return
	end
	slot.partVote = value
	resetReady(tbl)
	push(tbl)
end

function handlers.ready(tbl, slot, value)
	if tbl.phase ~= "setup" then
		return
	end
	if value == true and not slot.subject then
		return
	end
	slot.ready = value == true
	local rival = rivalOf(tbl, slot)
	if slot.ready and rival.ready then
		startCountdown(tbl, nil)
	else
		push(tbl)
	end
end

-- Сажает напротив тестового соперника. Работает только в Studio.
function handlers.addBot(tbl, slot)
	if not RunService:IsStudio() or tbl.phase ~= "idle" then
		return
	end
	local index = 3 - slot.index
	if tbl.slots[index] or tbl.seats[index].Occupant then
		return
	end
	local available = {}
	for _, subject in Subjects.list do
		if Bank.count(subject.id) > 0 then
			table.insert(available, subject.id)
		end
	end
	if #available == 0 then
		return
	end
	local bot = newBotSlot(index)
	bot.subject = available[math.random(#available)]
	tbl.slots[index] = bot
	enterSetup(tbl)
end

function handlers.leave(tbl, slot)
	if tbl.phase == "exam" or tbl.phase == "countdown" or tbl.phase == "review" then
		return
	end
	local player, seat = slot.player, tbl.seats[slot.index]
	removeSlot(tbl, slot.index)
	standUp(player, seat)
end

function handlers.answer(tbl, slot, payload)
	if tbl.phase ~= "exam" or slot.submitted then
		return
	end
	if now() > tbl.endsAt + Settings.graceSeconds or type(payload) ~= "table" then
		return
	end
	local index, value = payload.index, payload.value
	if type(index) ~= "number" or index % 1 ~= 0 or index < 1 or index > #slot.tasks then
		return
	end
	if type(value) ~= "string" then
		return
	end
	if slot.tasks[index].kind == "essay" then
		-- Развёрнутый ответ: длинный текст, переносы строк и точки сохраняются.
		if #value > Settings.essayMaxChars * 4 then
			return
		end
		slot.answers[index] = Text.truncate(value, Settings.essayMaxChars)
	else
		if #value > 200 then
			return
		end
		-- В бланке дробная часть отделяется запятой, поэтому точка всегда заменяется на запятую.
		slot.answers[index] = (string.gsub(Text.truncate(value, Settings.answerMaxChars), "%.", ","))
	end

	local answered = 0
	for taskIndex = 1, #slot.tasks do
		if not isBlank(slot.answers[taskIndex]) then
			answered += 1
		end
	end
	if answered ~= slot.answered then
		slot.answered = answered
		notifyRival(tbl, slot)
	end
end

function handlers.submit(tbl, slot)
	if tbl.phase ~= "exam" or slot.submitted then
		return
	end
	slot.submitted = true
	slot.elapsed = math.clamp(now() - tbl.startedAt, 0, tbl.duration)
	notifyRival(tbl, slot)
	local rival = rivalOf(tbl, slot)
	if rival.bot and not rival.submitted then
		-- Тестовый соперник не заставляет себя ждать. Развёрнутые ответы он дописывает сразу,
		-- чтобы в Studio можно было попробовать экран взаимной проверки.
		for index, botTask in rival.tasks do
			if botTask.kind == "essay" and isBlank(rival.answers[index]) then
				rival.answers[index] = botEssay(botTask, index)
			end
		end
		rival.submitted = true
		rival.elapsed = slot.elapsed
	end
	if allDone(tbl) then
		finish(tbl)
	end
end

-- Оценка за развёрнутый ответ соперника. payload: { index = номер задания в его варианте, score = балл }.
function handlers.grade(tbl, slot, payload)
	if tbl.phase ~= "review" or slot.reviewDone or type(payload) ~= "table" then
		return
	end
	local index, score = payload.index, payload.score
	if type(index) ~= "number" or not table.find(slot.reviewItems, index) then
		return
	end
	local points = rivalOf(tbl, slot).tasks[index].points
	if type(score) ~= "number" or score % 1 ~= 0 or score < 0 or score > points then
		return
	end
	slot.grades[index] = score
end

-- Игрок закончил проверку. Принимается, только когда оценены все работы.
function handlers.reviewDone(tbl, slot)
	if tbl.phase ~= "review" or slot.reviewDone then
		return
	end
	for _, index in slot.reviewItems do
		if slot.grades[index] == nil then
			return
		end
	end
	slot.reviewDone = true
	if reviewFinished(tbl) then
		conclude(tbl)
	else
		push(tbl)
	end
end

function handlers.rematch(tbl, slot)
	if tbl.phase ~= "results" then
		return
	end
	local rival = rivalOf(tbl, slot)
	if not isPresent(rival) then
		return
	end
	slot.rematch = true
	if rival.rematch then
		-- Оба согласны: возвращаемся к настройке. Прошлые предметы и голоса остаются выбранными,
		-- их можно поменять перед новым матчем.
		enterSetup(tbl)
		return
	end
	sendState(slot, {
		phase = "resultsUpdate",
		rivalPresent = true,
		rematch = { me = true, rival = false },
	})
	sendState(rival, {
		phase = "resultsUpdate",
		rivalPresent = true,
		rematch = { me = false, rival = true },
	})
end

local function onAction(player: Player, action: any, payload: any)
	local entry = entryByPlayer[player]
	if not entry or type(action) ~= "string" then
		return
	end
	local handler = handlers[action]
	if handler then
		handler(entry.tbl, entry.slot, payload)
	end
end

local function onOccupantChanged(tbl, index: number)
	local seat = tbl.seats[index]
	local humanoid = seat.Occupant
	local slot = tbl.slots[index]

	if humanoid then
		local player = Players:GetPlayerFromCharacter(humanoid.Parent)
		if not player then
			return
		end
		if slot and slot.player == player then
			return -- игрок вернулся на своё место
		end
		-- Чужое место, идущий матч или игрок уже числится за другой партой: сесть нельзя.
		if slot or tbl.phase ~= "idle" or entryByPlayer[player] then
			task.defer(standUp, player, seat)
			return
		end
		local created = newSlot(player, index)
		tbl.slots[index] = created
		entryByPlayer[player] = { tbl = tbl, slot = created }
		if tbl.slots[1] and tbl.slots[2] then
			enterSetup(tbl)
		else
			push(tbl)
		end
	elseif slot then
		if tbl.phase == "exam" or tbl.phase == "countdown" or tbl.phase == "review" then
			-- Во время матча место сохраняется за игроком, возвращаем его за парту.
			task.delay(0.3, reseat, tbl, slot)
		else
			removeSlot(tbl, index)
		end
	end
end

local function onPlayerRemoving(player: Player)
	local entry = entryByPlayer[player]
	if not entry then
		return
	end
	local tbl, slot = entry.tbl, entry.slot
	if tbl.phase == "exam" then
		entryByPlayer[player] = nil
		slot.left = true
		if not slot.submitted then
			slot.submitted = true
			slot.elapsed = tbl.duration
		end
		local rival = rivalOf(tbl, slot)
		if not isPresent(rival) or rival.bot then
			-- Вышли оба или остался только тестовый соперник: матч просто сбрасывается.
			tbl.matchId += 1
			tbl.slots = {}
			tbl.phase = "idle"
			refreshStatus(tbl)
			return
		end
		notifyRival(tbl, slot)
		if allDone(tbl) then
			finish(tbl)
		end
	elseif tbl.phase == "review" then
		-- Вышел во время взаимной проверки: матч заканчивается, непроверенные ответы соперника засчитываются полностью.
		entryByPlayer[player] = nil
		slot.left = true
		conclude(tbl)
	else
		if tbl.phase == "countdown" then
			tbl.matchId += 1 -- отменяет старт экзамена
			tbl.phase = "setup"
		end
		removeSlot(tbl, slot.index)
	end
end

local function onCharacterAdded(player: Player)
	local entry = entryByPlayer[player]
	if entry then
		task.delay(1, reseat, entry.tbl, entry.slot)
	end
end

local function newRemote(name: string): RemoteEvent
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = ReplicatedStorage:WaitForChild("Remotes")
	return remote
end

-- worldTables: список парт из World.build. setScoreboard: функция, которая пишет текст на доску побед.
function Duel.start(worldTables, setScoreboard: ((string) -> ())?)
	showScoreboard = setScoreboard
	refreshScoreboard()

	local folder = Instance.new("Folder")
	folder.Name = "Remotes"
	folder.Parent = ReplicatedStorage

	stateEvent = newRemote("State")
	rivalEvent = newRemote("Rival")
	actionEvent = newRemote("Action")
	actionEvent.OnServerEvent:Connect(onAction)

	for _, worldTable in worldTables do
		local tbl = {
			id = worldTable.id,
			seats = worldTable.seats,
			prompts = worldTable.prompts,
			setStatus = worldTable.setStatus,
			setLamp = worldTable.setLamp,
			celebrate = worldTable.celebrate,
			phase = "idle",
			slots = {},
			matchId = 0,
		}
		table.insert(tables, tbl)

		for index, seat in tbl.seats do
			seat:GetPropertyChangedSignal("Occupant"):Connect(function()
				onOccupantChanged(tbl, index)
			end)
			tbl.prompts[index].Triggered:Connect(function(player: Player)
				if seat.Occupant or tbl.slots[index] or tbl.phase ~= "idle" or entryByPlayer[player] then
					return
				end
				local character = player.Character
				local humanoid = character and character:FindFirstChildOfClass("Humanoid")
				if humanoid and humanoid.Health > 0 and not humanoid.Sit then
					seat:Sit(humanoid)
				end
			end)
		end
		refreshStatus(tbl)
	end

	Players.PlayerRemoving:Connect(onPlayerRemoving)
	local function watch(player: Player)
		player.CharacterAdded:Connect(function()
			onCharacterAdded(player)
		end)
	end
	Players.PlayerAdded:Connect(watch)
	for _, player in Players:GetPlayers() do
		watch(player)
	end

	-- Таймер на табличках парт.
	task.spawn(function()
		while true do
			task.wait(1)
			for _, tbl in tables do
				if tbl.phase == "exam" then
					refreshStatus(tbl)
				end
			end
		end
	end)
end

return Duel
