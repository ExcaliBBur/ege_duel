-- Строит класс кодом при запуске сервера: комната, окна, доски, плакаты, мебель, парты
-- и интерактивные предметы (глобус, книжные полки, выключатель, звонок, доска «Задача дня»).
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")

local World = {}

local COLORS = {
	floor = Color3.fromRGB(196, 164, 124),
	rug = Color3.fromRGB(120, 36, 70),
	wall = Color3.fromRGB(244, 240, 232),
	panel = Color3.fromRGB(86, 122, 118),
	trim = Color3.fromRGB(250, 250, 250),
	beam = Color3.fromRGB(110, 82, 58),
	glass = Color3.fromRGB(170, 215, 240),
	table = Color3.fromRGB(176, 132, 92),
	wood = Color3.fromRGB(128, 92, 62),
	leg = Color3.fromRGB(90, 84, 96),
	seatA = Color3.fromRGB(184, 21, 90),
	seatB = Color3.fromRGB(13, 118, 128),
	board = Color3.fromRGB(34, 60, 48),
	ink = Color3.fromRGB(27, 20, 32),
	paper = Color3.fromRGB(255, 255, 255),
	active = Color3.fromRGB(184, 21, 90),
	lampOn = Color3.fromRGB(255, 232, 170),
	lampOff = Color3.fromRGB(150, 146, 140),
	plant = Color3.fromRGB(58, 138, 72),
	pot = Color3.fromRGB(170, 96, 60),
	ocean = Color3.fromRGB(46, 120, 190),
	brass = Color3.fromRGB(200, 160, 60),
}

local BOOK_COLORS = {
	Color3.fromRGB(184, 21, 90),
	Color3.fromRGB(13, 118, 128),
	Color3.fromRGB(214, 160, 40),
	Color3.fromRGB(60, 90, 160),
	Color3.fromRGB(90, 150, 80),
	Color3.fromRGB(150, 70, 50),
}

local POSTERS = {
	{ text = "a² + b² = c²\nтеорема Пифагора", color = Color3.fromRGB(251, 227, 237) },
	{ text = "ЖИ, ШИ пиши с буквой И\nЧА, ЩА пиши с буквой А", color = Color3.fromRGB(221, 241, 242) },
	{ text = "F = m · a\nвторой закон Ньютона", color = Color3.fromRGB(251, 239, 211) },
	{ text = "H₂O   CO₂   NaCl   O₂\nхимия вокруг нас", color = Color3.fromRGB(223, 243, 231) },
	{ text = "1 байт = 8 бит\n1 Кбайт = 1024 байта", color = Color3.fromRGB(230, 228, 250) },
	{ text = "988 · 1242 · 1380 · 1812 · 1861 · 1961\nдаты, которые стоит помнить", color = Color3.fromRGB(251, 227, 237) },
	{ text = "sin²α + cos²α = 1\nосновное тригонометрическое тождество", color = Color3.fromRGB(221, 241, 242) },
	{ text = "be · was / were · been\ngo · went · gone", color = Color3.fromRGB(251, 239, 211) },
}

local GLOBE_FACTS = {
	"Байкал содержит около пятой части всей незамёрзшей пресной воды планеты.",
	"Россия расположена в 11 часовых зонах.",
	"Тихий океан больше, чем вся суша Земли вместе взятая.",
	"Сахара по площади сравнима с Китаем.",
	"Самая высокая вершина России, Эльбрус, поднимается на 5642 метра.",
	"Экватор пересекает три материка: Африку, Южную Америку и острова Азии.",
	"Марианская впадина глубже, чем высота Эвереста.",
	"Антарктида это самый высокий материк: её средняя высота больше двух километров.",
}

local BOOK_FACTS = {
	"Онегинская строфа состоит из 14 строк, как и сонет.",
	"Гоголь назвал «Мёртвые души» поэмой, хотя они написаны прозой.",
	"ДНК человека на 99,9% одинакова у всех людей.",
	"Ноль не является ни положительным, ни отрицательным числом.",
	"Слово «робот» придумал чешский писатель Карел Чапек в 1920 году.",
	"В сердце человека четыре камеры, а у лягушки три.",
	"Звук в воздухе проходит примерно 340 метров за секунду.",
	"В русском алфавите 33 буквы, из них 10 гласных.",
	"Первым программистом считают Аду Лавлейс, она жила в XIX веке.",
}

