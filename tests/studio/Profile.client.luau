-- Поиск причины низкой частоты кадров: по очереди убирает на клиенте группы объектов класса
-- и измеряет частоту кадров после каждого шага. Запускается через profile.project.json.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local lines = {}

local frames = 0
RunService.RenderStepped:Connect(function()
	frames += 1
end)

-- Частота кадров в Studio ограничена сверху (60, а в неактивном окне 15), поэтому рядом пишем
-- настоящие затраты на кадр из службы Stats: они не зависят от ограничения.
local Stats = game:GetService("Stats")

local function stat(name: string): number
	local ok, value = pcall(function()
		return (Stats :: any)[name]
	end)
	return if ok and type(value) == "number" then value else -1
end

local function measure(label: string)
	task.wait(1)
	frames = 0
	local started = os.clock()
	local samples, cpu, gpu, beat = 0, 0, 0, 0
	while os.clock() - started < 3 do
		cpu += stat("RenderCPUFrameTime")
		gpu += stat("RenderGPUFrameTime")
		beat += stat("HeartbeatTime")
		samples += 1
		task.wait(0.1)
	end
	table.insert(lines, string.format(
		"FPS %s: %.0f | RenderCPU %g | RenderGPU %g | Heartbeat %g | FrameTime %g | Physics %g | отрисовок %d",
		label, frames / (os.clock() - started), cpu / samples, gpu / samples, beat / samples,
		stat("FrameTime"), stat("PhysicsStepTime"), stat("SceneDrawcallCount")
	))
end

local function removeAll(root: Instance, predicate: (Instance) -> boolean): number
	local count = 0
	for _, item in root:GetDescendants() do
		if item.Parent and predicate(item) then
			item:Destroy()
			count += 1
		end
	end
	return count
end

local function run()
	if not player.Character then
		player.CharacterAdded:Wait()
	end
	local classroom = Workspace:WaitForChild("Classroom", 20)
	local gui = player:WaitForChild("PlayerGui"):WaitForChild("EgeDuel", 20)
	task.wait(4)
	local parts = 0
	for _, item in classroom:GetDescendants() do
		if item:IsA("BasePart") then
			parts += 1
		end
	end
	table.insert(lines, "деталей в классе: " .. parts)

	-- Рывки: длинные паузы между кадрами видны при любом ограничении частоты кадров.
	local gaps = {}
	local connection = RunService.RenderStepped:Connect(function(dt)
		table.insert(gaps, dt)
	end)
	task.wait(20)
	connection:Disconnect()
	table.sort(gaps)
	local total = 0
	for _, dt in gaps do
		total += dt
	end
	local long = 0
	for _, dt in gaps do
		if dt > 0.15 then
			long += 1
		end
	end
	table.insert(lines, string.format(
		"РЫВКИ за 20 с: кадров %d, средний %.0f мс, медиана %.0f мс, 95%% %.0f мс, худший %.0f мс, кадров дольше 150 мс: %d",
		#gaps, total / #gaps * 1000, gaps[math.ceil(#gaps / 2)] * 1000, gaps[math.ceil(#gaps * 0.95)] * 1000, gaps[#gaps] * 1000, long
	))
	measure("как есть")

	gui.Enabled = false
	measure("без интерфейса игры")

	local n = removeAll(classroom, function(item)
		return item:IsA("BillboardGui")
	end)
	measure("без табличек над партами (" .. n .. ")")

	n = removeAll(classroom, function(item)
		return item:IsA("SurfaceGui")
	end)
	measure("без надписей на досках и плакатах (" .. n .. ")")

	n = removeAll(classroom, function(item)
		return item:IsA("Light") or item:IsA("ParticleEmitter")
	end)
	for _, item in classroom:GetDescendants() do
		if item:IsA("BasePart") and item.Material == Enum.Material.Neon then
			item.Material = Enum.Material.SmoothPlastic
		end
	end
	measure("без света и неона (" .. n .. ")")

	n = removeAll(classroom, function(item)
		return item:IsA("BasePart") and item.Material == Enum.Material.Glass
	end)
	measure("без стёкол (" .. n .. ")")

	n = removeAll(classroom, function(item)
		return item:IsA("ProximityPrompt")
	end)
	measure("без подсказок E (" .. n .. ")")

	classroom:Destroy()
	measure("пустой мир")

	if player.Character then
		for _, item in player.Character:GetDescendants() do
			if item:IsA("Accessory") or item:IsA("Clothing") or item:IsA("WrapLayer") then
				item:Destroy()
			end
		end
	end
	measure("пустой мир, персонаж без аксессуаров")
end

local ok, message = pcall(run)
if not ok then
	table.insert(lines, "FAIL " .. tostring(message))
end
ReplicatedStorage:WaitForChild("EgeTestReport"):FireServer(table.concat(lines, "\n"))
