-- Клиентская часть автопроверки в Studio: осматривает класс, трогает интерактивные предметы,
-- проходит матч с тестовым соперником и проверяет экраны.
local LogService = game:GetService("LogService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local lines = {}

-- Режим снимков: сценарий задерживается на каждом экране, чтобы окно Studio успели снять.
local HOLD = if ReplicatedStorage:FindFirstChild("EgeTestHold") then 3 else 0

local function hold(seconds: number?)
	if HOLD > 0 then
		task.wait(seconds or HOLD)
	end
end

-- Ставит камеру в точку from и направляет на точку to (только в режиме снимков).
local function lookFrom(from: Vector3, to: Vector3)
	if HOLD == 0 then
		return
	end
	local camera = Workspace.CurrentCamera
	camera.CameraType = Enum.CameraType.Scriptable
	camera.CFrame = CFrame.lookAt(from, to)
	task.wait(HOLD)
	camera.CameraType = Enum.CameraType.Custom
end

-- Замер нагрузки по этапам. Частота кадров в Studio ограничена (60, а в неактивном окне 15),
-- поэтому главное здесь не она, а время процессора и видеокарты на кадр и самый долгий кадр.
local Stats = game:GetService("Stats")
local frames, since, cpuTime, gpuTime, worst = 0, os.clock(), 0, 0, 0
game:GetService("RunService").RenderStepped:Connect(function(dt)
	frames += 1
	cpuTime += Stats.RenderCPUFrameTime
	gpuTime += Stats.RenderGPUFrameTime
	worst = math.max(worst, dt)
end)
local function mark(label: string)
	local elapsed = os.clock() - since
	if elapsed > 0.5 and frames > 0 then
		table.insert(lines, string.format(
			"FPS %s: %.0f к/с, процессор %.1f мс на кадр, видеокарта %.1f мс, самый долгий кадр %.0f мс",
			label, frames / elapsed, cpuTime / frames * 1000, gpuTime / frames * 1000, worst * 1000
		))
	end
	frames, since, cpuTime, gpuTime, worst = 0, os.clock(), 0, 0, 0
end

local function check(name: string, condition: any)
	table.insert(lines, (if condition then "ok   " else "FAIL ") .. name)
end

local function waitFor(name: string, predicate: () -> any, timeout: number): boolean
	local deadline = os.clock() + timeout
	while os.clock() < deadline do
		local ok, value = pcall(predicate)
		if ok and value then
			check(name, true)
			return true
		end
		task.wait(0.2)
	end
	check(name, false)
	return false
end

local function findText(root: Instance, pattern: string): Instance?
	for _, item in root:GetDescendants() do
		if (item:IsA("TextLabel") or item:IsA("TextButton")) and string.find(item.Text, pattern) then
			return item
		end
	end
	return nil
end

local function countNamed(root: Instance, name: string): number
	local count = 0
	for _, item in root:GetDescendants() do
		if item.Name == name then
			count += 1
		end
	end
	return count
end

-- Нажимает подсказку «E» у предмета так же, как это сделал бы игрок.
local function press(part: Instance?): boolean
	local prompt = part and part:FindFirstChildOfClass("ProximityPrompt")
	if not prompt then
		return false
	end
	-- Подсказка срабатывает, только когда игрок рядом с предметом и видит его,
	-- поэтому подходим к предмету и поворачиваем к нему камеру.
	ReplicatedStorage:WaitForChild("EgeTestWalk"):FireServer(part)
	task.wait(1)
	local camera = Workspace.CurrentCamera
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if camera and root then
		camera.CameraType = Enum.CameraType.Scriptable
		camera.CFrame = CFrame.lookAt(root.Position + Vector3.new(0, 2, 0), part.Position)
	end
	task.wait(0.7)
	prompt:InputHoldBegin()
	task.wait(0.2)
	prompt:InputHoldEnd()
	task.wait(0.3)
	if camera then
		camera.CameraType = Enum.CameraType.Custom
	end
	return true
end

-- Нажимает подсказку и ждёт результата; при неудаче пробует ещё раз.
local function pressAndWait(name: string, part: Instance?, predicate: () -> any)
	for _ = 1, 3 do
		if not press(part) then
			break
		end
		local deadline = os.clock() + 2
		while os.clock() < deadline do
			local ok, value = pcall(predicate)
			if ok and value then
				check(name, true)
				return
			end
			task.wait(0.2)
		end
	end
	check(name, false)
end

local function checkClassroom()
	local classroom = Workspace:WaitForChild("Classroom", 20)
	check("класс построен", classroom ~= nil)
	if not classroom then
		return
	end
	check("окна на стенах: " .. countNamed(classroom, "Window"), countNamed(classroom, "Window") == 6)
	check("плакаты на стенах: " .. countNamed(classroom, "Poster"), countNamed(classroom, "Poster") == 8)
	check("книжные полки", countNamed(classroom, "Bookshelf") == 2)
	check("подвесные лампы", countNamed(classroom, "Lamp") == 6)
	check("настольные лампы на партах", countNamed(classroom, "DeskLampShade") == 6)

	local ceiling = classroom:FindFirstChild("Ceiling")
	check("над классом невидимый потолок", ceiling and ceiling.CanCollide and ceiling.Transparency == 1)
	local function rootPosition(): Vector3
		return player.Character.HumanoidRootPart.Position
	end
	local function inside(): boolean
		local position = rootPosition()
		return math.abs(position.X) < 42 and math.abs(position.Z) < 32 and position.Y > 0 and position.Y < 16
	end
	for name, point in { ["за стеной"] = Vector3.new(60, 5, 0), ["над классом"] = Vector3.new(0, 40, 0), ["под полом"] = Vector3.new(0, -30, 0) } do
		ReplicatedStorage:WaitForChild("EgeTestThrow"):FireServer(point)
		task.wait(0.3)
		waitFor("персонаж, оказавшийся " .. name .. ", возвращается в класс", inside, 4)
	end

	local scoreBoard = classroom:FindFirstChild("ScoreBoard")
	check("доска побед с текстом", scoreBoard and findText(scoreBoard, "Пока никто не сыграл") ~= nil)

	local clock = classroom:FindFirstChild("Clock")
	waitFor("часы показывают время", function()
		return clock and findText(clock, "^%d%d:%d%d$")
	end, 8)

	local globe = classroom:FindFirstChild("Globe")
	local before = globe and globe.CFrame
	pressAndWait("глобус показывает факт", globe, function()
		return globe.Bubble.Enabled and #globe.Bubble:FindFirstChildWhichIsA("TextLabel", true).Text > 10
	end)
	check("глобус вращается", globe and globe.CFrame ~= before)

	local switch = classroom:FindFirstChild("LightSwitch")
	local lamp = classroom:FindFirstChild("Lamp")
	pressAndWait("выключатель гасит лампы", switch, function()
		return lamp.PointLight.Enabled == false
	end)
	pressAndWait("выключатель снова включает лампы", switch, function()
		return lamp.PointLight.Enabled == true
	end)

	local daily = classroom:FindFirstChild("DailyTaskBoard")
	pressAndWait("на доске появилась задача", daily, function()
		return findText(daily, "Ответ появится через 20 секунд")
	end)

	local shelf = classroom:FindFirstChild("Bookshelf")
	local back = shelf and shelf:FindFirstChild("Back")
	check("подсказка у книжной полки рисуется поверх стены", back and back.Bubble.AlwaysOnTop)
	local door, doorFrame = classroom:FindFirstChild("Door"), classroom:FindFirstChild("DoorFrame")
	check("дверь выступает из стены и рамы", door and doorFrame
		and door.Position.Z - door.Size.Z / 2 < doorFrame.Position.Z - doorFrame.Size.Z / 2 - 0.1)
	pressAndWait("книжная полка показывает факт", back, function()
		return back.Bubble.Enabled
	end)
	local bell = classroom:FindFirstChild("Bell")
	local rest = bell and bell.CFrame
	pressAndWait("звонок звенит и качается", bell, function()
		return bell.CFrame ~= rest
	end)
end

local function checkFigureModule(gui: Instance)
	local scripts = player:WaitForChild("PlayerScripts")
	local module = scripts:FindFirstChild("Figure", true)
	check("модуль рисунков найден", module ~= nil)
	if not module then
		return
	end
	local Figure = require(module)
	local holder = Instance.new("Frame")
	holder.Visible = false
	holder.Parent = gui
	local frame = Figure.render({
		w = 200,
		h = 100,
		items = {
			{ "line", 0, 0, 100, 50, 0 },
			{ "line", 0, 50, 100, 0, 2 },
			{ "rect", 10, 10, 20, 30, 2 },
			{ "circle", 50, 50, 8, 1 },
			{ "text", 50, 50, "А", "c" },
		},
	}, holder)
	local shapes = 0
	if frame then
		for _, child in frame:GetChildren() do
			if child:IsA("GuiObject") then
				shapes += 1
			end
		end
	end
	check("рисунок из 5 фигур построен, фигур: " .. shapes, shapes == 5)
	check("без рисунка модуль возвращает пусто", Figure.render(nil, holder) == nil)
	holder:Destroy()
end

-- Справочные материалы: окно строится напрямую, как при нажатии кнопки на экзамене.
local function checkReference(gui: Instance)
	local module = player.PlayerScripts:FindFirstChild("Reference", true)
	check("модуль справочных материалов найден", module ~= nil)
	if not module then
		return
	end
	local Reference = require(module)
	local holder = Instance.new("Frame")
	holder.Size = UDim2.fromOffset(920, 620)
	holder.Visible = false
	holder.Parent = gui
	local panel = Reference.create(holder)
	local body = holder.Reference.Body

	check("справочные материалы есть у химии, физики, математики и географии", Reference.hasMaterials("chemistry")
		and Reference.hasMaterials("physics") and Reference.hasMaterials("math_base")
		and Reference.hasMaterials("math_prof") and Reference.hasMaterials("geography"))
	check("у русского языка справочных материалов нет", not Reference.hasMaterials("russian"))

	panel.open("chemistry")
	local cells, places, symbols = 0, {}, {}
	local overlap = false
	for _, cell in body.Content:GetChildren() do
		if cell:IsA("Frame") then
			cells += 1
			local key = cell.Position.X.Offset .. ":" .. cell.Position.Y.Offset
			overlap = overlap or places[key] ~= nil
			places[key] = true
			for _, label in cell:GetChildren() do
				symbols[label.Text] = true
			end
		end
	end
	check("таблица Менделеева: 118 клеток, клеток: " .. cells, cells == 118)
	check("таблица Менделеева: клетки не накладываются", not overlap)
	check("таблица Менделеева: есть H, Fe, Cl с массой 35,5 и Og", symbols["H"] and symbols["Fe"] and symbols["35,5"] and symbols["Og"])
	check("у химии три вкладки", holder.Reference:FindFirstChild("Tab3", true) ~= nil)

	panel.open("physics")
	check("физика: справочные данные показаны", findText(body, "постоянная Больцмана") ~= nil)
	panel.open("math_prof")
	check("математика, профиль: формулы показаны", findText(body, "sin 2α") ~= nil)
	panel.open("geography")
	local display = body:FindFirstChild("Display", true)
	check("география: калькулятор показан", display ~= nil and body:FindFirstChild("Key=", true) ~= nil)
	panel.close()
	check("после закрытия содержимое удалено", body:FindFirstChild("Content") == nil)
	holder:Destroy()
end

local function run()
	local remotes = ReplicatedStorage:WaitForChild("Remotes", 20)
	check("сервер создал Remotes", remotes ~= nil)
	local gui = player:WaitForChild("PlayerGui"):WaitForChild("EgeDuel", 20)
	check("клиент создал интерфейс EgeDuel", gui ~= nil)
	if not remotes or not gui then
		return
	end
	if not player.Character then
		player.CharacterAdded:Wait()
	end
	task.wait(2)

	lookFrom(Vector3.new(0, 11, 30), Vector3.new(0, 6, -32)) -- вид на доски
	lookFrom(Vector3.new(0, 11, -28), Vector3.new(0, 6, 32)) -- вид на заднюю стену
	lookFrom(Vector3.new(30, 9, 8), Vector3.new(-42, 8, -6)) -- вид на боковую стену с окнами
	lookFrom(Vector3.new(-8, 9, -12), Vector3.new(-25, 5, -27)) -- учительский стол и глобус
	mark("загрузка")
	task.wait(3)
	mark("класс, игрок стоит")
	checkClassroom()
	mark("класс, осмотр предметов")
	checkFigureModule(gui)
	checkReference(gui)
	mark("справочные материалы")

	local action = remotes:WaitForChild("Action")
	local setup = gui:FindFirstChild("Setup", true)
	local exam = gui:FindFirstChild("Exam", true)
	local results = gui:FindFirstChild("Results", true)
	local countdown = gui:FindFirstChild("Countdown", true)
	check("экраны созданы", setup and exam and results and countdown)
	if not (setup and exam and results and countdown) then
		return
	end

	local botButton = findText(gui, "тестового соперника")
	check("есть кнопка тестового соперника", botButton ~= nil)

	-- Садимся через подсказку у стула; если из сценария она не срабатывает, сажает сервер.
	local seat = Workspace.Classroom.Table1.SeatA
	press(seat)
	local seatedByPrompt = waitFor("посадка через подсказку «Сесть» у стула", function()
		return botButton.Visible
	end, 5)
	if not seatedByPrompt then
		ReplicatedStorage:WaitForChild("EgeTestSeat"):FireServer()
		if not waitFor("посадка за парту (запасной путь)", function()
			return botButton.Visible
		end, 10) then
			return
		end
	end
	check("табличка парты: ждёт соперника", findText(Workspace.Classroom.Table1, "Ждёт соперника") ~= nil)
	mark("посадка")
	task.wait(2)
	mark("за партой, ожидание")

	action:FireServer("addBot")
	if not waitFor("экран настройки открылся", function()
		return setup.Visible
	end, 10) then
		return
	end
	check("в настройке показан соперник", findText(setup, "Тестовый соперник") ~= nil)
	action:FireServer("setSubject", "math_base")
	action:FireServer("voteTime", 10)
	action:FireServer("voteCount", 20)
	task.wait(1)
	check("кнопка «Готов» на экране настройки", findText(setup, "^Готов$") ~= nil)
	mark("экран настройки")
	hold()
	action:FireServer("ready", true)

	waitFor("отсчёт показан", function()
		return countdown.Visible
	end, 5)
	check("в отсчёте указан предмет", findText(countdown, "Математика, база") ~= nil)
	if not waitFor("экран экзамена открылся", function()
		return exam.Visible
	end, 12) then
		return
	end

	mark("отсчёт")
	task.wait(3)
	mark("экран экзамена")
	check("в шапке предмет и номер задания", findText(exam, "задание 1 из 20") ~= nil)
	check("таймер идёт", findText(exam, "^%d%d:%d%d$") ~= nil)
	check("кнопка «Сдать работу» стоит в шапке", exam:FindFirstChild("Submit", true) and exam:FindFirstChild("Submit", true).Parent ~= exam)
	check("окно подтверждения сдачи закрыто", exam:FindFirstChild("Confirm") and not exam.Confirm.Visible)
	check("у математики есть кнопка справочных материалов", exam:FindFirstChild("ReferenceButton") and exam.ReferenceButton.Visible)
	check("стрелки листания и кнопка «К заданию без ответа»", exam:FindFirstChild("Prev") and exam:FindFirstChild("Next") and exam:FindFirstChild("NextEmpty"))
	check("в навигаторе 20 номеров", exam:FindFirstChild("Nav20") and exam.Nav20.Visible)
	local taskText = exam:FindFirstChild("TaskText", true)
	check("текст задания показан", taskText and #taskText.Text > 15)
	check("лампа на парте горит во время экзамена", Workspace.Classroom.Table1.DeskLampShade.PointLight.Enabled)

	local input = exam:FindFirstChildWhichIsA("TextBox", true)
	check("поле ответа есть", input ~= nil)
	if input then
		local function shown(): string
			local parts = {}
			for _, cell in input.Parent:GetChildren() do
				if cell:IsA("TextLabel") and cell.Text ~= "" then
					table.insert(parts, cell.Text)
				end
			end
			return table.concat(parts, "|")
		end
		input.Text = "ёж 2"
		task.wait(0.6)
		check("клетки показывают ответ заглавными: " .. shown(), shown() == "Ё|Ж| |2")
		input.Text = string.rep("я", 30)
		task.wait(0.3)
		check("ответ обрезан до 17 символов", utf8.len(input.Text) == 17)
		input.Text = "0.5"
		task.wait(0.6)
		check("точка заменена на запятую: " .. shown(), shown() == "0|,|5")
	end

	waitFor("виден прогресс соперника", function()
		return findText(exam, "ответил на %d+ из 20")
	end, 12)
	hold()

	action:FireServer("submit")
	if not waitFor("экран итогов открылся", function()
		return results.Visible
	end, 10) then
		return
	end
	mark("экзамен, ввод ответа")
	task.wait(3)
	mark("экран итогов")
	local cards = 0
	for _, item in results:GetDescendants() do
		if item:IsA("TextLabel") and string.find(item.Text, "^Верных ответов: %d+ из 20$") then
			cards += 1
		end
	end
	check("в итогах число верных ответов у обоих игроков", cards == 2)
	check("в итогах есть исход", findText(results, "^Победа$") or findText(results, "^Поражение$") or findText(results, "^Ничья$"))
	check("в итогах есть проценты", findText(results, "^%d+%%$") ~= nil)
	local list = results:FindFirstChildWhichIsA("ScrollingFrame")
	local rows = 0
	if list then
		for _, item in list:GetChildren() do
			if item:IsA("Frame") then
				rows += 1
			end
		end
	end
	check("разбор ошибок показан, строк: " .. rows, rows >= 19)
	check("в разборе ответ с запятой", findText(results, "ваш ответ: 0,5") ~= nil)
	check("разбор содержит верный ответ", findText(results, "верно: ") ~= nil)
	local figures = countNamed(results, "Figure")
	check("в разборе нарисованы рисунки заданий: " .. figures, figures >= 3)
	check("соперник согласен на реванш", findText(results, "Принять реванш") ~= nil)
	check("лампа на парте погасла после экзамена", not Workspace.Classroom.Table1.DeskLampShade.PointLight.Enabled)
	hold(5)

	action:FireServer("rematch")
	waitFor("реванш: снова экран настройки, предмет можно сменить", function()
		return setup.Visible
	end, 5)
	action:FireServer("setSubject", "chemistry")
	task.wait(0.5)
	action:FireServer("ready", true)
	waitFor("реванш: отсчёт", function()
		return countdown.Visible
	end, 5)
	check("реванш: выбран новый предмет", findText(countdown, "Химия") ~= nil)
	waitFor("реванш: экзамен", function()
		return exam.Visible
	end, 10)
	task.wait(1)
	check("у химии есть кнопка справочных материалов", exam.ReferenceButton.Visible)
	mark("реванш, экзамен")
	action:FireServer("submit")
	waitFor("реванш: итоги", function()
		return results.Visible
	end, 10)

	action:FireServer("leave")
	waitFor("после «Встать» экраны закрыты", function()
		return not results.Visible and not setup.Visible and not exam.Visible
	end, 5)
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	waitFor("персонаж встал со стула", function()
		return humanoid and not humanoid.Sit
	end, 5)
end

-- Режим снимков: показывает экран экзамена с заданиями-образцами (символы и рисунки).
local function showSamples()
	if HOLD == 0 then
		return
	end
	local gui = player.PlayerGui:FindFirstChild("EgeDuel")
	local panel = gui and gui:FindFirstChild("Exam", true) and gui:FindFirstChild("Exam", true).Parent
	local module = player.PlayerScripts:FindFirstChild("ExamScreen", true)
	if not panel or not module then
		return
	end
	-- Справочные материалы: показываем каждую вкладку по очереди.
	local referenceModule = player.PlayerScripts:FindFirstChild("Reference", true)
	if referenceModule then
		local reference = require(referenceModule).create(panel)
		for _, subject in { "chemistry", "physics", "math_base", "geography" } do
			reference.open(subject)
			task.wait(3)
		end
		reference.close()
	end
	if ReplicatedStorage:FindFirstChild("EgeTestHold") and ReplicatedStorage.EgeTestHold.Value then
		return -- короткий режим снимков: только справочные материалы
	end

	local tasks = ReplicatedStorage:WaitForChild("EgeTestSamples"):InvokeServer()
	local noop = function() end
	local preview = require(module).create(panel, { answer = noop, submit = noop })
	local now = Workspace:GetServerTimeNow()
	for index, sample in tasks do
		preview.show({
			subject = "math_prof",
			startedAt = now,
			endsAt = now + 900,
			tasks = { sample, sample, sample, sample, sample, sample, sample, sample },
			rival = { name = "Образец " .. index, subject = "physics", answered = 3, total = 8, submitted = false, left = false },
		})
		task.wait(2.5)
	end
	preview.hide()
end

local ok, message = pcall(run)
pcall(showSamples)
if not ok then
	table.insert(lines, "FAIL сценарий упал: " .. tostring(message))
end
for _, entry in LogService:GetLogHistory() do
	if entry.messageType == Enum.MessageType.MessageError then
		table.insert(lines, "CLIENT ERROR: " .. entry.message)
	end
end
ReplicatedStorage:WaitForChild("EgeTestReport"):FireServer(table.concat(lines, "\n"))
