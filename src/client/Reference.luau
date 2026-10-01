-- Справочные материалы, которые выдают на экзамене: таблица Менделеева и ряд активности металлов
-- для химии, справочные данные для физики, формулы для математики, калькулятор там, где он разрешён.
-- Вкладки строятся только при открытии и удаляются при закрытии, чтобы не держать лишние объекты.
local Ui = require(script.Parent.Ui)
local Calculator = require(game:GetService("ReplicatedStorage"):WaitForChild("Shared").Calculator)

local Reference = {}

local C = Ui.colors

-- Символ и относительная атомная масса, округлённая как в школьной таблице. Индекс равен порядковому номеру.
local ELEMENTS = {
	{ "H", "1" }, { "He", "4" }, { "Li", "7" }, { "Be", "9" }, { "B", "11" }, { "C", "12" }, { "N", "14" },
	{ "O", "16" }, { "F", "19" }, { "Ne", "20" }, { "Na", "23" }, { "Mg", "24" }, { "Al", "27" }, { "Si", "28" },
	{ "P", "31" }, { "S", "32" }, { "Cl", "35,5" }, { "Ar", "40" }, { "K", "39" }, { "Ca", "40" }, { "Sc", "45" },
	{ "Ti", "48" }, { "V", "51" }, { "Cr", "52" }, { "Mn", "55" }, { "Fe", "56" }, { "Co", "59" }, { "Ni", "59" },
	{ "Cu", "64" }, { "Zn", "65" }, { "Ga", "70" }, { "Ge", "73" }, { "As", "75" }, { "Se", "79" }, { "Br", "80" },
	{ "Kr", "84" }, { "Rb", "85" }, { "Sr", "88" }, { "Y", "89" }, { "Zr", "91" }, { "Nb", "93" }, { "Mo", "96" },
	{ "Tc", "98" }, { "Ru", "101" }, { "Rh", "103" }, { "Pd", "106" }, { "Ag", "108" }, { "Cd", "112" },
	{ "In", "115" }, { "Sn", "119" }, { "Sb", "122" }, { "Te", "128" }, { "I", "127" }, { "Xe", "131" },
	{ "Cs", "133" }, { "Ba", "137" }, { "La", "139" }, { "Ce", "140" }, { "Pr", "141" }, { "Nd", "144" },
	{ "Pm", "145" }, { "Sm", "150" }, { "Eu", "152" }, { "Gd", "157" }, { "Tb", "159" }, { "Dy", "163" },
	{ "Ho", "165" }, { "Er", "167" }, { "Tm", "169" }, { "Yb", "173" }, { "Lu", "175" }, { "Hf", "178" },
	{ "Ta", "181" }, { "W", "184" }, { "Re", "186" }, { "Os", "190" }, { "Ir", "192" }, { "Pt", "195" },
	{ "Au", "197" }, { "Hg", "201" }, { "Tl", "204" }, { "Pb", "207" }, { "Bi", "209" }, { "Po", "209" },
	{ "At", "210" }, { "Rn", "222" }, { "Fr", "223" }, { "Ra", "226" }, { "Ac", "227" }, { "Th", "232" },
	{ "Pa", "231" }, { "U", "238" }, { "Np", "237" }, { "Pu", "244" }, { "Am", "243" }, { "Cm", "247" },
	{ "Bk", "247" }, { "Cf", "251" }, { "Es", "252" }, { "Fm", "257" }, { "Md", "258" }, { "No", "259" },
	{ "Lr", "262" }, { "Rf", "267" }, { "Db", "268" }, { "Sg", "269" }, { "Bh", "270" }, { "Hs", "277" },
	{ "Mt", "278" }, { "Ds", "281" }, { "Rg", "282" }, { "Cn", "285" }, { "Nh", "286" }, { "Fl", "289" },
	{ "Mc", "290" }, { "Lv", "293" }, { "Ts", "294" }, { "Og", "294" },
}

-- Место элемента в длинной форме таблицы: строка (1-7 периоды, 8 лантаноиды, 9 актиноиды) и столбец (группа).
local function placeOf(number: number): (number, number)
	if number == 1 then
		return 1, 1
	elseif number == 2 then
		return 1, 18
	elseif number <= 10 then
		return 2, if number <= 4 then number - 2 else number + 8
	elseif number <= 18 then
		return 3, if number <= 12 then number - 10 else number
	elseif number <= 36 then
		return 4, number - 18
	elseif number <= 54 then
		return 5, number - 36
	elseif number <= 57 then
		return 6, number - 54
	elseif number <= 71 then
		return 8, number - 54 -- лантаноиды: церий в 4-м столбце
	elseif number <= 86 then
		return 6, number - 68
	elseif number <= 89 then
		return 7, number - 86
	elseif number <= 103 then
		return 9, number - 86 -- актиноиды: торий в 4-м столбце
	end
	return 7, number - 100
