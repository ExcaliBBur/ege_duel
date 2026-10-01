-- Работа с текстом ответов. string.lower не умеет кириллицу, поэтому регистр меняем по кодам символов.
local Text = {}

local function lowerCode(code: number): number
	if code >= 0x41 and code <= 0x5A then
		return code + 32
	elseif code >= 0x410 and code <= 0x42F then
		return code + 32
	elseif code == 0x401 or code == 0x451 then
		return 0x435 -- Ё и ё считаем буквой е
	end
	return code
end

local function upperCode(code: number): number
	if code >= 0x61 and code <= 0x7A then
		return code - 32
	elseif code >= 0x430 and code <= 0x44F then
		return code - 32
	elseif code == 0x451 then
		return 0x401
	end
	return code
end

local function isSpace(code: number): boolean
	return code == 32 or code == 9 or code == 10 or code == 13 or code == 0xA0
end

local function isDash(code: number): boolean
	return code == 0x2212 or code == 0x2013 or code == 0x2014
end

-- Массив кодов символов; для битой строки возвращает пустой массив.
function Text.codes(s: string): { number }
	local result = {}
	if type(s) ~= "string" or utf8.len(s) == nil then
		return result
	end
	for _, code in utf8.codes(s) do
		table.insert(result, code)
	end
	return result
end

function Text.length(s: string): number
	return #Text.codes(s)
end

-- Массив отдельных символов строки.
function Text.chars(s: string): { string }
	local result = {}
	for _, code in Text.codes(s) do
		table.insert(result, utf8.char(code))
	end
	return result
end

function Text.upper(s: string): string
	local out = {}
	for _, code in Text.codes(s) do
		table.insert(out, utf8.char(upperCode(code)))
	end
	return table.concat(out)
end

-- Обрезает строку до maxChars символов.
function Text.truncate(s: string, maxChars: number): string
	local out = {}
	for index, code in Text.codes(s) do
		if index > maxChars then
			break
		end
		table.insert(out, utf8.char(code))
	end
	return table.concat(out)
end

-- Приводит ответ к виду для сравнения: без пробелов, строчными буквами, ё как е, любое тире как минус.
function Text.normalize(s: string): string
	local out = {}
	for _, code in Text.codes(s) do
		if not isSpace(code) then
			if isDash(code) then
				code = 0x2D
			end
			table.insert(out, utf8.char(lowerCode(code)))
		end
	end
	return table.concat(out)
end

return Text
