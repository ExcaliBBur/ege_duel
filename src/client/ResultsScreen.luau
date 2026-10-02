-- Экран итогов: исход, баллы и число верных ответов у обоих, разбор своей работы, реванш.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Ui = require(script.Parent.Ui)
local Figure = require(script.Parent.Figure)

local ResultsScreen = {}

local C = Ui.colors

local OUTCOME_TITLES = { win = "Победа", lose = "Поражение", draw = "Ничья" }

local function reasonText(outcome: string, reason: string): string
	if reason == "walkover" then
		return if outcome == "win" then "Соперник вышел из игры" else "Вы вышли из игры"
	elseif outcome == "draw" then
		return "Доля баллов и время сдачи совпали"
	elseif reason == "time" then
		return "Доля баллов равная, победил сдавший работу раньше"
	end
	return "Сравниваем долю набранных баллов от максимума по своему предмету"
end

-- Карточка игрока. Возвращает функцию заполнения.
local function scoreCard(parent: Instance, x: number, mine: boolean)
	local card = Ui.frame({
		Position = UDim2.fromOffset(x, 84),
		Size = UDim2.fromOffset(430, 150),
		Parent = parent,
	}, { Ui.corner(10) })
	local stroke = Ui.stroke(C.line, 1.5)
	stroke.Parent = card

	local pill = Ui.pill("", if mine then C.accent else C.rival, if mine then C.accentSoft else C.rivalSoft, {
		Position = UDim2.fromOffset(14, 12),
		Size = UDim2.fromOffset(402, 26),
		BackgroundTransparency = 0,
		Parent = card,
	})
	local percent = Ui.label({
		Font = Ui.fonts.display,
		TextSize = 44,
		Position = UDim2.fromOffset(14, 46),
		Size = UDim2.fromOffset(150, 56),
		Parent = card,
	})
	local points = Ui.label({ TextSize = 15, Position = UDim2.fromOffset(170, 48), Size = UDim2.fromOffset(250, 22), Parent = card })
	local correct = Ui.label({
		TextSize = 15,
		Font = Ui.fonts.bold,
		Position = UDim2.fromOffset(170, 72),
		Size = UDim2.fromOffset(250, 22),
		Parent = card,
	})
	local extra = Ui.label({
		TextSize = 14,
		TextColor3 = C.muted,
		Position = UDim2.fromOffset(14, 110),
		Size = UDim2.fromOffset(402, 30),
		Parent = card,
	})

	return function(data, winner: boolean)
		pill.Text = string.format("%s · %s", if mine then "Вы" else data.name, Subjects.nameOf(data.subject))
		percent.Text = data.percent .. "%"
		points.Text = string.format(
			"%d из %d %s",
			data.earned,
			data.max,
			Ui.plural(data.max, "первичного балла", "первичных баллов", "первичных баллов")
		)
		correct.Text = string.format("Верных ответов: %d из %d", data.correct, data.total)
		local parts = {}
		if data.partial > 0 then
			table.insert(parts, "частично верных: " .. data.partial)
		end
		table.insert(parts, "без ответа: " .. (data.total - data.answered))
		table.insert(parts, "время: " .. Ui.clock(data.elapsed))
		extra.Text = table.concat(parts, " · ")
		stroke.Color = if winner then (if mine then C.accent else C.rival) else C.line
		stroke.Thickness = if winner then 3 else 1.5
	end
end