end

local BLOCK_COLORS = {
	s = Color3.fromRGB(251, 227, 237),
	p = Color3.fromRGB(251, 239, 211),
	d = Color3.fromRGB(221, 241, 242),
	f = Color3.fromRGB(223, 243, 231),
}

local function blockOf(row: number, column: number, number: number): string
	if row >= 8 then
		return "f"
	elseif column <= 2 or number == 2 then
		return "s"
	elseif column >= 13 then
		return "p"
	end
	return "d"
end

local function buildPeriodicTable(parent: Instance)
	local cellWidth, cellHeight = 47, 46
	local left, top = 12, 8
	for number, element in ELEMENTS do
		local row, column = placeOf(number)
		local y = top + (row - 1) * cellHeight + (if row >= 8 then 14 else 0)
		local cell = Ui.frame({
			Position = UDim2.fromOffset(left + (column - 1) * cellWidth, y),
			Size = UDim2.fromOffset(cellWidth - 2, cellHeight - 2),
			BackgroundColor3 = BLOCK_COLORS[blockOf(row, column, number)],
			Parent = parent,
		})
		Ui.label({
			Text = tostring(number),
			TextSize = 10,
			TextColor3 = C.muted,
			TextWrapped = false,
			Position = UDim2.fromOffset(3, 1),
			Size = UDim2.fromOffset(30, 11),
			Parent = cell,
		})
		Ui.label({
			Text = element[1],
			Font = Ui.fonts.bold,
			TextSize = 17,
			TextWrapped = false,
			TextXAlignment = Enum.TextXAlignment.Center,
			Position = UDim2.fromOffset(0, 11),
			Size = UDim2.new(1, 0, 0, 20),
			Parent = cell,
		})
		Ui.label({
			Text = element[2],
			TextSize = 10,
			TextWrapped = false,
			TextXAlignment = Enum.TextXAlignment.Center,
			Position = UDim2.fromOffset(0, 31),
			Size = UDim2.new(1, 0, 0, 12),
			Parent = cell,
		})
	end
	Ui.label({
		Text = "В клетке: порядковый номер, символ, относительная атомная масса. Строки внизу: лантаноиды (58-71) и актиноиды (90-103). "
			.. "Номер периода равен номеру строки, номер группы равен номеру столбца.",
		TextSize = 13,
		TextColor3 = C.muted,
		TextYAlignment = Enum.TextYAlignment.Top,
		Position = UDim2.fromOffset(left, top + 9 * cellHeight + 22),
		Size = UDim2.new(1, -24, 0, 40),
		Parent = parent,
	})
end

local function buildSheet(parent: Instance, text: string)
	local scroll = Ui.new("ScrollingFrame", {
		Position = UDim2.fromOffset(12, 8),
		Size = UDim2.new(1, -24, 1, -16),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = C.muted,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		Parent = parent,
	})
	Ui.label({
		Text = text,
		TextSize = 17,
		LineHeight = 1.25,
		TextYAlignment = Enum.TextYAlignment.Top,
		Size = UDim2.new(1, -14, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		Parent = scroll,
	})
end

local CALCULATOR_KEYS = {
	{ "C", "←", "√", "÷" },
	{ "7", "8", "9", "×" },
	{ "4", "5", "6", "-" },
	{ "1", "2", "3", "+" },
	{ "±", "0", ",", "=" },
}

local function buildCalculator(parent: Instance)
	local press = Calculator.new()
	local holder = Ui.frame({
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 16),
		Size = UDim2.fromOffset(368, 420),
		BackgroundTransparency = 1,
		Parent = parent,
	})
	local display = Ui.label({
		Name = "Display",
		Text = "0",
		Font = Ui.fonts.mono,
		TextSize = 34,
		TextXAlignment = Enum.TextXAlignment.Right,
		TextWrapped = false,
		BackgroundTransparency = 0,
		BackgroundColor3 = C.sunken,
		Size = UDim2.new(1, 0, 0, 64),
		Parent = holder,
	})
	Ui.corner(8).Parent = display
	Ui.new("UIPadding", { PaddingRight = UDim.new(0, 14), Parent = display })
	for rowIndex, row in CALCULATOR_KEYS do
		for columnIndex, key in row do
			local isAction = not string.match(key, "^[%d,]$")
			local button = Ui.button(key, if key == "=" then "primary" elseif isAction then "selected" else "plain", {
				Name = "Key" .. key,
				TextSize = 22,
				Position = UDim2.fromOffset((columnIndex - 1) * 94, 76 + (rowIndex - 1) * 66),
				Size = UDim2.fromOffset(86, 58),
				Parent = holder,
			})
			button.Activated:Connect(function()
				display.Text = press(key)
			end)
		end
	end
	Ui.label({
		Text = "Обычный непрограммируемый калькулятор, как разрешено на экзамене.",
		TextSize = 13,
		TextColor3 = C.muted,
		TextXAlignment = Enum.TextXAlignment.Center,
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 444),
		Size = UDim2.fromOffset(600, 20),
		Parent = parent,
	})
