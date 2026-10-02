-- Точка входа клиента: получает состояние парты с сервера и показывает нужный экран.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Subjects = require(Shared.Subjects)
local Ui = require(script.Parent.Ui)
local SetupScreen = require(script.Parent.SetupScreen)
local ExamScreen = require(script.Parent.ExamScreen)
local ResultsScreen = require(script.Parent.ResultsScreen)
local ReviewScreen = require(script.Parent.ReviewScreen)
local Perf = require(script.Parent.Perf)

local player = Players.LocalPlayer
local remotes = ReplicatedStorage:WaitForChild("Remotes")
local stateEvent: RemoteEvent = remotes:WaitForChild("State")
local rivalEvent: RemoteEvent = remotes:WaitForChild("Rival")
local actionEvent: RemoteEvent = remotes:WaitForChild("Action")

local C = Ui.colors
local PANEL_WIDTH, PANEL_HEIGHT = 920, 620

local function send(action: string, payload: any?)
	actionEvent:FireServer(action, payload)
end

local gui = Ui.new("ScreenGui", {
	Name = "EgeDuel",
	ResetOnSpawn = false,
	IgnoreGuiInset = true,
	DisplayOrder = 10,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	Parent = player:WaitForChild("PlayerGui"),
})

local dim = Ui.frame({
	Size = UDim2.fromScale(1, 1),
	BackgroundColor3 = C.ink,
	BackgroundTransparency = 0.45,
	Visible = false,
	Parent = gui,
})

-- Панель фиксированного размера, которая масштабируется под экран: так интерфейс одинаков на ПК и телефоне.
local scale = Ui.new("UIScale")
local panel = Ui.frame({
	AnchorPoint = Vector2.new(0.5, 0.5),
	Position = UDim2.fromScale(0.5, 0.5),
	Size = UDim2.fromOffset(PANEL_WIDTH, PANEL_HEIGHT),
	BackgroundTransparency = 1,
	Parent = gui,
}, { scale })

local function updateScale()
	local camera = Workspace.CurrentCamera
	if not camera then
		return
	end
	local size = camera.ViewportSize
	-- Сверху экран занят кнопками Roblox, поэтому панель считается от высоты без этой полосы.
	local inset = GuiService:GetGuiInset()
	local height = size.Y - inset.Y
	scale.Scale = math.clamp(math.min(size.X / (PANEL_WIDTH + 40), height / (PANEL_HEIGHT + 24)), 0.3, 1.3)
	panel.Position = UDim2.new(0.5, 0, 0.5, inset.Y / 2)
end
updateScale()
if Workspace.CurrentCamera then
	Workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(updateScale)
end

local setup = SetupScreen.create(panel, {
	setSubject = function(id: string)
		send("setSubject", id)
	end,
	voteTime = function(minutes: number)
		send("voteTime", minutes)
	end,
	voteCount = function(count: number)
		send("voteCount", count)
	end,
	votePart = function(value: boolean)
		send("votePart", value)
	end,
	ready = function(value: boolean)
		send("ready", value)
	end,
	leave = function()
		send("leave")
	end,
})

local exam = ExamScreen.create(panel, {
	answer = function(index: number, value: string)
		send("answer", { index = index, value = value })
	end,
	submit = function()
		send("submit")
	end,
})

local review = ReviewScreen.create(panel, {
	grade = function(index: number, score: number)
		send("grade", { index = index, score = score })
	end,
	done = function()
		send("reviewDone")
	end,
})

local results = ResultsScreen.create(panel, {
	rematch = function()
		send("rematch")
	end,
	leave = function()
		send("leave")
	end,
})

-- Плашка ожидания соперника внизу экрана.
local waiting = Ui.frame({
	AnchorPoint = Vector2.new(0.5, 1),
	Position = UDim2.new(0.5, 0, 1, -24),
	Size = UDim2.fromOffset(460, 64),
	Visible = false,
	Parent = gui,
}, { Ui.corner(12), Ui.stroke(C.line, 1.5) })
local waitingText = Ui.label({
	Font = Ui.fonts.bold,
	Position = UDim2.fromOffset(18, 0),
	Size = UDim2.new(1, -170, 1, 0),
	Parent = waiting,
})
local waitingLeave = Ui.button("Встать", "plain", {
	Position = UDim2.new(1, -140, 0.5, -20),
	Size = UDim2.fromOffset(124, 40),
	Parent = waiting,
})
waitingLeave.Activated:Connect(function()
	send("leave")
end)