local function newPart(parent: Instance, name: string, size: Vector3, cframe: CFrame, color: Color3, material: Enum.Material?): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.Size = size
	part.CFrame = cframe
	part.Color = color
	part.Material = material or Enum.Material.SmoothPlastic
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = parent
	return part
end

local function newPrompt(part: BasePart, actionText: string, objectText: string): ProximityPrompt
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = actionText
	prompt.ObjectText = objectText
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	return prompt
end

local function newSound(parent: Instance, soundId: string, volume: number, speed: number?): Sound
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = volume
	sound.PlaybackSpeed = speed or 1
	sound.RollOffMaxDistance = 80
	sound.Parent = parent
	return sound
end

-- Надписи на грани детали. Возвращает SurfaceGui.
local function newSurface(part: BasePart, face: Enum.NormalId): SurfaceGui
	local gui = Instance.new("SurfaceGui")
	gui.Face = face
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 40
	gui.Parent = part
	return gui
end

local function newText(parent: Instance, text: string, size: UDim2, position: UDim2, color: Color3, font: Enum.Font?): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Size = size
	label.Position = position
	label.Font = font or Enum.Font.GothamBold
	label.Text = text
	label.TextColor3 = color
	label.TextScaled = true
	label.TextWrapped = true
	label.Parent = parent
	return label
end

-- Всплывающая подпись над предметом. Возвращает функцию показа текста на несколько секунд.
-- toward: сдвиг подписи в сторону комнаты, чтобы она не уходила в стену за предметом.
local function newBubble(part: BasePart, height: number, toward: Vector3?): (string) -> ()
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "Bubble"
	billboard.Size = UDim2.fromOffset(340, 96)
	billboard.StudsOffsetWorldSpace = Vector3.new(0, height, 0) + (toward or Vector3.zero)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 60
	billboard.Enabled = false
	billboard.Parent = part

	local frame = Instance.new("Frame")
	frame.Size = UDim2.fromScale(1, 1)
	frame.BackgroundColor3 = COLORS.paper
	frame.BorderSizePixel = 0
	frame.Parent = billboard
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = frame
	local stroke = Instance.new("UIStroke")
	stroke.Thickness = 2
	stroke.Color = COLORS.active
	stroke.Parent = frame

	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Size = UDim2.new(1, -20, 1, -12)
	label.Position = UDim2.fromOffset(10, 6)
	label.Font = Enum.Font.GothamMedium
	label.TextSize = 16
	label.TextWrapped = true
	label.TextColor3 = COLORS.ink
	label.Parent = frame

	local token = 0
	return function(text: string)
		token += 1
		local mine = token
		label.Text = text
		billboard.Enabled = true
		task.delay(7, function()
			if token == mine then
				billboard.Enabled = false
			end
		end)
	end
end

-- Выдаёт факты по кругу в случайном порядке, чтобы они не повторялись подряд.
local function factCycle(facts: { string }): () -> string
	local order, position = {}, 0
	return function(): string
		if position >= #order then
			order = table.clone(facts)
			for index = #order, 2, -1 do
				local other = math.random(index)
				order[index], order[other] = order[other], order[index]
			end
			position = 0
		end
		position += 1
		return order[position]
	end
end

-- Стена вдоль оси X (север и юг) или Z (запад и восток) с панелью внизу и плинтусом.
local function buildWall(parent: Instance, name: string, center: Vector3, length: number, alongX: boolean, inward: Vector3)
	local function size(thickness: number, height: number): Vector3
		return if alongX then Vector3.new(length, height, thickness) else Vector3.new(thickness, height, length)
	end
	newPart(parent, name, size(1, 16), CFrame.new(center.X, 8, center.Z), COLORS.wall)
	local panelAt = center + inward * 0.6
	newPart(parent, name .. "Panel", size(0.2, 4.5), CFrame.new(panelAt.X, 2.25, panelAt.Z), COLORS.panel)
	local trimAt = center + inward * 0.65
	newPart(parent, name .. "Trim", size(0.3, 0.35), CFrame.new(trimAt.X, 4.65, trimAt.Z), COLORS.trim)
end

