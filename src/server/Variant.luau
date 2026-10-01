-- Составление варианта: случайные задания из банка, по возможности из разных тем.
-- Свой генератор случайных чисел нужен, чтобы один и тот же seed давал один и тот же вариант.
local Variant = {}

local MODULUS = 2147483647

local function newRandom(seed: number)
	local state = math.floor(seed) % MODULUS
	if state <= 0 then
		state += MODULUS - 1
	end
	-- Возвращает целое от 1 до n.
	return function(n: number): number
		state = (state * 48271) % MODULUS
		return state % n + 1
	end
end

local function shuffle(list, random)
	for index = #list, 2, -1 do
		local other = random(index)
		list[index], list[other] = list[other], list[index]
	end
end

-- Выбирает count заданий. Задания с одинаковым group берутся по очереди, чтобы темы не повторялись подряд.
function Variant.pick(tasks, count: number, seed: number)
	local random = newRandom(seed)
	local groups, order = {}, {}
	for _, task in tasks do
		local key = task.group or task.id or "общая"
		if not groups[key] then
			groups[key] = {}
			table.insert(order, key)
		end
		table.insert(groups[key], task)
	end
	table.sort(order)
	shuffle(order, random)
	for _, key in order do
		shuffle(groups[key], random)
	end

	local picked = {}
	local round = 1
	while #picked < count do
		local added = false
		for _, key in order do
			local task = groups[key][round]
			if task then
				table.insert(picked, task)
				added = true
				if #picked >= count then
					break
				end
			end
		end
		if not added then
			break
		end
		round += 1
	end
	return picked
end

return Variant
