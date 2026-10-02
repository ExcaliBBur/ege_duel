-- Настройки матча, общие для сервера и клиента.
local Settings = {}

Settings.timeOptions = { 10, 20, 30, 45, 60, 90, 120, 180 } -- минуты
-- Число заданий. 0 означает всю первую часть экзамена; остальные значения дают сокращённый вариант,
-- в котором номера идут по порядку и охватывают экзамен от начала до конца.
Settings.countOptions = { 8, 12, 16, 0 }
Settings.fullCount = 0
Settings.defaultTime = 20
Settings.defaultCount = 12

Settings.countdownSeconds = 3
Settings.answerMaxChars = 17 -- как в бланке ответов №1
Settings.graceSeconds = 1.5 -- сколько сервер ждёт последние ответы после конца времени

-- Вторая часть: задания с развёрнутым ответом. Расчётные проверяются по итоговому ответу,
-- остальные после сдачи оценивает соперник по эталону и критериям.
Settings.essayMaxChars = 3000 -- длина развёрнутого ответа
Settings.reviewBaseSeconds = 60 -- время на взаимную проверку: основа и добавка за каждую работу
Settings.reviewPerItemSeconds = 90
Settings.reviewMaxSeconds = 900

function Settings.isTimeOption(value: any): boolean
	return table.find(Settings.timeOptions, value) ~= nil
end

function Settings.isCountOption(value: any): boolean
	return table.find(Settings.countOptions, value) ~= nil
end

-- Сколько секунд даётся на взаимную проверку, если самому занятому проверяющему досталось items работ.
function Settings.reviewSeconds(items: number): number
	return math.min(Settings.reviewMaxSeconds, Settings.reviewBaseSeconds + Settings.reviewPerItemSeconds * items)
end

return Settings