local function buildWindow(parent: Instance, x: number, z: number, inward: Vector3)
	local at = Vector3.new(x, 9.5, z) + inward * 0.55
	local glass = newPart(parent, "Window", Vector3.new(0.15, 6.5, 9), CFrame.new(at), COLORS.glass, Enum.Material.Glass)
	glass.Transparency = 0.35
	glass.Reflectance = 0.15
	local frameAt = at + inward * 0.05
	newPart(parent, "WindowTop", Vector3.new(0.3, 0.4, 9.8), CFrame.new(frameAt.X, 12.95, frameAt.Z), COLORS.trim)
	newPart(parent, "WindowSill", Vector3.new(0.9, 0.4, 10.2), CFrame.new(frameAt.X + inward.X * 0.3, 6.05, frameAt.Z), COLORS.trim)
	newPart(parent, "WindowLeft", Vector3.new(0.3, 7.3, 0.4), CFrame.new(frameAt.X, 9.5, frameAt.Z - 4.7), COLORS.trim)
	newPart(parent, "WindowRight", Vector3.new(0.3, 7.3, 0.4), CFrame.new(frameAt.X, 9.5, frameAt.Z + 4.7), COLORS.trim)
	newPart(parent, "WindowBar", Vector3.new(0.25, 6.5, 0.25), CFrame.new(frameAt.X, 9.5, frameAt.Z), COLORS.trim)
	newPart(parent, "WindowCross", Vector3.new(0.25, 0.25, 9), CFrame.new(frameAt.X, 9.5, frameAt.Z), COLORS.trim)
end

local function buildPoster(parent: Instance, size: Vector3, cframe: CFrame, face: Enum.NormalId, poster)
	local part = newPart(parent, "Poster", size, cframe, poster.color)
	local gui = newSurface(part, face)
	newText(gui, poster.text, UDim2.fromScale(0.9, 0.84), UDim2.fromScale(0.05, 0.08), COLORS.ink)
end

local function buildPlant(parent: Instance, x: number, z: number)
	newPart(parent, "Pot", Vector3.new(2.2, 2, 2.2), CFrame.new(x, 1, z), COLORS.pot)
	for index, offset in { Vector3.new(0, 3.4, 0), Vector3.new(0.7, 4.4, 0.3), Vector3.new(-0.6, 4.6, -0.4), Vector3.new(0.1, 5.5, 0) } do
		local leaf = newPart(parent, "Leaves" .. index, Vector3.new(2.6, 2.6, 2.6), CFrame.new(x + offset.X, offset.Y, z + offset.Z), COLORS.plant, Enum.Material.Grass)
		leaf.Shape = Enum.PartType.Ball
	end
end

