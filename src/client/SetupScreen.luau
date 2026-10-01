-- Экран настройки матча: свой предмет, выбор соперника, голосование за время и число заданий.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Settings = require(Shared.Settings)
local Ui = require(script.Parent.Ui)

local SetupScreen = {}

local C = Ui.colors

-- Ряд кнопок голосования. Возвращает рамку и функцию обновления (мой голос, голос соперника).
local function voteRow(parent: Instance, y: number, title: string, options: { number }, suffix: string, onVote: (number) -> ())
	Ui.caption(title, { Position = UDim2.fromOffset(20, y), Size = UDim2.fromOffset(400, 16), Parent = parent })
	local buttons, marks = {}, {}
	for index, option in options do
		local x = 20 + (index - 1) * 142
		local button = Ui.button(option .. suffix, "plain", {
			Position = UDim2.fromOffset(x, y + 22),
			Size = UDim2.fromOffset(130, 40),
			Parent = parent,
		})
		button.Activated:Connect(function()
			onVote(option)
		end)
		buttons[option] = button
		marks[option] = Ui.label({
			Text = "выбор соперника",
			TextSize = 12,
			Font = Ui.fonts.bold,
			TextColor3 = C.rival,
			TextXAlignment = Enum.TextXAlignment.Center,
			Position = UDim2.fromOffset(x, y + 64),
			Size = UDim2.fromOffset(130, 14),
			Visible = false,
			Parent = parent,
		})
	end
	return function(mine: number, rivals: number)
		for option, button in buttons do
			Ui.styleButton(button, if option == mine then "selected" else "plain")
			marks[option].Visible = option == rivals
		end
	end
end

-- actions: setSubject(id), voteTime(n), voteCount(n), ready(bool), leave()
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

	local updateTime = voteRow(frame, 312, "ВРЕМЯ НА РАБОТУ", Settings.timeOptions, " мин", actions.voteTime)
	local updateCount = voteRow(frame, 402, "ЧИСЛО ЗАДАНИЙ", Settings.countOptions, "", actions.voteCount)

	local status = Ui.label({
		TextSize = 15,
		Position = UDim2.fromOffset(20, 496),
		Size = UDim2.new(1, -40, 0, 40),
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
		updateCount(me.count, rival.count)

		local notes = {}
		if me.subject and me.subject == rival.subject then
			table.insert(notes, "Предмет одинаковый: вы получите один и тот же вариант.")
		end
		if me.time ~= rival.time and me.count ~= rival.count then
			table.insert(notes, "Время и число заданий не совпали: их выберет жребий.")
		elseif me.time ~= rival.time then
			table.insert(notes, "Время не совпало: его выберет жребий.")
		elseif me.count ~= rival.count then
			table.insert(notes, "Число заданий не совпало: его выберет жребий.")
		end
		if not me.subject then
			table.insert(notes, "Выберите предмет, чтобы нажать «Готов».")
		elseif me.ready and not rival.ready then
			table.insert(notes, "Ждём, пока соперник нажмёт «Готов».")
		end
		status.Text = table.concat(notes, "\n")
		status.TextColor3 = if me.time ~= rival.time or me.count ~= rival.count then C.warn else C.muted

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
