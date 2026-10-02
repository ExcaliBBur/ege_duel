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
		{ "math_base", { "b2_units", "b3_bar_chart", "b3_price_graph", "b6_carriers", "b6_internet", "b6_route", "b7_function_points",
			"b7_speed_intervals", "b8_clubs", "b9_rhombus", "b9_plan", "b18_number_line", "b18_quadratic" } },
		{ "math_prof", { "p1_right_triangle", "p1_circle_angles", "s_cylinder", "st_table", "d_graph_tangent", "d_graph_derivative",
			"d_graph_points", "g_two_lines", "g_parabola", "g_hyperbola", "g_exponent", "g_logarithm", "g_root" } },
		{ "physics", { "fig_xt_graph", "fig_circuit_series", "fig_circuit_parallel", "fig_forces", "fig_pv_work", "fig_iu_graph" } },
		{ "informatics", { "fig_paths", "fig_spreadsheet" } },
		{ "chemistry", { "fig_atom", "fig_skeleton" } },
		{ "biology", { "fig_punnett", "fig_dna" } },
		{ "geography", { "fig_climate", "fig_wind_rose" } },
		{ "social", { "fig_poll", "fig_market" } },
	}
	local picked = {}
	local Bank = require(game:GetService("ServerScriptService"):WaitForChild("Server"):WaitForChild("Bank"))
	for _, entry in wanted do
		for _, group in entry[2] do
			for _, task in Bank.getTasks(entry[1]) do
				if task.group == group then
					table.insert(picked, { text = task.text, points = task.points, figure = task.figure, number = task.number, topic = task.topic })
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

-- Переносит персонажа в указанную точку: так проверяется возврат из-за пределов класса.
local throwRequest = Instance.new("RemoteEvent")
throwRequest.Name = "EgeTestThrow"
throwRequest.Parent = ReplicatedStorage
throwRequest.OnServerEvent:Connect(function(player: Player, position: any)
	if player.Character and typeof(position) == "Vector3" then
		player.Character:PivotTo(CFrame.new(position))
	end
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