local function buildBookshelf(parent: Instance, x: number, z: number): Part
	local model = Instance.new("Model")
	model.Name = "Bookshelf"
	model.Parent = parent
	local back = newPart(model, "Back", Vector3.new(8, 9, 0.4), CFrame.new(x, 4.5, z + 0.8), COLORS.wood, Enum.Material.Wood)
	newPart(model, "SideLeft", Vector3.new(0.4, 9, 2), CFrame.new(x - 4, 4.5, z), COLORS.wood, Enum.Material.Wood)
	newPart(model, "SideRight", Vector3.new(0.4, 9, 2), CFrame.new(x + 4, 4.5, z), COLORS.wood, Enum.Material.Wood)
	for level = 0, 3 do
		local y = 0.2 + level * 2.9
		newPart(model, "Shelf", Vector3.new(8, 0.3, 2), CFrame.new(x, y, z), COLORS.wood, Enum.Material.Wood)
		if level < 3 then
			local cursor = x - 3.6
			while cursor < x + 3.2 do
				local width = 0.3 + math.random() * 0.4
				local height = 1.5 + math.random() * 0.9
				newPart(
					model,
					"Book",
					Vector3.new(width, height, 1.3),
					CFrame.new(cursor + width / 2, y + 0.15 + height / 2, z),
					BOOK_COLORS[math.random(#BOOK_COLORS)]
				)
				cursor += width + 0.05
			end
		end
	end
	return back
end

local function buildRoom(parent: Instance)
	newPart(parent, "Floor", Vector3.new(84, 1, 64), CFrame.new(0, -0.5, 0), COLORS.floor, Enum.Material.WoodPlanks)
	newPart(parent, "Rug", Vector3.new(10, 0.1, 40), CFrame.new(0, 0.05, 4), COLORS.rug, Enum.Material.Fabric)

	buildWall(parent, "WallNorth", Vector3.new(0, 0, -32.5), 84, true, Vector3.new(0, 0, 1))
	buildWall(parent, "WallSouth", Vector3.new(0, 0, 32.5), 84, true, Vector3.new(0, 0, -1))
	buildWall(parent, "WallWest", Vector3.new(-42.5, 0, 0), 66, false, Vector3.new(1, 0, 0))
	buildWall(parent, "WallEast", Vector3.new(42.5, 0, 0), 66, false, Vector3.new(-1, 0, 0))

	for _, z in { -20, 0, 20 } do
		buildWindow(parent, -42, z, Vector3.new(1, 0, 0))
		buildWindow(parent, 42, z, Vector3.new(-1, 0, 0))
	end

	-- Плакаты между окнами на боковых стенах и на задней стене.
	local sideSpots = { -10, 10 }
	for index, z in sideSpots do
		buildPoster(parent, Vector3.new(0.2, 4.6, 6.4), CFrame.new(-41.85, 9.6, z), Enum.NormalId.Right, POSTERS[index])
		buildPoster(parent, Vector3.new(0.2, 4.6, 6.4), CFrame.new(41.85, 9.6, z), Enum.NormalId.Left, POSTERS[index + 2])
	end
	for index, x in { -27, -16, 16, 27 } do
		buildPoster(parent, Vector3.new(7.4, 4.6, 0.2), CFrame.new(x, 10.6, 31.85), Enum.NormalId.Front, POSTERS[index + 4])
	end

	-- Невидимый потолок: со шкафа или парты нельзя перепрыгнуть через стену.
	local ceiling = newPart(parent, "Ceiling", Vector3.new(86, 1, 66), CFrame.new(0, 16.7, 0), COLORS.wall)
	ceiling.Transparency = 1
	ceiling.CastShadow = false

	-- Балки под потолком: к ним подвешены лампы.
	for _, z in { -10, 14 } do
		newPart(parent, "Beam", Vector3.new(84, 0.8, 1), CFrame.new(0, 15.6, z), COLORS.beam, Enum.Material.Wood)
	end
	for _, x in { -24, 0, 24 } do
		newPart(parent, "CrossBeam", Vector3.new(1, 0.6, 64), CFrame.new(x, 15.9, 0), COLORS.beam, Enum.Material.Wood)
	end

	-- Дверь на задней стене.
	newPart(parent, "Door", Vector3.new(5, 9, 0.6), CFrame.new(0, 4.5, 31.6), COLORS.wood, Enum.Material.Wood)
	newPart(parent, "DoorFrame", Vector3.new(5.8, 9.4, 0.4), CFrame.new(0, 4.7, 31.75), COLORS.trim)
	newPart(parent, "DoorKnob", Vector3.new(0.5, 0.5, 0.5), CFrame.new(1.8, 4.4, 31.15), COLORS.brass, Enum.Material.Metal).Shape =
		Enum.PartType.Ball

	buildPlant(parent, -39, -29)
	buildPlant(parent, 39, -29)
	buildPlant(parent, -39, 27)
	buildPlant(parent, 39, 27)

	local spawn = Instance.new("SpawnLocation")
	spawn.Name = "Spawn"
	spawn.Anchored = true
	spawn.Size = Vector3.new(10, 1, 6)
	spawn.CFrame = CFrame.new(0, 0.05, 25)
	spawn.Transparency = 1
	spawn.CanCollide = false
	spawn.Neutral = true
	spawn.Parent = parent

	Lighting.ClockTime = 14
	Lighting.Brightness = 2
	Lighting.Ambient = Color3.fromRGB(130, 126, 134)
end

-- Доска с заголовком и текстом. Возвращает надпись с текстом.
local function buildBoard(parent: Instance, name: string, x: number, width: number, title: string): (Part, TextLabel)
	newPart(parent, name .. "Frame", Vector3.new(width + 0.8, 9.8, 0.3), CFrame.new(x, 9.5, -31.85), COLORS.wood, Enum.Material.Wood)
	local board = newPart(parent, name, Vector3.new(width, 9, 0.3), CFrame.new(x, 9.5, -31.7), COLORS.board)
	local gui = newSurface(board, Enum.NormalId.Back)
	newText(gui, title, UDim2.fromScale(0.9, 0.2), UDim2.fromScale(0.05, 0.04), COLORS.paper, Enum.Font.GothamBlack)
	local body = newText(gui, "", UDim2.fromScale(0.9, 0.68), UDim2.fromScale(0.05, 0.28), COLORS.paper, Enum.Font.GothamMedium)
	body.TextYAlignment = Enum.TextYAlignment.Top
	return board, body
end

-- Доска «Задача дня»: по нажатию показывает случайное задание из банка, через 20 секунд ответ.
local function buildDailyTask(parent: Instance, randomTask: (() -> any)?)
	local board, body = buildBoard(parent, "DailyTaskBoard", 28, 20, "ЗАДАЧА ДНЯ")
	body.TextXAlignment = Enum.TextXAlignment.Left
	body.Text = "Подойдите к доске и нажмите E, чтобы получить задачу."
	local prompt = newPrompt(board, "Новая задача", "Задача дня")
	prompt.MaxActivationDistance = 16

	local token = 0
	prompt.Triggered:Connect(function()
		local picked = randomTask and randomTask()
		if not picked then
			body.Text = "Банк заданий пуст."
			return
		end
		token += 1
		local mine = token
		body.Text = string.format("%s\n\n%s\n\nОтвет появится через 20 секунд.", picked.subject, picked.task.text)
		task.delay(20, function()
			if token == mine then
				body.Text = string.format(
					"%s\n\n%s\n\nОтвет: %s\n%s",
					picked.subject,
					picked.task.text,
					picked.task.answers[1],
					picked.task.explanation
				)
			end
		end)
	end)
end

local function buildTeacherCorner(parent: Instance)
	newPart(parent, "TeacherDesk", Vector3.new(12, 0.5, 4.5), CFrame.new(-22, 3.4, -25), COLORS.wood, Enum.Material.Wood)
	newPart(parent, "TeacherDeskFront", Vector3.new(12, 3.1, 0.4), CFrame.new(-22, 1.6, -23), COLORS.wood, Enum.Material.Wood)
	for _, dx in { -5.6, 5.6 } do
		newPart(parent, "TeacherDeskSide", Vector3.new(0.4, 3.1, 4.5), CFrame.new(-22 + dx, 1.6, -25), COLORS.wood, Enum.Material.Wood)
	end

	-- Глобус: его можно покрутить и узнать факт.
	newPart(parent, "GlobeStand", Vector3.new(1.4, 0.3, 1.4), CFrame.new(-25, 3.8, -25), COLORS.brass, Enum.Material.Metal)
	newPart(parent, "GlobeAxis", Vector3.new(0.2, 1, 0.2), CFrame.new(-25, 4.4, -25), COLORS.brass, Enum.Material.Metal)
	local globe = newPart(parent, "Globe", Vector3.new(2.8, 2.8, 2.8), CFrame.new(-25, 6.1, -25), COLORS.ocean)
	globe.Shape = Enum.PartType.Ball
	local landSpots = {
		{ Vector3.new(0.9, 0.5, 0.8), 1.2 },
		{ Vector3.new(-0.8, 0.2, 0.95), 1 },
		{ Vector3.new(0.3, -0.6, -1.05), 1.1 },
		{ Vector3.new(-1.05, -0.4, -0.5), 0.9 },
		{ Vector3.new(0.2, 1.15, -0.3), 0.8 },
	}
	local lands = {}
	for index, spot in landSpots do
		local land = newPart(parent, "GlobeLand" .. index, Vector3.one * spot[2], globe.CFrame * CFrame.new(spot[1]), COLORS.plant)
		land.Shape = Enum.PartType.Ball
		land.CanCollide = false
		lands[index] = { part = land, offset = CFrame.new(spot[1]) }
	end

	-- Глобус вращается только несколько секунд после толчка. В покое детали не двигаются,
	-- и серверу нечего рассылать игрокам.
	local angle = 0
	local base = globe.CFrame
	local spinning = false
	local speed = 0
	local function spin()
		speed = 9
		if spinning then
			return
		end
		spinning = true
		task.spawn(function()
			while speed > 0.2 do
				local dt = task.wait(0.05)
				angle += speed * dt
				speed -= 2.2 * dt
				local turned = base * CFrame.Angles(0, angle, 0)
				globe.CFrame = turned
				for _, land in lands do
					land.part.CFrame = turned * land.offset
				end
			end
			spinning = false
		end)
	end

	local showFact = newBubble(globe, 3.5)
	local nextFact = factCycle(GLOBE_FACTS)
	newPrompt(globe, "Покрутить", "Глобус").Triggered:Connect(function()
		spin()
		showFact(nextFact())
	end)

	-- Стопка тетрадей и кружка для уюта.
	for index = 0, 3 do
		newPart(parent, "Notebook", Vector3.new(1.6, 0.12, 2.1), CFrame.new(-19, 3.72 + index * 0.13, -25) * CFrame.Angles(0, index * 0.15, 0), BOOK_COLORS[index % #BOOK_COLORS + 1])
	end
	newPart(parent, "Mug", Vector3.new(0.6, 0.7, 0.6), CFrame.new(-17.4, 4, -24.2), COLORS.trim)
end

local function buildShelves(parent: Instance)
	local nextFact = factCycle(BOOK_FACTS)
	for _, x in { -35, 35 } do
		local back = buildBookshelf(parent, x, 30.6)
		local showFact = newBubble(back, 3, Vector3.new(0, 0, -3))
		newPrompt(back, "Открыть книгу", "Книжная полка").Triggered:Connect(function()
			showFact(nextFact())
		end)
	end
end

-- Подвесные лампы, выключатель и школьный звонок у двери.
local function buildLights(parent: Instance, spots: { Vector3 })
	local lamps = {}
	for _, spot in spots do
		newPart(parent, "LampCord", Vector3.new(0.15, 3.6, 0.15), CFrame.new(spot.X, 13.4, spot.Z), COLORS.leg)
		local shade = newPart(parent, "Lamp", Vector3.new(2.4, 1, 2.4), CFrame.new(spot.X, 11.2, spot.Z), COLORS.lampOn, Enum.Material.Neon)
		local light = Instance.new("PointLight")
		light.Range = 26
		light.Brightness = 1.1
		light.Color = COLORS.lampOn
		light.Parent = shade
		table.insert(lamps, { shade = shade, light = light })
	end

	local switch = newPart(parent, "LightSwitch", Vector3.new(0.8, 1.2, 0.2), CFrame.new(5, 6, 31.88), COLORS.trim)
	local click = newSound(switch, "rbxasset://sounds/switch.wav", 0.6)
	local on = true
	local prompt = newPrompt(switch, "Выключить свет", "Выключатель")
	prompt.Triggered:Connect(function()
		on = not on
		click:Play()
		prompt.ActionText = if on then "Выключить свет" else "Включить свет"
		for _, lamp in lamps do
			lamp.light.Enabled = on
			lamp.shade.Material = if on then Enum.Material.Neon else Enum.Material.SmoothPlastic
			lamp.shade.Color = if on then COLORS.lampOn else COLORS.lampOff
		end
	end)

	local bell = newPart(parent, "Bell", Vector3.new(1.6, 1.6, 0.6), CFrame.new(-5, 11, 31.7), COLORS.brass, Enum.Material.Metal)
	local ring = newSound(bell, "rbxasset://sounds/electronicpingshort.wav", 0.7, 0.7)
	local ringing = false
	newPrompt(bell, "Позвонить", "Школьный звонок").Triggered:Connect(function()
		if ringing then
			return
		end
		ringing = true
		local rest = bell.CFrame
		for strike = 1, 6 do
			ring:Play()
			bell.CFrame = rest * CFrame.Angles(0, 0, if strike % 2 == 0 then 0.12 else -0.12)
			task.wait(0.22)
		end
		bell.CFrame = rest
		ringing = false
	end)

	-- Часы над дверью показывают время сервера.
	local clock = newPart(parent, "Clock", Vector3.new(3.2, 3.2, 0.3), CFrame.new(0, 11.4, 31.8), COLORS.trim)
	local face = newSurface(clock, Enum.NormalId.Front)
	local time = newText(face, "", UDim2.fromScale(0.86, 0.5), UDim2.fromScale(0.07, 0.25), COLORS.ink, Enum.Font.RobotoMono)
	task.spawn(function()
		while true do
			time.Text = os.date("%H:%M")
			task.wait(15)
		end
	end)
end

local function buildSeat(parent: Instance, name: string, position: Vector3, lookAt: Vector3, color: Color3): (Seat, ProximityPrompt)
	local facing = CFrame.lookAt(position, Vector3.new(lookAt.X, position.Y, lookAt.Z))

	local seat = Instance.new("Seat")
	seat.Name = name
	seat.Anchored = true
	seat.Size = Vector3.new(2.6, 0.4, 2.6)
	seat.CFrame = facing
	seat.Color = color
	seat.Material = Enum.Material.SmoothPlastic
	seat.TopSurface = Enum.SurfaceType.Smooth
	seat.BottomSurface = Enum.SurfaceType.Smooth
	seat.Parent = parent

	newPart(parent, name .. "Base", Vector3.new(1.6, 1.5, 1.6), CFrame.new(position.X, 0.75, position.Z), COLORS.leg)
	-- Спинка стоит позади сидящего, то есть с обратной стороны от парты.
	newPart(parent, name .. "Back", Vector3.new(2.6, 2.6, 0.3), facing * CFrame.new(0, 1.5, 1.45), color)

	local prompt = newPrompt(seat, "Сесть", "")
	prompt.MaxActivationDistance = 9
	return seat, prompt
end

local function buildTable(parent: Instance, id: number, center: Vector3)
	local model = Instance.new("Model")
	model.Name = "Table" .. id
	model.Parent = parent

	local top = newPart(model, "Top", Vector3.new(9, 0.4, 4.4), CFrame.new(center.X, 3.3, center.Z), COLORS.table, Enum.Material.Wood)
	for _, dx in { -4, 4 } do
		for _, dz in { -1.8, 1.8 } do
			newPart(model, "Leg", Vector3.new(0.4, 3.1, 0.4), CFrame.new(center.X + dx, 1.55, center.Z + dz), COLORS.leg)
		end
	end

	local seatA, promptA = buildSeat(model, "SeatA", Vector3.new(center.X, 1.7, center.Z - 3.8), center, COLORS.seatA)
	local seatB, promptB = buildSeat(model, "SeatB", Vector3.new(center.X, 1.7, center.Z + 3.8), center, COLORS.seatB)
	promptA.ObjectText = "Парта " .. id
	promptB.ObjectText = "Парта " .. id

	-- Бланки на парте.
	for _, dz in { -1.1, 1.1 } do
		newPart(model, "Sheet", Vector3.new(1.5, 0.05, 2), CFrame.new(center.X - 1.2, 3.53, center.Z + dz), COLORS.paper)
	end

	-- Настольная лампа: горит, пока за партой идёт экзамен.
	newPart(model, "DeskLampBase", Vector3.new(0.9, 0.2, 0.9), CFrame.new(center.X + 3.6, 3.6, center.Z), COLORS.leg)
	newPart(model, "DeskLampStem", Vector3.new(0.15, 1.6, 0.15), CFrame.new(center.X + 3.6, 4.4, center.Z), COLORS.leg)
	local shade = newPart(model, "DeskLampShade", Vector3.new(1.1, 0.6, 1.1), CFrame.new(center.X + 3.6, 5.4, center.Z), COLORS.lampOff)
	local lampLight = Instance.new("PointLight")
	lampLight.Range = 14
	lampLight.Brightness = 1.6
	lampLight.Color = COLORS.active
	lampLight.Enabled = false
	lampLight.Parent = shade

	-- Салют над местом победителя.
	local fanfare = newSound(top, "rbxasset://sounds/victory.wav", 0.5)
	local emitters = {}
	for index, seat in { seatA, seatB } do
		local holder = newPart(model, "Confetti" .. index, Vector3.one, CFrame.new(seat.Position + Vector3.new(0, 7, 0)), COLORS.paper)
		holder.Transparency = 1
		holder.CanCollide = false
		local emitter = Instance.new("ParticleEmitter")
		emitter.Enabled = false
		emitter.Rate = 0
		emitter.Lifetime = NumberRange.new(1.5, 2.5)
		emitter.Speed = NumberRange.new(8, 16)
		emitter.SpreadAngle = Vector2.new(180, 180)
		emitter.Acceleration = Vector3.new(0, -18, 0)
		emitter.Size = NumberSequence.new(0.5)
		emitter.Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, COLORS.seatA),
			ColorSequenceKeypoint.new(0.5, COLORS.brass),
			ColorSequenceKeypoint.new(1, COLORS.seatB),
		})
		emitter.Parent = holder
		emitters[index] = emitter
	end

	local billboard = Instance.new("BillboardGui")
	billboard.Name = "Status"
	billboard.Size = UDim2.fromScale(5.6, 1.6) -- размер в студах: издалека табличка уменьшается и не закрывает соседние
	billboard.StudsOffset = Vector3.new(0, 5, 0)
	billboard.MaxDistance = 90
	billboard.Parent = top

	local frame = Instance.new("Frame")
	frame.Size = UDim2.fromScale(1, 1)
	frame.BackgroundColor3 = COLORS.paper
	frame.BorderSizePixel = 0
	frame.Parent = billboard
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.18, 0)
	corner.Parent = frame
	local stroke = Instance.new("UIStroke")
	stroke.Thickness = 2
	stroke.Color = COLORS.leg
	stroke.Parent = frame

	local title = Instance.new("TextLabel")
	title.BackgroundTransparency = 1
	title.Size = UDim2.fromScale(0.9, 0.4)
	title.Position = UDim2.fromScale(0.05, 0.08)
	title.Font = Enum.Font.GothamBold
	title.TextScaled = true
	title.TextColor3 = COLORS.ink
	title.Text = "Парта " .. id
	title.Parent = frame

	local status = Instance.new("TextLabel")
	status.BackgroundTransparency = 1
	status.Size = UDim2.fromScale(0.92, 0.38)
	status.Position = UDim2.fromScale(0.04, 0.54)
	status.Font = Enum.Font.GothamMedium
	status.TextScaled = true
	status.TextColor3 = COLORS.ink
	status.TextWrapped = true
	status.Text = "Свободно"
	status.Parent = frame

	return {
		id = id,
		seats = { seatA, seatB },
		prompts = { promptA, promptB },
		setStatus = function(text: string, active: boolean?)
			status.Text = text
			stroke.Color = if active then COLORS.active else COLORS.leg
		end,
		setLamp = function(on: boolean)
			if lampLight.Enabled ~= on then
				lampLight.Enabled = on
				shade.Material = if on then Enum.Material.Neon else Enum.Material.SmoothPlastic
				shade.Color = if on then COLORS.active else COLORS.lampOff
			end
		end,
		celebrate = function(seatIndex: number)
			local emitter = emitters[seatIndex]
			if emitter then
				emitter:Emit(80)
				fanfare:Play()
			end
		end,
	}
