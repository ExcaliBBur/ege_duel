-- Экран настройки матча: свой предмет, выбор соперника, голосование за время и число заданий.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Settings = require(Shared.Settings)
local Ui = require(script.Parent.Ui)

local SetupScreen = {}

local C = Ui.colors

-- Ряд кнопок голосования. options: список { value, label }. Возвращает функцию обновления
-- (мой голос, голос соперника, новые подписи кнопок по значению).
local function voteRow(parent: Instance, x: number, y: number, title: string, prefix: string, options, step: number, width: number, onVote: (any) -> ())
	Ui.caption(title, { Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(#options * step, 16), Parent = parent })
	local buttons, marks = {}, {}
	for index, option in options do
		local value = option.value
		local left = x + (index - 1) * step
		local button = Ui.button(option.label, "plain", {
			Name = prefix .. tostring(value),
			TextSize = 15,
			Position = UDim2.fromOffset(left, y + 22),
			Size = UDim2.fromOffset(width, 40),
			Parent = parent,
		})
		button.Activated:Connect(function()
			onVote(value)
		end)
		buttons[value] = button
		marks[value] = Ui.label({
			Text = "выбор соперника",
			TextSize = 12,
			Font = Ui.fonts.bold,
			TextColor3 = C.rival,
			TextXAlignment = Enum.TextXAlignment.Center,
			Position = UDim2.fromOffset(left - 10, y + 64),
			Size = UDim2.fromOffset(width + 20, 14),
			Visible = false,
			Parent = parent,
		})
	end
	return function(mine: any, rivals: any, labels: { [any]: string }?)
		for value, button in buttons do
			if labels and labels[value] then
				button.Text = labels[value]
			end
			Ui.styleButton(button, if value == mine then "selected" else "plain")
			marks[value].Visible = value == rivals
		end
	end
end

local function numberOptions(values: { number }, suffix: string)
	local options = {}
	for _, value in values do
		table.insert(options, { value = value, label = if value == 0 then "вся часть 1" else value .. suffix })
	end
	return options
end

-- actions: setSubject(id), voteTime(n), voteCount(n), votePart(bool), ready(bool), leave()
function SetupScreen.create(parent: Instance, actions)
	local screen = {}
	local state = nil

	local frame = Ui.frame({ Name = "Setup", Size = UDim2.fromScale(1, 1), Visible = false, Parent = parent }, { Ui.corner(14) })

	local header = Ui.frame({ Size = UDim2.new(1, 0, 0, 56), BackgroundColor3 = C.sunken, Parent = frame }, { Ui.corner(14) })
	Ui.label({
		Text = "Настройка матча",
		Font = Ui.fonts.bold,
		TextSize = 20,
		Position = UDim2.fromOffset(20, 0),
		Size = UDim2.new(0.6, 0, 1, 0),
		Parent = header,
	})
	local tableLabel = Ui.label({
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -220, 0, 0),
		Size = UDim2.fromOffset(200, 56),
		Parent = header,
	})

	-- Мой предмет.
	Ui.pill("Вы", C.accent, C.accentSoft, { Position = UDim2.fromOffset(20, 70), Size = UDim2.fromOffset(60, 26), Parent = frame })
	Ui.caption("ВАШ ПРЕДМЕТ", { Position = UDim2.fromOffset(92, 75), Size = UDim2.fromOffset(300, 16), Parent = frame })

	local subjectButtons = {}
	for index, subject in Subjects.list do
		local column = (index - 1) % 3
		local row = (index - 1) // 3
		local button = Ui.button(subject.name, "plain", {
			TextSize = 14,
			Position = UDim2.fromOffset(20 + column * 184, 106 + row * 48),
			Size = UDim2.fromOffset(174, 40),
			Parent = frame,
		})
		button.Activated:Connect(function()
			if state and (state.counts[subject.id] or 0) > 0 then
				actions.setSubject(subject.id)
			end
		end)
		subjectButtons[subject.id] = button
	end

	-- Соперник.
	local rivalPanel = Ui.frame({
		Position = UDim2.fromOffset(590, 70),
		Size = UDim2.fromOffset(310, 226),
		BackgroundColor3 = C.rivalSoft,
		Parent = frame,
	}, { Ui.corner(10) })
	local rivalName = Ui.label({
		Font = Ui.fonts.bold,
		TextColor3 = C.rival,
		TextSize = 18,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextWrapped = false,
		Position = UDim2.fromOffset(16, 12),
		Size = UDim2.new(1, -32, 0, 24),
		Parent = rivalPanel,
	})
	Ui.caption("ПРЕДМЕТ СОПЕРНИКА", { Position = UDim2.fromOffset(16, 52), Size = UDim2.new(1, -32, 0, 16), Parent = rivalPanel })
	local rivalSubject = Ui.label({
		Font = Ui.fonts.bold,
		TextSize = 22,
		Position = UDim2.fromOffset(16, 72),
		Size = UDim2.new(1, -32, 0, 60),
		TextYAlignment = Enum.TextYAlignment.Top,
		Parent = rivalPanel,
	})
	local rivalReady = Ui.pill("", C.muted, C.surface, {
		Position = UDim2.fromOffset(16, 180),
		Size = UDim2.fromOffset(150, 28),
		Parent = rivalPanel,
	})

	local updateTime = voteRow(frame, 20, 312, "ВРЕМЯ НА РАБОТУ, МИНУТ", "Vote", numberOptions(Settings.timeOptions, ""), 110, 102, actions.voteTime)
	local updateCount = voteRow(frame, 20, 402, "ПЕРВАЯ ЧАСТЬ: ВСЯ ИЛИ СОКРАЩЁННАЯ ПО НОМЕРАМ", "Vote", numberOptions(Settings.countOptions, ""), 142, 130,
		actions.voteCount)
	-- Вторая часть: задания с развёрнутым ответом, которые после сдачи оценивает соперник.
	local updatePart = voteRow(frame, 612, 402, "ВТОРАЯ ЧАСТЬ", "Part", { { value = false, label = "без неё" }, { value = true, label = "с ней" } }, 142, 130,
		actions.votePart)

	local status = Ui.label({
		TextSize = 14,
		TextYAlignment = Enum.TextYAlignment.Top,
		Position = UDim2.fromOffset(20, 490),
		Size = UDim2.new(1, -40, 0, 60),
		Parent = frame,
	})

	local leaveButton = Ui.button("Встать из-за стола", "plain", {
		Position = UDim2.new(0, 20, 1, -64),
		Size = UDim2.fromOffset(210, 44),
		Parent = frame,
	})
	leaveButton.Activated:Connect(actions.leave)

	local readyButton = Ui.button("Готов", "primary", {
		Position = UDim2.new(1, -260, 1, -64),
		Size = UDim2.fromOffset(240, 44),
		Parent = frame,
	})
	readyButton.Activated:Connect(function()
		if state and state.me.subject then
			actions.ready(not state.me.ready)
		end
	end)

	local function render()
		local me, rival = state.me, state.rival
		tableLabel.Text = "Парта " .. state.tableId

		for id, button in subjectButtons do
			if (state.counts[id] or 0) == 0 then
				Ui.styleButton(button, "disabled")
			elseif id == me.subject then
				Ui.styleButton(button, "selected")
			else
				Ui.styleButton(button, "plain")
			end
		end

		rivalName.Text = "Соперник: " .. rival.name
		rivalSubject.Text = if rival.subject then Subjects.nameOf(rival.subject) else "выбирает…"
		rivalSubject.TextColor3 = if rival.subject then C.ink else C.muted
		rivalReady.Text = if rival.ready then "Готов" else "Не готов"
		rivalReady.TextColor3 = if rival.ready then C.ok else C.muted

		updateTime(me.time, rival.time)
		-- У предмета с разбивкой по номерам показываем размер первой части.
		local full = me.subject and state.fullCounts and state.fullCounts[me.subject] or 0
		updateCount(me.count, rival.count, { [0] = if full > 0 then string.format("вся часть 1 (%d)", full) else "вся часть 1" })
		local second = me.subject and state.partTwoCounts and state.partTwoCounts[me.subject] or 0
		updatePart(me.part, rival.part, { [true] = if second > 0 then string.format("с ней (%d)", second) else "с ней" })

		local notes = {}
		if me.subject and me.subject == rival.subject then
			table.insert(notes, "Предмет одинаковый: вы получите один и тот же вариант.")
		end
		local differ = {}
		if me.time ~= rival.time then
			table.insert(differ, "время")
		end
		if me.count ~= rival.count then
			table.insert(differ, "число заданий")
		end
		if me.part ~= rival.part then
			table.insert(differ, "вторая часть")
		end
		if #differ > 0 then
			table.insert(notes, "Голоса не совпали (" .. table.concat(differ, ", ") .. "): решит жребий.")
		end
		if me.part and me.subject and second == 0 then
			table.insert(notes, "У вашего предмета второй части нет: вам достанется только первая.")
		elseif me.part then
			table.insert(notes, "Вторая часть: развёрнутые ответы после сдачи оценивает соперник по эталону и критериям.")
		end
		if not me.subject then
			table.insert(notes, "Выберите предмет, чтобы нажать «Готов».")
		elseif me.ready and not rival.ready then
			table.insert(notes, "Ждём, пока соперник нажмёт «Готов».")
		end
		status.Text = table.concat(notes, "\n")
		status.TextColor3 = if #differ > 0 then C.warn else C.muted

		if not me.subject then
			readyButton.Text = "Готов"
			Ui.styleButton(readyButton, "disabled")
		elseif me.ready then
			readyButton.Text = "Отменить готовность"
			Ui.styleButton(readyButton, "plain")
		else
			readyButton.Text = "Готов"
			Ui.styleButton(readyButton, "primary")
		end
	end

	function screen.show(newState)
		state = newState
		render()
		frame.Visible = true
	end

	function screen.hide()
		frame.Visible = false
	end

	return screen
end

return SetupScreen
