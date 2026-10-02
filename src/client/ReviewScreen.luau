-- Экран взаимной проверки: после сдачи игрок видит развёрнутые ответы соперника, эталонное решение и критерии
-- и выставляет баллы. Пока соперник оценивает его работу, экран показывает ожидание.
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Ui = require(script.Parent.Ui)

local ReviewScreen = {}

local C = Ui.colors

local MAX_SCORE = 25
local TEXT_HEIGHT = 4000 -- запас по высоте: надпись заведомо выше окна, холст считается по границам текста

-- Прокручиваемый текст. Возвращает функции: задать текст и подогнать высоту холста.
local function scrollText(parent: Instance, name: string, position: UDim2, size: UDim2, back: Color3)
	local scroll = Ui.new("ScrollingFrame", {
		Name = name,
		Position = position,
		Size = size,
		BackgroundColor3 = back,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = C.muted,
		CanvasSize = UDim2.new(),
		ScrollingDirection = Enum.ScrollingDirection.Y,
		Parent = parent,
	}, { Ui.corner(6) })
	local label = Ui.label({
		Name = "Text",
		TextSize = 15,
		LineHeight = 1.1,
		RichText = false,
		TextYAlignment = Enum.TextYAlignment.Top,
		Position = UDim2.fromOffset(10, 8),
		Size = UDim2.new(1, -28, 0, TEXT_HEIGHT),
		Parent = scroll,
	})
	local function fit()
		local scale = label.AbsoluteSize.Y / TEXT_HEIGHT
		if scale > 0 then
			local height = math.ceil(label.TextBounds.Y / scale) + 20
			if scroll.CanvasSize.Y.Offset ~= height then
				scroll.CanvasSize = UDim2.fromOffset(0, height)
			end
		end
	end
	local function set(text: string)
		label.Text = text
		scroll.CanvasPosition = Vector2.zero
	end
	return set, fit
end

