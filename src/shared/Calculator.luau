-- Калькулятор для справочных материалов экзамена. Модуль не использует API Roblox,
-- поэтому его можно проверять тестами отдельно от интерфейса.
local Calculator = {}

-- Число для экрана калькулятора: до 10 значащих цифр, дробная часть через запятую.
local function formatNumber(value: number): string
	if value ~= value or value == math.huge or value == -math.huge then
		return "ошибка"
	end
	local text = string.format("%.10g", value)
	return (string.gsub(text, "%.", ","))
end

Calculator.format = formatNumber

-- Вычислительная часть калькулятора отдельно от кнопок, чтобы её можно было проверить тестами.
-- press(key) принимает цифры, ",", "+", "-", "×", "÷", "=", "√", "±", "C", "←" и возвращает строку для экрана.
function Calculator.new()
	local entry = "0" -- то, что набирается сейчас
	local stored: number? = nil -- левое число незавершённого действия
	local operation: string? = nil
	local fresh = true -- следующая цифра начинает новое число

	local function current(): number
		return tonumber((string.gsub(entry, ",", "."))) or 0
	end

	local function apply(left: number, op: string, right: number): number
		if op == "+" then
			return left + right
		elseif op == "-" then
			return left - right
		elseif op == "×" then
			return left * right
		end
		return if right == 0 then 0 / 0 else left / right
	end

	local function resolve()
		if stored ~= nil and operation then
			entry = formatNumber(apply(stored, operation, current()))
		end
		stored, operation = nil, nil
	end

	local function press(key: string): string
		if entry == "ошибка" and key ~= "C" then
			return entry
		end
		if string.match(key, "^%d$") then
			if fresh or entry == "0" then
				entry = key
			elseif #entry < 14 then
				entry ..= key
			end
			fresh = false
		elseif key == "," then
			if fresh then
				entry = "0,"
			elseif not string.find(entry, ",", 1, true) then
				entry ..= ","
			end
			fresh = false
		elseif key == "C" then
			entry, stored, operation, fresh = "0", nil, nil, true
		elseif key == "←" then
			if not fresh then
				entry = string.sub(entry, 1, -2)
				if entry == "" or entry == "-" then
					entry = "0"
				end
			end
		elseif key == "±" then
			entry = formatNumber(-current())
		elseif key == "√" then
			local value = current()
			entry = if value < 0 then "ошибка" else formatNumber(math.sqrt(value))
			fresh = true
		elseif key == "=" then
			resolve()
			fresh = true
		elseif key == "+" or key == "-" or key == "×" or key == "÷" then
			if not fresh or stored == nil then
				resolve()
			end
			if entry ~= "ошибка" then
				stored, operation = current(), key
			end
			fresh = true
		end
		return entry
	end

	return press
end

return Calculator
