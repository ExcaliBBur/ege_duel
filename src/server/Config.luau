-- Настройки сервера.
local Config = {}

-- Адрес папки с банком заданий в интернете (там должны лежать index.json и файлы предметов из bank/dist).
-- Пустая строка: используется только копия банка, встроенная в игру.
-- Если скачать не удалось, игра тоже берёт встроенную копию.
Config.bankBaseUrl = "https://raw.githubusercontent.com/ExcaliBBur/ege_duel/main/bank/dist"

Config.tableCount = 6

return Config