-- actions: grade(index, score), done()
function ReviewScreen.create(parent: Instance, actions)
	local screen = {}
	local state = nil
	local current = 1
	local scores: { [number]: number } = {} -- оценки по номеру задания в варианте соперника
	local finished = false
	local reviewId = nil

	local frame = Ui.frame({ Name = "Review", Size = UDim2.fromScale(1, 1), Visible = false, Parent = parent }, { Ui.corner(14) })

	local header = Ui.frame({ Size = UDim2.new(1, 0, 0, 70), BackgroundColor3 = C.sunken, Parent = frame }, { Ui.corner(14) })
	local title = Ui.label({
		Font = Ui.fonts.display,
		TextSize = 24,
		Position = UDim2.fromOffset(20, 8),
		Size = UDim2.new(1, -200, 0, 32),
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextWrapped = false,
		Parent = header,
	})
	Ui.label({
		Text = "Сравните ответ с эталоном и поставьте балл по критериям. Соперник так же оценивает ваши ответы.",
		TextSize = 14,
		TextColor3 = C.muted,
		Position = UDim2.fromOffset(20, 40),
		Size = UDim2.new(1, -200, 0, 22),
		Parent = header,
	})
	local timerLabel = Ui.label({
		Name = "Timer",
		Font = Ui.fonts.mono,
		TextSize = 30,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -170, 0, 14),
		Size = UDim2.fromOffset(150, 40),
		Parent = header,
	})

	local prevButton = Ui.button("‹", "plain", {
		Name = "Prev",
		TextSize = 22,
		Position = UDim2.fromOffset(20, 80),
		Size = UDim2.fromOffset(44, 34),
		Parent = frame,
	})
	local nextButton = Ui.button("›", "plain", {
		Name = "Next",
		TextSize = 22,
		Position = UDim2.new(1, -64, 0, 80),
		Size = UDim2.fromOffset(44, 34),
		Parent = frame,
	})
	local itemTitle = Ui.label({
		Name = "ItemTitle",
		Font = Ui.fonts.bold,
		TextSize = 16,
		TextXAlignment = Enum.TextXAlignment.Center,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextWrapped = false,
		Position = UDim2.fromOffset(74, 80),
		Size = UDim2.new(1, -148, 0, 34),
		Parent = frame,
	})

	Ui.caption("ЗАДАНИЕ", { Position = UDim2.fromOffset(20, 124), Size = UDim2.fromOffset(430, 16), Parent = frame })
	local setTask, fitTask = scrollText(frame, "TaskScroll", UDim2.fromOffset(20, 144), UDim2.fromOffset(430, 130), C.sunken)
	Ui.caption("ОТВЕТ СОПЕРНИКА", {
		TextColor3 = C.rival,
		Position = UDim2.fromOffset(20, 284),
		Size = UDim2.fromOffset(430, 16),
		Parent = frame,
	})
	local setAnswer, fitAnswer = scrollText(frame, "AnswerScroll", UDim2.fromOffset(20, 304), UDim2.fromOffset(430, 180), C.rivalSoft)
	Ui.caption("ЭТАЛОННОЕ РЕШЕНИЕ И КРИТЕРИИ", {
		TextColor3 = C.ok,
		Position = UDim2.fromOffset(470, 124),
		Size = UDim2.fromOffset(430, 16),
		Parent = frame,
	})
	local setReference, fitReference = scrollText(frame, "ReferenceScroll", UDim2.fromOffset(470, 144), UDim2.fromOffset(430, 340), C.okSoft)

	local scoreCaption = Ui.caption("", { Name = "ScoreCaption", Position = UDim2.fromOffset(20, 494), Size = UDim2.fromOffset(880, 16), Parent = frame })
	local scoreButtons = {}
	for score = 0, MAX_SCORE do
		local button = Ui.button(tostring(score), "plain", {
			Name = "Score" .. score,
			Position = UDim2.fromOffset(20, 512),
			Size = UDim2.fromOffset(40, 38),
			Visible = false,
			Parent = frame,
		})
		scoreButtons[score] = button
	end

	local progress = Ui.label({
		Name = "Progress",
		TextSize = 14,
		TextColor3 = C.muted,
		Position = UDim2.new(0, 20, 1, -64),
		Size = UDim2.new(1, -280, 0, 44),
		Parent = frame,
	})
	local doneButton = Ui.button("Завершить проверку", "disabled", {
		Name = "Done",
		Position = UDim2.new(1, -240, 1, -64),
		Size = UDim2.fromOffset(220, 44),
		Parent = frame,
	})

	-- Закрывает экран, когда проверять больше нечего: остаётся дождаться соперника.
	local cover = Ui.frame({
		Name = "Cover",
		Position = UDim2.fromOffset(0, 70),
		Size = UDim2.new(1, 0, 1, -70),
		ZIndex = 5,
		Visible = false,
		Parent = frame,
	}, { Ui.corner(14) })
	local coverText = Ui.label({
		Name = "CoverText",
		Font = Ui.fonts.bold,
		TextSize = 20,
		TextXAlignment = Enum.TextXAlignment.Center,
		Position = UDim2.fromOffset(60, 120),
		Size = UDim2.new(1, -120, 0, 200),
		ZIndex = 6,
		Parent = cover,
	})

	local function gradedCount(): number
		local count = 0
		for _, item in state.items do
			if scores[item.index] ~= nil then
				count += 1
			end
		end
		return count
	end

	local function renderScore()
		local item = state.items[current]
		if not item then
			return
		end
		local mine = scores[item.index]
		scoreCaption.Text = if mine ~= nil
			then string.format("ВАША ОЦЕНКА: %d ИЗ %d", mine, item.points)
			else string.format("ПОСТАВЬТЕ ОЦЕНКУ: ОТ 0 ДО %d", item.points)
		local step = math.min(52, 880 // (item.points + 1))
		for score, button in scoreButtons do
			button.Visible = score <= item.points
			if button.Visible then
				button.Position = UDim2.fromOffset(20 + score * step, 512)
				button.Size = UDim2.fromOffset(step - 6, 38)
				Ui.styleButton(button, if score == mine then "selected" else "plain")
			end
		end
		local graded, total = gradedCount(), #state.items
		progress.Text = if graded == total
			then "Все ответы оценены. Оценки можно поменять, пока проверка не завершена."
			else string.format("Оценено %d из %d. Ответ без оценки по истечении времени получит полный балл.", graded, total)
		Ui.styleButton(doneButton, if graded == total then "primary" else "disabled")
	end

	local function renderItem()
		local total = #state.items
		current = math.clamp(current, 1, math.max(1, total))
		local item = state.items[current]
		if not item then
			return
		end
		itemTitle.Text = string.format(
			"Ответ %d из %d · задание № %d%s · до %d %s",
			current,
			total,
			item.number or item.index,
			if item.topic then " · " .. item.topic else "",
			item.points,
			Ui.plural(item.points, "балла", "баллов", "баллов")
		)
		setTask(item.text)
		setAnswer(item.answer or "")
		local lines = {}
		if item.solution and item.solution ~= "" then
			table.insert(lines, item.solution)
			table.insert(lines, "")
		end
		table.insert(lines, "Критерии:")
		for _, line in item.criteria or {} do
			table.insert(lines, "• " .. line)
		end
		setReference(table.concat(lines, "\n"))
		Ui.styleButton(prevButton, if current > 1 then "plain" else "disabled")
		Ui.styleButton(nextButton, if current < total then "plain" else "disabled")
		renderScore()
	end

	local function renderCover()
		if #state.items == 0 then
			cover.Visible = true
			coverText.Text = string.format(
				"Соперник оценивает ваши развёрнутые ответы: %d.\nПроверять вам нечего, итоги появятся, когда он закончит.",
				state.waitingForMe
			)
		elseif finished then
			cover.Visible = true
			coverText.Text = if state.rivalDone
				then "Проверка завершена. Подводим итоги…"
				else "Вы закончили проверку.\nЖдём, пока соперник оценит ваши ответы."
		else
			cover.Visible = false
		end
	end

	local function go(delta: number)
		if state and not finished and state.items[current + delta] then
			current += delta
			renderItem()
		end
	end
	prevButton.Activated:Connect(function()
		go(-1)
	end)
	nextButton.Activated:Connect(function()
		go(1)
	end)

	for score, button in scoreButtons do
		button.Activated:Connect(function()
			local item = state and state.items[current]
			if not item or finished or score > item.points then
				return
			end
			scores[item.index] = score
			actions.grade(item.index, score)
			renderScore()
		end)
	end

	doneButton.Activated:Connect(function()
		if state and not finished and gradedCount() == #state.items then
			finished = true
			actions.done()
			renderCover()
		end
	end)

	function screen.show(newState)
		-- Сервер присылает состояние повторно, когда соперник заканчивает проверку: набранное при этом сохраняется.
		if reviewId ~= newState.endsAt then
			reviewId = newState.endsAt
			current = 1
			scores = {}
			finished = false
		end
		state = newState
		for _, item in state.items do
			if scores[item.index] == nil and item.score ~= nil then
				scores[item.index] = item.score
			end
		end
		finished = finished or state.done == true
		title.Text = "Проверка работы: " .. tostring(state.rivalName)
		renderItem()
		renderCover()
		frame.Visible = true
	end

	function screen.hide()
		frame.Visible = false
		reviewId = nil
	end

	RunService.Heartbeat:Connect(function()
		if not frame.Visible or not state then
			return
		end
		local remaining = state.endsAt - Workspace:GetServerTimeNow()
		timerLabel.Text = Ui.clock(remaining)
		timerLabel.TextColor3 = if remaining <= 30 then C.danger else C.ink
		fitTask()
		fitAnswer()
		fitReference()
	end)

	return screen
end

return ReviewScreen