-- Кнопка тестового соперника. Сервер разрешает его только при запуске в Studio.
local waitingBot = Ui.button("Позвать тестового соперника (только в Studio)", "primary", {
	TextSize = 14,
	AnchorPoint = Vector2.new(0.5, 1),
	Position = UDim2.new(0.5, 0, 1, -96),
	Size = UDim2.fromOffset(460, 40),
	Visible = false,
	Parent = gui,
})
waitingBot.Activated:Connect(function()
	send("addBot")
end)

-- Отсчёт перед началом.
local countdown = Ui.frame({ Name = "Countdown", Size = UDim2.fromScale(1, 1), Visible = false, Parent = panel }, { Ui.corner(14) })
local countdownNumber = Ui.label({
	Font = Ui.fonts.display,
	TextSize = 150,
	TextColor3 = C.accent,
	TextXAlignment = Enum.TextXAlignment.Center,
	Position = UDim2.fromOffset(0, 90),
	Size = UDim2.new(1, 0, 0, 180),
	Parent = countdown,
})
local countdownInfo = Ui.label({
	TextSize = 20,
	TextXAlignment = Enum.TextXAlignment.Center,
	TextYAlignment = Enum.TextYAlignment.Top,
	Position = UDim2.fromOffset(40, 300),
	Size = UDim2.new(1, -80, 0, 260),
	Parent = countdown,
})
local countdownEndsAt = 0

RunService.Heartbeat:Connect(function()
	if countdown.Visible then
		local remaining = countdownEndsAt - Workspace:GetServerTimeNow()
		countdownNumber.Text = tostring(math.max(1, math.ceil(remaining)))
	end
end)

-- Во время матча прыжок отключён, чтобы случайно не встать из-за парты.
local jumpLocked = false
local function applyJumpLock()
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, not jumpLocked)
	end
end
player.CharacterAdded:Connect(function(character)
	character:WaitForChild("Humanoid")
	applyJumpLock()
end)

local function showOnly(name: string?)
	if name ~= "setup" then
		setup.hide()
	end
	if name ~= "exam" then
		exam.hide()
	end
	if name ~= "review" then
		review.hide()
	end
	if name ~= "results" then
		results.hide()
	end
	countdown.Visible = name == "countdown"
	waiting.Visible = name == "waiting"
	waitingBot.Visible = false
	dim.Visible = name == "setup" or name == "exam" or name == "review" or name == "results" or name == "countdown"

	jumpLocked = name == "exam" or name == "review" or name == "countdown"
	applyJumpLock()
	Perf.setPhase(name or "класс")
end

Perf.start()

stateEvent.OnClientEvent:Connect(function(state)
	local phase = state.phase
	if phase == "none" then
		showOnly(nil)
	elseif phase == "waiting" then
		-- Итоги прошлого матча остаются на экране, пока игрок сам не встанет.
		if not results.isVisible() then
			showOnly("waiting")
			waitingText.Text = string.format("Парта %d. Ждём соперника…", state.tableId)
			waitingBot.Visible = state.canAddBot == true
		end
	elseif phase == "setup" then
		showOnly("setup")
		setup.show(state)
	elseif phase == "countdown" then
		showOnly("countdown")
		countdownEndsAt = state.startsAt
		local lines = {
			string.format("Ваш предмет: %s", Subjects.nameOf(state.subject)),
			string.format("%s: %s", state.rivalName, Subjects.nameOf(state.rivalSubject)),
			"",
			string.format(
				"%s %d мин",
				if state.lotTime then "Жребий выбрал время:" else "Время на работу:",
				state.time
			),
			string.format(
				"%s %s",
				if state.lotCount then "Жребий выбрал задания первой части:" else "Задания первой части:",
				if state.count == 0 then "все" else tostring(state.count)
			),
			string.format(
				"%s %s",
				if state.lotPart then "Жребий решил:" else "Вторая часть:",
				if state.part then "вторая часть есть, развёрнутые ответы оценит соперник" else "без второй части"
			),
		}
		countdownInfo.Text = table.concat(lines, "\n")
	elseif phase == "exam" then
		showOnly("exam")
		exam.show(state)
	elseif phase == "review" then
		showOnly("review")
		review.show(state)
	elseif phase == "results" then
		showOnly("results")
		results.show(state)
	elseif phase == "resultsUpdate" then
		results.update(state)
	end
end)

rivalEvent.OnClientEvent:Connect(function(progress)
	exam.setRival(progress)
end)
