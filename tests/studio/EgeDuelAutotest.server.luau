-- Серверная часть автопроверки в Studio: по просьбе клиента сажает игрока за парту и собирает отчёт.
local LogService = game:GetService("LogService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local report = Instance.new("RemoteEvent")
report.Name = "EgeTestReport"
report.Parent = ReplicatedStorage

local seatRequest = Instance.new("RemoteEvent")
seatRequest.Name = "EgeTestSeat"
seatRequest.Parent = ReplicatedStorage

local function serverErrors(): string
	local lines = {}
	for _, entry in LogService:GetLogHistory() do
		if entry.messageType == Enum.MessageType.MessageError then
			table.insert(lines, "SERVER ERROR: " .. entry.message)
		end
	end
	return table.concat(lines, "\n")
end

local finished = false
local function finish(text: string)
	if finished then
		return
	end
	finished = true
	local full = text .. "\n" .. serverErrors()
	for _, line in string.split(full, "\n") do
		print("EGETEST " .. line)
	end
	local value = Instance.new("StringValue")
	value.Name = "EgeTestResult"
	value.Value = full
	value.Parent = ReplicatedStorage
end

report.OnServerEvent:Connect(function(_, text)
	finish(tostring(text))
end)
task.delay(200, finish, "TIMEOUT: клиент не прислал отчёт")

-- Образцы заданий для режима снимков: по одному заданию с рисунком каждого вида и задания с символами.
local samples = Instance.new("RemoteFunction")
samples.Name = "EgeTestSamples"
samples.Parent = ReplicatedStorage
samples.OnServerInvoke = function()
	local wanted = {
		math_base = { "fig_bar_chart", "fig_grid_triangle", "fig_linear_graph", "mb_powers" },
		math_prof = { "mp_exponential", "mp_log", "mp_root_equation" },
		physics = { "fig_velocity_graph" },
		informatics = { "fig_roads" },
		chemistry = { "ch_oxidation", "органика" },
	}
	local picked = {}
	local bank = game:GetService("ServerStorage"):WaitForChild("Bank")
	for subject, groups in wanted do
		local data = require(bank:WaitForChild(subject))
		for _, group in groups do
			for _, task in data.tasks do
				if task.group == group then
					table.insert(picked, { text = task.text, points = task.points, figure = task.figure })
					break
				end
			end
		end
	end
	return picked
end

-- Подводит персонажа к предмету, чтобы подсказка «E» у него стала доступной.
local walkRequest = Instance.new("RemoteEvent")
walkRequest.Name = "EgeTestWalk"
walkRequest.Parent = ReplicatedStorage
walkRequest.OnServerEvent:Connect(function(player: Player, part: any)
	local character = player.Character
	if not character or typeof(part) ~= "Instance" or not part:IsA("BasePart") then
		return
	end
	local flat = Vector3.new(part.Position.X, 0, part.Position.Z)
	local toCenter = if flat.Magnitude > 1 then -flat.Unit else Vector3.new(0, 0, 1)
	character:PivotTo(CFrame.new(flat + toCenter * 4 + Vector3.new(0, 3.5, 0)))
end)

-- Запасной путь посадки, если подсказку у стула не удалось нажать из сценария.
seatRequest.OnServerEvent:Connect(function(player: Player)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local seat = Workspace:WaitForChild("Classroom"):WaitForChild("Table1"):WaitForChild("SeatA")
	if humanoid and not seat.Occupant then
		seat:Sit(humanoid)
	end
end)