-- actions: rematch(), leave()
function ResultsScreen.create(parent: Instance, actions)
	local screen = {}
	local state = nil
	local onlyMistakes = true

	local frame = Ui.frame({ Name = "Results", Size = UDim2.fromScale(1, 1), Visible = false, Parent = parent }, { Ui.corner(14) })

	local header = Ui.frame({ Size = UDim2.new(1, 0, 0, 70), BackgroundColor3 = C.sunken, Parent = frame }, { Ui.corner(14) })
	local title = Ui.label({
		Font = Ui.fonts.display,
		TextSize = 26,
		Position = UDim2.fromOffset(20, 8),
		Size = UDim2.new(1, -40, 0, 32),
		Parent = header,
	})
	local reason = Ui.label({
		TextSize = 14,
		TextColor3 = C.muted,
		Position = UDim2.fromOffset(20, 40),
		Size = UDim2.new(1, -40, 0, 22),
		Parent = header,
	})

	local fillMine = scoreCard(frame, 20, true)
	local fillRival = scoreCard(frame, 470, false)

	Ui.caption("РАЗБОР ВАШЕЙ РАБОТЫ", { Position = UDim2.fromOffset(20, 250), Size = UDim2.fromOffset(400, 16), Parent = frame })
	local filterButton = Ui.button("", "plain", {
		TextSize = 14,
		Position = UDim2.new(1, -220, 0, 242),
		Size = UDim2.fromOffset(200, 30),
		Parent = frame,
	})

	local list = Ui.new("ScrollingFrame", {
		Position = UDim2.fromOffset(20, 280),
		Size = UDim2.new(1, -40, 0, 262),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = C.muted,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		Parent = frame,
	}, {
		Ui.new("UIListLayout", { Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder }),
	})
	local emptyNote = Ui.label({
		Text = "Ошибок нет. Все ответы верные.",
		TextColor3 = C.ok,
		Font = Ui.fonts.bold,
		Position = UDim2.fromOffset(20, 290),
		Size = UDim2.new(1, -40, 0, 30),
		Visible = false,
		Parent = frame,
	})

	local leaveButton = Ui.button("Встать из-за стола", "plain", {
		Position = UDim2.new(0, 20, 1, -64),
		Size = UDim2.fromOffset(210, 44),
		Parent = frame,
	})
	leaveButton.Activated:Connect(actions.leave)

	local rematchNote = Ui.label({
		TextSize = 14,
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(0, 240, 1, -64),
		Size = UDim2.new(1, -480, 0, 44),
		Parent = frame,
	})
	local rematchButton = Ui.button("Реванш", "primary", {
		Position = UDim2.new(1, -220, 1, -64),
		Size = UDim2.fromOffset(200, 44),
		Parent = frame,
	})
	rematchButton.Activated:Connect(function()
		if state and state.rivalPresent and not state.rematch.me then
			actions.rematch()
		end
	end)

	local function reviewRow(index: number, item)
		local full = item.earned == item.points
		local row = Ui.frame({
			Size = UDim2.new(1, -12, 0, 0),
			AutomaticSize = Enum.AutomaticSize.Y,
			BackgroundColor3 = if full then C.okSoft elseif item.earned > 0 then C.warnSoft else C.dangerSoft,
			LayoutOrder = index,
		}, {
			Ui.corner(8),
			Ui.new("UIPadding", {
				PaddingTop = UDim.new(0, 10),
				PaddingBottom = UDim.new(0, 10),
				PaddingLeft = UDim.new(0, 12),
				PaddingRight = UDim.new(0, 12),
			}),
			Ui.new("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }),
		})

		local yours = if item.your == "" then "ответа нет" else "ваш ответ: " .. item.your
		Ui.label({
			Text = string.format("№ %d · %d из %d · %s · верно: %s", item.number or index, item.earned, item.points, yours, item.correct),
			Font = Ui.fonts.bold,
			TextSize = 15,
			TextColor3 = if full then C.ok elseif item.earned > 0 then C.warn else C.danger,
			Size = UDim2.new(1, 0, 0, 0),
			AutomaticSize = Enum.AutomaticSize.Y,
			LayoutOrder = 1,
			Parent = row,
		})
		Ui.label({
			Text = item.text,
			TextSize = 14,
			Size = UDim2.new(1, 0, 0, 0),
			AutomaticSize = Enum.AutomaticSize.Y,
			TextYAlignment = Enum.TextYAlignment.Top,
			LayoutOrder = 2,
			Parent = row,
		})
		local figure = Figure.render(item.figure, row)
		if figure then
			figure.LayoutOrder = 3
		end
		if item.explanation and item.explanation ~= "" then
			Ui.label({
				Text = "Пояснение: " .. item.explanation,
				TextSize = 14,
				TextColor3 = C.muted,
				Size = UDim2.new(1, 0, 0, 0),
				AutomaticSize = Enum.AutomaticSize.Y,
				TextYAlignment = Enum.TextYAlignment.Top,
				LayoutOrder = 4,
				Parent = row,
			})
		end
		return row
	end

	local function renderReview()
		for _, child in list:GetChildren() do
			if child:IsA("Frame") then
				child:Destroy()
			end
		end
		local shown = 0
		for index, item in state.review do
			if not onlyMistakes or item.earned < item.points then
				reviewRow(index, item).Parent = list
				shown += 1
			end
		end
		list.CanvasPosition = Vector2.zero
		emptyNote.Visible = shown == 0
		filterButton.Text = if onlyMistakes then "Показать все задания" else "Показать только ошибки"
	end

	filterButton.Activated:Connect(function()
		if state then
			onlyMistakes = not onlyMistakes
			renderReview()
		end
	end)

	local function renderRematch()
		if not state.rivalPresent then
			rematchNote.Text = "Соперник ушёл. Можно остаться за партой и подождать нового."
			rematchButton.Text = "Реванш"
			Ui.styleButton(rematchButton, "disabled")
		elseif state.rematch.me then
			rematchNote.Text = "Ждём ответа соперника."
			rematchButton.Text = "Реванш предложен"
			Ui.styleButton(rematchButton, "disabled")
		elseif state.rematch.rival then
			rematchNote.Text = "Соперник хочет реванш."
			rematchButton.Text = "Принять реванш"
			Ui.styleButton(rematchButton, "primary")
		else
			rematchNote.Text = "Перед реваншем можно сменить предмет и настройки."
			rematchButton.Text = "Реванш"
			Ui.styleButton(rematchButton, "primary")
		end
	end

	function screen.show(newState)
		state = newState
		onlyMistakes = true

		title.Text = OUTCOME_TITLES[state.outcome] or "Итоги"
		title.TextColor3 = if state.outcome == "win" then C.ok elseif state.outcome == "lose" then C.danger else C.ink
		reason.Text = reasonText(state.outcome, state.reason)

		fillMine(state.me, state.outcome == "win")
		fillRival(state.rival, state.outcome == "lose")
		renderReview()
		renderRematch()
		frame.Visible = true
	end

	-- Обновление без перерисовки разбора: реванш и уход соперника.
	function screen.update(patch)
		if not state then
			return
		end
		state.rivalPresent = patch.rivalPresent
		state.rematch = patch.rematch
		renderRematch()
	end

	function screen.isVisible(): boolean
		return frame.Visible
	end

	function screen.hide()
		if frame.Visible then
			-- Разбор может содержать сотни объектов (строки и рисунки), скрытым он не нужен.
			for _, child in list:GetChildren() do
				if child:IsA("Frame") then
					child:Destroy()
				end
			end
		end
		frame.Visible = false
	end

	return screen
end

return ResultsScreen