end

-- Запасная защита: если персонаж всё же оказался за пределами класса, возвращаем его ко входу.
local ROOM_HALF_X, ROOM_HALF_Z, ROOM_TOP, ROOM_BOTTOM = 43, 33, 18, -4
local RETURN_POINT = CFrame.new(0, 4, 25)

local function isOutside(position: Vector3): boolean
	return math.abs(position.X) > ROOM_HALF_X
		or math.abs(position.Z) > ROOM_HALF_Z
		or position.Y > ROOM_TOP
		or position.Y < ROOM_BOTTOM
end

World.isOutside = isOutside

local function keepPlayersInside()
	task.spawn(function()
		while true do
			task.wait(0.5)
			for _, player in Players:GetPlayers() do
				local character = player.Character
				local root = character and character:FindFirstChild("HumanoidRootPart")
				if root and root:IsA("BasePart") and isOutside(root.Position) then
					root.AssemblyLinearVelocity = Vector3.zero
					character:PivotTo(RETURN_POINT)
				end
			end
		end
	end)
end

local TABLE_COLUMNS = { -24, 0, 24 }
local TABLE_ROWS = { -10, 14 }

-- options.randomTask: функция, которая возвращает { subject = название, task = задание } для доски «Задача дня».
-- Возвращает { tables = список парт, setScoreboard = функция записи текста на доску побед }.
-- Парта: { id, seats, prompts, setStatus, setLamp, celebrate }.
function World.build(tableCount: number, options: { randomTask: (() -> any)? }?)
	local classroom = Instance.new("Folder")
	classroom.Name = "Classroom"
	classroom.Parent = Workspace

	buildRoom(classroom)

	-- Три доски на передней стене: победы, главная, задача дня.
	local _, mainBody = buildBoard(classroom, "Board", 0, 30, "ЕГЭ-ДУЭЛЬ")
	mainBody.Text = "Сядьте за парту вдвоём, выберите каждый свой предмет и время.\nПобеждает тот, кто лучше сдал свой экзамен."
	local _, scoreBody = buildBoard(classroom, "ScoreBoard", -28, 20, "ДОСКА ПОБЕД")
	scoreBody.TextXAlignment = Enum.TextXAlignment.Left
	buildDailyTask(classroom, options and options.randomTask)

	buildTeacherCorner(classroom)
	buildShelves(classroom)

	local tables, lampSpots = {}, {}
	local id = 0
	for _, z in TABLE_ROWS do
		for _, x in TABLE_COLUMNS do
			id += 1
			if id <= tableCount then
				table.insert(tables, buildTable(classroom, id, Vector3.new(x, 0, z)))
			end
			table.insert(lampSpots, Vector3.new(x, 0, z))
		end
	end
	buildLights(classroom, lampSpots)
	keepPlayersInside()

	return {
		tables = tables,
		setScoreboard = function(text: string)
			scoreBody.Text = text
		end,
	}
end

return World