end

local ACTIVITY_SERIES = [[Электрохимический ряд напряжений металлов

Li   K   Ba   Ca   Na   Mg   Al   Mn   Zn   Cr   Fe   Co   Ni   Sn   Pb   (H₂)   Cu   Hg   Ag   Pt   Au

Слева направо активность металлов уменьшается.

Металлы, стоящие левее водорода, вытесняют водород из растворов кислот. Металлы правее водорода с растворами кислот без окислительных свойств не реагируют.

Более активный металл вытесняет менее активный из раствора его соли. Самые активные металлы (от Li до Na) в растворе реагируют прежде всего с водой.]]

local PHYSICS_SHEET = [[Десятичные приставки
гига (Г) 10⁹     мега (М) 10⁶     кило (к) 10³     гекто (г) 10²
деци (д) 10⁻¹     санти (с) 10⁻²     милли (м) 10⁻³     микро (мк) 10⁻⁶     нано (н) 10⁻⁹     пико (п) 10⁻¹²

Константы
число π = 3,14
ускорение свободного падения на Земле g = 10 м/с²
гравитационная постоянная G = 6,7 · 10⁻¹¹ Н·м²/кг²
универсальная газовая постоянная R = 8,31 Дж/(моль·К)
постоянная Больцмана k = 1,38 · 10⁻²³ Дж/К
постоянная Авогадро N = 6 · 10²³ моль⁻¹
скорость света в вакууме c = 3 · 10⁸ м/с
коэффициент в законе Кулона k = 9 · 10⁹ Н·м²/Кл²
модуль заряда электрона e = 1,6 · 10⁻¹⁹ Кл
постоянная Планка h = 6,6 · 10⁻³⁴ Дж·с

Соотношения между единицами
температура: 0 К = -273 °C
атомная единица массы: 1 а. е. м. = 1,66 · 10⁻²⁷ кг
1 электронвольт: 1 эВ = 1,6 · 10⁻¹⁹ Дж

Массы частиц
электрон 9,1 · 10⁻³¹ кг     протон 1,673 · 10⁻²⁷ кг     нейтрон 1,675 · 10⁻²⁷ кг

Плотность, кг/м³
вода 1000     древесина (сосна) 400     керосин 800     подсолнечное масло 900
алюминий 2700     железо 7800     ртуть 13 600

Удельная теплоёмкость, Дж/(кг·К)
вода 4200     лёд 2100     железо 460     свинец 130     алюминий 900     медь 380     чугун 500

Удельная теплота
парообразования воды 2,3 · 10⁶ Дж/кг     плавления льда 3,3 · 10⁵ Дж/кг     плавления свинца 2,5 · 10⁴ Дж/кг

Нормальные условия: давление 10⁵ Па, температура 0 °C

Молярная масса, г/моль
водород 2     гелий 4     литий 6     неон 20     азот 28     воздух 29     кислород 32     аргон 40
вода 18     углекислый газ 44]]

local MATH_PROFILE_SHEET = [[Справочные материалы

sin²α + cos²α = 1

sin 2α = 2 · sin α · cos α

cos 2α = cos²α - sin²α

sin (α + β) = sin α · cos β + cos α · sin β

cos (α + β) = cos α · cos β - sin α · sin β]]

local MATH_BASE_SHEET = [[Формулы сокращённого умножения
(a + b)² = a² + 2ab + b²     (a - b)² = a² - 2ab + b²     a² - b² = (a + b)(a - b)

Степени (знак ^ означает возведение в степень)
a^n · a^m = a^(n+m)     a^n : a^m = a^(n-m)     (a^n)^m = a^(n·m)     a^(-n) = 1 : a^n     a⁰ = 1

Квадратный корень
√(a · b) = √a · √b     √(a : b) = √a : √b     (√a)² = a

Квадратное уравнение ax² + bx + c = 0
D = b² - 4ac     x = (-b ± √D) : (2a)

Прогрессии
арифметическая: n-й член равен a₁ + d · (n - 1), сумма первых n членов равна (a₁ + aₙ) · n : 2
геометрическая: n-й член равен b₁ · q^(n-1)

Логарифмы
log (b · c) = log b + log c     log (b : c) = log b - log c     log (b^n) = n · log b
(основание логарифмов одинаковое)

Вероятность
P = m : n, где m это число благоприятных исходов, n это число всех исходов

Таблица квадратов
11² = 121   12² = 144   13² = 169   14² = 196   15² = 225   16² = 256   17² = 289   18² = 324   19² = 361
20² = 400   21² = 441   22² = 484   23² = 529   24² = 576   25² = 625

Площади
треугольник: a · h : 2     прямоугольный треугольник: a · b : 2, c² = a² + b²
прямоугольник: a · b     параллелограмм: a · h     трапеция: (a + b) : 2 · h
круг: πr²     длина окружности: 2πr

Объёмы и поверхности
куб: a³     прямоугольный параллелепипед: a · b · c     цилиндр: πr²h     конус: πr²h : 3
шар: 4πr³ : 3     площадь сферы: 4πr²

Значения тригонометрических функций
угол      0°     30°     45°     60°     90°
sin       0      1/2     √2/2    √3/2    1
cos       1      √3/2    √2/2    1/2     0
tg        0      √3/3    1       √3      нет

sin²α + cos²α = 1     tg α = sin α : cos α]]

