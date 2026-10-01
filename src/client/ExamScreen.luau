-- Экран экзамена: задание с рисунком, поле ответа клетками как в бланке №1, навигатор, таймер, прогресс соперника.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local SoundService = game:GetService("SoundService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Settings = require(Shared.Settings)
local Text = require(Shared.Text)
local Ui = require(script.Parent.Ui)
local Figure = require(script.Parent.Figure)
local Reference = require(script.Parent.Reference)

local ExamScreen = {}

local C = Ui.colors
local CELLS = Settings.answerMaxChars
local MAX_TASKS = 20

local function serverNow(): number
	return Workspace:GetServerTimeNow()
end

-- actions: answer(index, value), submit()
function ExamScreen.create(parent: Instance, actions)
	local screen = {}

	local tasks = {}
	local answers: { [number]: string } = {}
	local flags: { [number]: boolean } = {}
	local current = 1
	local submitted = false
	local timeUp = false
	local endsAt = 0
	local duration = 0
	local pending: { index: number, value: string }? = nil
	local sendToken = 0
	local lastBeepStage = 0
	local settingText = false
	local subjectName = ""
	local subjectId = ""
	local figureFrame: Frame? = nil

	local frame = Ui.frame({ Name = "Exam", Size = UDim2.fromScale(1, 1), Visible = false, Parent = parent }, { Ui.corner(14) })

	local beep = Ui.new("Sound", { SoundId = "rbxasset://sounds/electronicpingshort.wav", Volume = 0.5, Parent = frame })

	-- Шапка: предмет и номер задания, таймер, кнопка сдачи. Кнопка стоит вверху, далеко от листания заданий.
	local header = Ui.frame({ Size = UDim2.new(1, 0, 0, 56), BackgroundColor3 = C.sunken, Parent = frame }, { Ui.corner(14) })
	local titleLabel = Ui.label({
		Font = Ui.fonts.bold,
		TextSize = 18,
		Position = UDim2.fromOffset(20, 0),
		Size = UDim2.new(1, -400, 1, 0),
		TextWrapped = false,
		TextTruncate = Enum.TextTruncate.AtEnd,
		Parent = header,
	})
	local timerLabel = Ui.label({
		Font = Ui.fonts.mono,
		TextSize = 28,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -370, 0, 0),
		Size = UDim2.fromOffset(130, 56),
		Parent = header,
	})
	local submitButton = Ui.button("Сдать работу", "danger", {
		Name = "Submit",
		Position = UDim2.new(1, -216, 0, 9),
		Size = UDim2.fromOffset(200, 38),
		Parent = header,
	})

	-- Соперник.
	local rivalPill = Ui.pill("", C.rival, C.rivalSoft, {
		Position = UDim2.fromOffset(20, 64),
		Size = UDim2.fromOffset(360, 26),
		Parent = frame,
	})
	local rivalText = Ui.label({
		TextSize = 14,
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -420, 0, 64),
		Size = UDim2.fromOffset(400, 26),
		Parent = frame,
	})
	local rivalBar = Ui.frame({
		Position = UDim2.fromOffset(20, 96),
		Size = UDim2.new(1, -40, 0, 6),
		BackgroundColor3 = C.sunken,
		Parent = frame,
	}, { Ui.corner(3) })
	local rivalFill = Ui.frame({ Size = UDim2.fromScale(0, 1), BackgroundColor3 = C.rival, Parent = rivalBar }, { Ui.corner(3) })

	-- Навигатор: номера всех заданий над текстом.
	local navButtons = {}
	for index = 1, MAX_TASKS do
		navButtons[index] = Ui.button(tostring(index), "plain", {
			Name = "Nav" .. index,
			Font = Ui.fonts.mono,
			TextSize = 16,
			Position = UDim2.fromOffset(20 + (index - 1) * 44, 112),
			Size = UDim2.fromOffset(38, 34),
			Visible = false,
			Parent = frame,
		})
	end
	Ui.label({
		Text = "Закрашено: ответ дан. Жёлтое: отмечено, чтобы вернуться. Толстая рамка: текущее задание.",
		TextSize = 12,
		TextColor3 = C.muted,
		Position = UDim2.fromOffset(20, 150),
		Size = UDim2.new(1, -40, 0, 16),
		Parent = frame,
	})

	-- Задание со стрелками по бокам.
	local prevButton = Ui.button("‹", "plain", {
		Name = "Prev",
		TextSize = 34,
		Position = UDim2.fromOffset(20, 174),
		Size = UDim2.fromOffset(40, 284),
		Parent = frame,
	})
	local nextButton = Ui.button("›", "plain", {
		Name = "Next",
		TextSize = 34,
		Position = UDim2.new(1, -60, 0, 174),
		Size = UDim2.fromOffset(40, 284),
		Parent = frame,
	})
	local taskScroll = Ui.new("ScrollingFrame", {
		Position = UDim2.fromOffset(72, 174),
		Size = UDim2.new(1, -144, 0, 284),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = C.muted,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		Parent = frame,
	})
	local pointsLabel = Ui.caption("", { Size = UDim2.new(1, -12, 0, 16), Parent = taskScroll })
	-- Текст слева, рисунок справа: так задание с рисунком помещается на экран без прокрутки.
	local taskLabel = Ui.label({
		Name = "TaskText",
		TextSize = 19,
		LineHeight = 1.15,
		TextYAlignment = Enum.TextYAlignment.Top,
		Position = UDim2.fromOffset(0, 22),
		Size = UDim2.new(1, -12, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		Parent = taskScroll,
	})

	-- Поле ответа: настоящий TextBox невидим и лежит поверх клеток, клетки показывают введённые символы.
	Ui.caption("ОТВЕТ", { Position = UDim2.fromOffset(20, 466), Size = UDim2.fromOffset(100, 16), Parent = frame })
	Ui.label({
		Text = "Без пробелов, как в бланке. В дробях точка сама заменяется на запятую.",
		TextSize = 13,
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -560, 0, 466),
		Size = UDim2.fromOffset(540, 16),
		Parent = frame,
	})
	local cellRow = Ui.frame({
		Position = UDim2.fromOffset(20, 486),
		Size = UDim2.fromOffset(CELLS * 40 - 4, 44),
		BackgroundTransparency = 1,
		Parent = frame,
	})
	local cells = {}
	for index = 1, CELLS do
		local cell = Ui.label({
			Font = Ui.fonts.mono,
			TextSize = 24,
			TextXAlignment = Enum.TextXAlignment.Center,
			BackgroundTransparency = 0,
			BackgroundColor3 = C.surface,
			Position = UDim2.fromOffset((index - 1) * 40, 0),
			Size = UDim2.fromOffset(36, 44),
			Parent = cellRow,
		})
		Ui.corner(3).Parent = cell
		Ui.stroke(C.line, 1.5).Parent = cell
		cells[index] = cell
	end
	local input = Ui.new("TextBox", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		TextTransparency = 1,
		TextSize = 1,
		Text = "",
		PlaceholderText = "",
		ClearTextOnFocus = false,
		MultiLine = false,
		ZIndex = 5,
		Parent = cellRow,
	})

	-- Нижний ряд: отметка и переход к заданию без ответа.
	local flagButton = Ui.button("Отметить", "plain", {
		Name = "Flag",
		Position = UDim2.new(0, 20, 1, -64),
		Size = UDim2.fromOffset(170, 44),
		Parent = frame,
	})
	local nextEmptyButton = Ui.button("К заданию без ответа", "plain", {
		Name = "NextEmpty",
		Position = UDim2.new(0, 200, 1, -64),
		Size = UDim2.fromOffset(240, 44),
		Parent = frame,
	})
	-- Справочные материалы, которые выдают на экзамене по этому предмету. Кнопка видна, только если они есть.
	local referenceButton = Ui.button("Справочные материалы", "rival", {
		Name = "ReferenceButton",
		Position = UDim2.new(0, 450, 1, -64),
		Size = UDim2.fromOffset(236, 44),
		Visible = false,
		Parent = frame,
	})
	local hintLabel = Ui.label({
		Text = "Enter или Tab: следующее\nPageUp, PageDown: листать",
		TextSize = 12,
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Right,
		Position = UDim2.new(1, -216, 1, -64),
		Size = UDim2.fromOffset(196, 44),
		Parent = frame,
	})

	-- Подтверждение сдачи: отдельное окно по центру, главная кнопка в нём возвращает к заданиям.
	local confirmShade = Ui.frame({
		Name = "Confirm",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = C.ink,
		BackgroundTransparency = 0.35,
		Active = true,
		Visible = false,
		ZIndex = 30,
		Parent = frame,
	}, { Ui.corner(14) })
	local confirmCard = Ui.frame({
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(560, 290),
		Parent = confirmShade,
	}, { Ui.corner(14), Ui.stroke(C.danger, 3) })
	Ui.label({
		Text = "Сдать работу?",
		Font = Ui.fonts.display,
		TextSize = 26,
		TextColor3 = C.danger,
		Position = UDim2.fromOffset(28, 22),
		Size = UDim2.new(1, -56, 0, 32),
		Parent = confirmCard,
	})
	local confirmText = Ui.label({
		TextSize = 17,
		TextYAlignment = Enum.TextYAlignment.Top,
		LineHeight = 1.2,
		Position = UDim2.fromOffset(28, 66),
		Size = UDim2.new(1, -56, 0, 120),
		Parent = confirmCard,
	})
	local confirmNo = Ui.button("Вернуться к заданиям", "primary", {
		Name = "ConfirmNo",
		Position = UDim2.new(0, 28, 1, -74),
		Size = UDim2.fromOffset(280, 50),
		Parent = confirmCard,
	})
	local confirmYes = Ui.button("Сдать окончательно", "danger", {
		Name = "ConfirmYes",
		Position = UDim2.new(1, -228, 1, -74),
		Size = UDim2.fromOffset(200, 50),
		Parent = confirmCard,
	})

	local reference = Reference.create(frame)
	referenceButton.Activated:Connect(function()
		if not (submitted or timeUp) then
			input:ReleaseFocus()
			reference.open(subjectId)
		end
	end)

	-- Заглушка после сдачи работы.
	local doneCover = Ui.frame({
		Position = UDim2.fromOffset(0, 106),
		Size = UDim2.new(1, 0, 1, -106),
		Visible = false,
		ZIndex = 20,
		Parent = frame,
	}, { Ui.corner(14) })
	local doneText = Ui.label({
		Font = Ui.fonts.bold,
		TextSize = 24,
		TextXAlignment = Enum.TextXAlignment.Center,
		Size = UDim2.new(1, -80, 1, 0),
		Position = UDim2.fromOffset(40, 0),
		Parent = doneCover,
	})

	local function isAnswered(index: number): boolean
		local answer = answers[index]
		return answer ~= nil and Text.normalize(answer) ~= ""
	end

	local function isLocked(): boolean
		return submitted or timeUp
	end

	local function flush()
		if pending then
			actions.answer(pending.index, pending.value)
			pending = nil
		end
	end

	local function renderCells()
		local chars = Text.chars(Text.upper(answers[current] or ""))
		local focused = input:IsFocused()
		for index, cell in cells do
			cell.Text = chars[index] or ""
			local stroke = cell:FindFirstChildOfClass("UIStroke")
			if index <= #chars then
				stroke.Color = C.accent
			elseif focused and index == #chars + 1 then
				stroke.Color = C.ink
			else
				stroke.Color = C.line
			end
		end
	end

	local function renderNav()
		for index, button in navButtons do
			if index <= #tasks then
				button.Visible = true
				local style = "plain"
				if flags[index] then
					style = "warn"
				elseif isAnswered(index) then
					style = "primary"
				end
				Ui.styleButton(button, style)
				local stroke = button:FindFirstChildOfClass("UIStroke")
				stroke.Thickness = if index == current then 4 else 1.5
				if index == current then
					stroke.Color = C.ink
				end
			else
				button.Visible = false
			end
		end
		Ui.styleButton(prevButton, if current > 1 then "plain" else "disabled")
		Ui.styleButton(nextButton, if current < #tasks then "plain" else "disabled")
	end

	local function renderTask()
		local task = tasks[current]
		if not task then
			return
		end
		titleLabel.Text = string.format("%s · задание %d из %d", subjectName, current, #tasks)
		pointsLabel.Text = if task.points == 2 then "2 БАЛЛА" else "1 БАЛЛ"
		taskLabel.Text = task.text
		if figureFrame then
			figureFrame:Destroy()
			figureFrame = nil
		end
		figureFrame = Figure.render(task.figure, taskScroll)
		if figureFrame then
			local width = figureFrame.Size.X.Offset
			figureFrame.AnchorPoint = Vector2.new(1, 0)
			figureFrame.Position = UDim2.new(1, -14, 0, 22)
			taskLabel.Size = UDim2.new(1, -(width + 40), 0, 0)
		else
			taskLabel.Size = UDim2.new(1, -12, 0, 0)
		end
		taskScroll.CanvasPosition = Vector2.zero
		flagButton.Text = if flags[current] then "Снять отметку" else "Отметить"

		settingText = true
		input.Text = answers[current] or ""
		settingText = false
		renderCells()
		renderNav()
	end

	-- Переходит к заданию. keepTyping: после перехода курсор остаётся в поле ответа.
	local function goTo(index: number, keepTyping: boolean?)
		if isLocked() or index < 1 or index > #tasks then
			return
		end
		if index ~= current then
			flush()
			current = index
			renderTask()
		end
		if keepTyping then
			task.defer(function()
				if frame.Visible and not isLocked() and not confirmShade.Visible then
					input:CaptureFocus()
				end
			end)
		end
	end

	local function nextEmpty(): number?
		for step = 1, #tasks do
			local index = (current + step - 1) % #tasks + 1
			if not isAnswered(index) then
				return index
			end
		end
		return nil
	end

	local function setLocked(text: string)
		flush()
		input:ReleaseFocus()
		input.TextEditable = false
		confirmShade.Visible = false
		reference.close()
		doneText.Text = text
		doneCover.Visible = true
	end

	input:GetPropertyChangedSignal("Text"):Connect(function()
		if settingText or isLocked() then
			return
		end
		local cleaned = string.gsub(input.Text, "[\r\n\t]", "")
		cleaned = string.gsub(cleaned, "%.", ",") -- в бланке дробная часть отделяется запятой
		cleaned = Text.truncate(cleaned, CELLS)
		if cleaned ~= input.Text then
			-- Присваивание вызовет этот обработчик ещё раз, уже с чистым текстом.
			input.Text = cleaned
			return
		end
		answers[current] = cleaned
		renderCells()
		renderNav()

		pending = { index = current, value = cleaned }
		sendToken += 1
		local token = sendToken
		task.delay(0.35, function()
			if token == sendToken then
				flush()
			end
		end)
	end)
	input.Focused:Connect(renderCells)
	input.FocusLost:Connect(function(enterPressed: boolean)
		flush()
		renderCells()
		if enterPressed and current < #tasks then
			goTo(current + 1, true)
		end
	end)

	for index, button in navButtons do
		button.Activated:Connect(function()
			goTo(index)
		end)
	end
	prevButton.Activated:Connect(function()
		goTo(current - 1)
	end)
	nextButton.Activated:Connect(function()
		goTo(current + 1)
	end)
	flagButton.Activated:Connect(function()
		if isLocked() then
			return
		end
		flags[current] = not flags[current] or nil
		flagButton.Text = if flags[current] then "Снять отметку" else "Отметить"
		renderNav()
	end)
	nextEmptyButton.Activated:Connect(function()
		local index = nextEmpty()
		if index then
			goTo(index)
		else
			hintLabel.Text = "Ответы даны на все задания."
		end
	end)

	UserInputService.InputBegan:Connect(function(inputObject: InputObject)
		if not frame.Visible or isLocked() then
			return
		end
		local key = inputObject.KeyCode
		if reference.isOpen() then
			if key == Enum.KeyCode.Escape then
				reference.close()
			end
			return
		end
		if confirmShade.Visible then
			if key == Enum.KeyCode.Escape then
				confirmShade.Visible = false
			end
			return
		end
		local typing = input:IsFocused()
		if key == Enum.KeyCode.PageDown or key == Enum.KeyCode.Tab then
			goTo(current + 1, typing)
		elseif key == Enum.KeyCode.PageUp then
			goTo(current - 1, typing)
		elseif not typing and key == Enum.KeyCode.Right then
			goTo(current + 1)
		elseif not typing and key == Enum.KeyCode.Left then
			goTo(current - 1)
		end
	end)

	submitButton.Activated:Connect(function()
		if isLocked() then
			return
		end
		flush()
		input:ReleaseFocus()
		local answered, flagged = 0, 0
		for index = 1, #tasks do
			if isAnswered(index) then
				answered += 1
			end
			if flags[index] then
				flagged += 1
			end
		end
		local lines = { string.format("Ответов дано: %d из %d.", answered, #tasks) }
		if answered < #tasks then
			table.insert(lines, string.format("Без ответа: %d.", #tasks - answered))
		end
		if flagged > 0 then
			table.insert(lines, string.format("Отмечено, чтобы вернуться: %d.", flagged))
		end
		table.insert(lines, "После сдачи изменить ответы будет нельзя.")
		confirmText.Text = table.concat(lines, "\n")
		confirmShade.Visible = true
	end)
	confirmNo.Activated:Connect(function()
		confirmShade.Visible = false
	end)
	confirmYes.Activated:Connect(function()
		if isLocked() then
			return
		end
		submitted = true
		setLocked("Работа сдана.\nЖдём, пока соперник закончит или выйдет время.")
		actions.submit()
	end)

	function screen.setRival(progress)
		local total = math.max(progress.total or 0, 1)
		rivalFill.Size = UDim2.fromScale(math.clamp((progress.answered or 0) / total, 0, 1), 1)
		if progress.left then
			rivalText.Text = "вышел из игры, победа за вами"
		elseif progress.submitted then
			rivalText.Text = string.format("сдал работу, ответов: %d из %d", progress.answered, progress.total)
		else
			rivalText.Text = string.format("ответил на %d из %d", progress.answered, progress.total)
		end
	end

	function screen.show(state)
		tasks = state.tasks
		answers = {}
		flags = {}
		current = 1
		submitted = false
		timeUp = false
		pending = nil
		lastBeepStage = 0
		endsAt = state.endsAt
		duration = state.endsAt - state.startedAt
		subjectName = Subjects.nameOf(state.subject)
		subjectId = state.subject
		referenceButton.Visible = Reference.hasMaterials(subjectId)
		reference.close()

		rivalPill.Text = string.format("%s · %s", state.rival.name, Subjects.nameOf(state.rival.subject))
		screen.setRival(state.rival)

		hintLabel.Text = "Enter или Tab: следующее\nPageUp, PageDown: листать"
		input.TextEditable = true
		confirmShade.Visible = false
		doneCover.Visible = false
		renderTask()
		frame.Visible = true
	end

	function screen.hide()
		frame.Visible = false
		input:ReleaseFocus()
		-- Скрытый экран не держит лишних объектов: рисунок и справочные материалы удаляются.
		reference.close()
		if figureFrame then
			figureFrame:Destroy()
			figureFrame = nil
		end
	end

	RunService.Heartbeat:Connect(function()
		if not frame.Visible then
			return
		end
		local remaining = endsAt - serverNow()
		timerLabel.Text = Ui.clock(remaining)

		-- Жёлтый за 5 минут до конца (за 2 минуты в коротком матче), красный за минуту.
		local warnAt = if duration > 600 then 300 else 120
		local stage = 0
		if remaining <= 60 then
			stage = 2
			timerLabel.TextColor3 = C.danger
		elseif remaining <= warnAt then
			stage = 1
			timerLabel.TextColor3 = C.warn
		else
			timerLabel.TextColor3 = C.ink
		end
		if stage > lastBeepStage then
			lastBeepStage = stage
			if not submitted then
				SoundService:PlayLocalSound(beep)
			end
		end

		if remaining <= 0 and not timeUp then
			timeUp = true
			if not submitted then
				setLocked("Время вышло.\nПроверяем работы…")
			end
		end
	end)

	return screen
end

return ExamScreen
