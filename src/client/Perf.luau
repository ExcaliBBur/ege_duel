-- Диагностика производительности. Работает только при запуске в Studio: раз в 5 секунд пишет в Output
-- строку с меткой EGEPERF (частота кадров, время процессора и видеокарты на кадр, самый долгий кадр).
-- По этим строкам в журнале Studio можно понять, на каком экране игра тормозит.
local RunService = game:GetService("RunService")
local Stats = game:GetService("Stats")

local Perf = {}

local phase = "класс"

-- Название текущего экрана, попадает в строку диагностики.
function Perf.setPhase(name: string)
	phase = name
end

function Perf.start()
	if not RunService:IsStudio() then
		return
	end
	local frames, cpu, gpu, worst, since = 0, 0, 0, 0, os.clock()
	RunService.RenderStepped:Connect(function(dt: number)
		frames += 1
		cpu += Stats.RenderCPUFrameTime
		gpu += Stats.RenderGPUFrameTime
		worst = math.max(worst, dt)
		local elapsed = os.clock() - since
		if elapsed >= 5 then
			print(string.format(
				"EGEPERF экран=%s кадров_в_секунду=%.0f процессор_мс=%.1f видеокарта_мс=%.1f худший_кадр_мс=%.0f скрипты_мс=%.2f",
				phase, frames / elapsed, cpu / frames * 1000, gpu / frames * 1000, worst * 1000, Stats.HeartbeatTime * 1000
			))
			frames, cpu, gpu, worst, since = 0, 0, 0, 0, os.clock()
		end
	end)
end

return Perf
