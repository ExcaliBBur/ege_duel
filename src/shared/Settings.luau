-- Настройки матча, общие для сервера и клиента.
local Settings = {}

Settings.timeOptions = { 10, 20, 30, 45 } -- минуты
Settings.countOptions = { 8, 12, 16, 20 } -- число заданий
Settings.defaultTime = 20
Settings.defaultCount = 12

Settings.countdownSeconds = 3
Settings.answerMaxChars = 17 -- как в бланке ответов №1
Settings.graceSeconds = 1.5 -- сколько сервер ждёт последние ответы после конца времени

function Settings.isTimeOption(value: any): boolean
	return table.find(Settings.timeOptions, value) ~= nil
end

function Settings.isCountOption(value: any): boolean
	return table.find(Settings.countOptions, value) ~= nil
end

return Settings