-- Какие вкладки есть у предмета. Если предмета здесь нет, справочных материалов на экзамене не дают.
local TABS = {
	chemistry = {
		{ title = "Таблица Менделеева", build = buildPeriodicTable },
		{ title = "Ряд активности металлов", build = function(parent)
			buildSheet(parent, ACTIVITY_SERIES)
		end },
		{ title = "Калькулятор", build = buildCalculator },
	},
	physics = {
		{ title = "Справочные данные", build = function(parent)
			buildSheet(parent, PHYSICS_SHEET)
		end },
		{ title = "Калькулятор", build = buildCalculator },
	},
	math_base = {
		{ title = "Формулы", build = function(parent)
			buildSheet(parent, MATH_BASE_SHEET)
		end },
	},
	math_prof = {
		{ title = "Формулы", build = function(parent)
			buildSheet(parent, MATH_PROFILE_SHEET)
		end },
	},
	geography = {
		{ title = "Калькулятор", build = buildCalculator },
	},
}

function Reference.hasMaterials(subjectId: string): boolean
	return TABS[subjectId] ~= nil
end

-- Создаёт окно справочных материалов поверх экрана экзамена. Возвращает { open(subjectId), close(), isOpen() }.
function Reference.create(parent: Instance)
	local panel = {}
	local content: Frame? = nil
	local tabButtons = {}

	local frame = Ui.frame({
		Name = "Reference",
		Size = UDim2.fromScale(1, 1),
		Active = true,
		Visible = false,
		ZIndex = 25,
		Parent = parent,
	}, { Ui.corner(14) })
	local header = Ui.frame({ Size = UDim2.new(1, 0, 0, 56), BackgroundColor3 = C.sunken, Parent = frame }, { Ui.corner(14) })
	Ui.label({
		Text = "Справочные материалы",
		Font = Ui.fonts.bold,
		TextSize = 18,
		Position = UDim2.fromOffset(20, 0),
		Size = UDim2.fromOffset(260, 56),
		Parent = header,
	})
	local closeButton = Ui.button("Вернуться к заданию", "primary", {
		Name = "Close",
		Position = UDim2.new(1, -236, 0, 9),
		Size = UDim2.fromOffset(220, 38),
		Parent = header,
	})
	local tabRow = Ui.frame({
		Position = UDim2.fromOffset(20, 64),
		Size = UDim2.new(1, -40, 0, 36),
		BackgroundTransparency = 1,
		Parent = frame,
	})
	local body = Ui.frame({
		Name = "Body",
		Position = UDim2.fromOffset(20, 106),
		Size = UDim2.new(1, -40, 1, -122),
		BackgroundTransparency = 1,
		Parent = frame,
	})

	local function clear()
		if content then
			content:Destroy()
			content = nil
		end
	end

	local function showTab(tabs, index: number)
		clear()
		content = Ui.frame({ Name = "Content", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Parent = body })
		tabs[index].build(content)
		for buttonIndex, button in tabButtons do
			Ui.styleButton(button, if buttonIndex == index then "selected" else "plain")
		end
	end

	function panel.open(subjectId: string)
		local tabs = TABS[subjectId]
		if not tabs then
			return
		end
		for _, button in tabButtons do
			button:Destroy()
		end
		tabButtons = {}
		for index, tab in tabs do
			local button = Ui.button(tab.title, "plain", {
				Name = "Tab" .. index,
				TextSize = 15,
				Position = UDim2.fromOffset((index - 1) * 250, 0),
				Size = UDim2.fromOffset(240, 36),
				Parent = tabRow,
			})
			button.Activated:Connect(function()
				showTab(tabs, index)
			end)
			tabButtons[index] = button
		end
		showTab(tabs, 1)
		frame.Visible = true
	end

	function panel.close()
		frame.Visible = false
		clear()
	end

	function panel.isOpen(): boolean
		return frame.Visible
	end

	closeButton.Activated:Connect(panel.close)
	return panel
end

return Reference
