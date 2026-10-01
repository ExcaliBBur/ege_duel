-- Временный плагин для автопроверки в Roblox Studio.
-- В режиме редактирования запускает игру (как кнопка Play), внутри игры ждёт отчёт тестового сценария
-- и завершает запуск. Срабатывает только в месте, собранном из test.project.json.
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local StudioTestService = game:GetService("StudioTestService")

if not ServerScriptService:FindFirstChild("EgeDuelAutotest") then
	return
end

if RunService:IsEdit() then
	task.wait(4)
	print("EGETEST PLUGIN запускаю игру")
	local ok, result = pcall(function()
		return StudioTestService:ExecutePlayModeAsync({})
	end)
	print("EGETEST PLUGIN RESULT ok=" .. tostring(ok) .. " " .. tostring(result))
	pcall(function()
		plugin:SetSetting("EgeDuelAutotestResult", tostring(ok) .. " " .. tostring(result))
	end)
	print("EGETEST PLUGIN END")
elseif RunService:IsServer() then
	local result = ReplicatedStorage:WaitForChild("EgeTestResult", 240)
	local text = if result then result.Value else "TIMEOUT: сценарий не прислал отчёт"
	print("EGETEST PLUGIN завершаю игру")
	StudioTestService:EndTest(text)
end
