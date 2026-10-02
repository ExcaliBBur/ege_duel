-- Составление варианта. Если у заданий есть номера ЕГЭ, вариант собирается по номерам:
-- по одному заданию на номер, в порядке номеров, как на экзамене. Иначе берутся случайные задания разных тем.
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

local function numbersOfPart(tasks, partTwo: boolean): { number }
	local seen, numbers = {}, {}
	for _, task in tasks do
		if task.number and (task.part == 2) == partTwo and not seen[task.number] then
			seen[task.number] = true
			table.insert(numbers, task.number)
		end
	end
	table.sort(numbers)
	return numbers
end

-- Номера первой части (с кратким ответом), для которых в банке есть задания, по возрастанию.
function Variant.numbersOf(tasks): { number }
	return numbersOfPart(tasks, false)
end

-- Номера второй части (с развёрнутым ответом), по возрастанию.
function Variant.partTwoNumbersOf(tasks): { number }
	return numbersOfPart(tasks, true)
end

-- Вариант по номерам. count = 0 означает всю первую часть; иначе номера делятся на count
-- подряд идущих групп и из каждой берётся один случайный номер, чтобы сокращённый вариант
-- охватывал экзамен от начала до конца. С withPartTwo в конец добавляется вся вторая часть.
local function pickByNumbers(tasks, numbers: { number }, count: number, random, withPartTwo: boolean)
	local byNumber = {}
	for _, task in tasks do
		if task.number then
			byNumber[task.number] = byNumber[task.number] or {}
			table.insert(byNumber[task.number], task)
		end
	end

	local chosen = numbers
	if count > 0 and count < #numbers then
		chosen = {}
		for group = 1, count do
			local first = math.floor((group - 1) * #numbers / count) + 1
			local last = math.floor(group * #numbers / count)
			table.insert(chosen, numbers[first + random(last - first + 1) - 1])
		end
	end
	if withPartTwo then
		chosen = table.clone(chosen)
		for _, number in Variant.partTwoNumbersOf(tasks) do
			table.insert(chosen, number)
		end
	end

	-- Задания к одному тексту помечены общим context вида "семейство:текст". Выбрав текст для первого
	-- такого номера, остальные номера того же семейства берём по тому же тексту, как на экзамене.
	local contexts = {}
	local picked = {}
	for _, number in chosen do
		local pool = byNumber[number]
		local task = pool[random(#pool)]
		local family = if task.context then string.match(task.context, "^([^:]+):") else nil
		if family then
			if contexts[family] then
				local same = {}
				for _, candidate in pool do
					if candidate.context == contexts[family] then
						table.insert(same, candidate)
					end
				end
				if #same > 0 then
					task = same[random(#same)]
				end
			else
				contexts[family] = task.context
			end
		end
		table.insert(picked, task)
	end
	return picked
end

-- Выбирает count заданий без учёта номеров. Задания с одинаковым group берутся по очереди,
-- чтобы темы не повторялись подряд.
local function pickByGroups(tasks, count: number, random)
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

-- count = 0 означает всю первую часть (для банка без номеров это 20 заданий).
-- withPartTwo: добавить после первой части все номера второй части.
function Variant.pick(tasks, count: number, seed: number, withPartTwo: boolean?)
	local random = newRandom(seed)
	local numbers = Variant.numbersOf(tasks)
	if #numbers > 0 then
		return pickByNumbers(tasks, numbers, count, random, withPartTwo == true)
	end
	return pickByGroups(tasks, if count > 0 then count else 20, random)
end

return Variant
