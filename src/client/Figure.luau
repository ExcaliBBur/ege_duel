-- Рисунок к заданию. Сервер присылает список простых фигур, клиент рисует их рамками и подписями:
-- картинки-файлы не нужны.
--   { "line", x1, y1, x2, y2, стиль }     стиль: 0 сетка, 1 основная линия, 2 выделенная линия
--   { "rect", x, y, ширина, высота, стиль }
--   { "circle", x, y, радиус, стиль }      стиль 1: белый круг с обводкой, 2: закрашенная точка
--   { "text", x, y, строка, выравнивание }  выравнивание: "c", "l", "r"
local Ui = require(script.Parent.Ui)

local Figure = {}

local C = Ui.colors

local LINE_STYLES = {
	[0] = { color = C.line, thickness = 1, z = 1 },
	[1] = { color = C.ink, thickness = 2, z = 2 },
	[2] = { color = C.accent, thickness = 3, z = 3 },
}

local ALIGNMENTS = {
	c = { anchor = 0.5, enum = Enum.TextXAlignment.Center },
	l = { anchor = 0, enum = Enum.TextXAlignment.Left },
	r = { anchor = 1, enum = Enum.TextXAlignment.Right },
}

local function drawLine(parent: Instance, x1: number, y1: number, x2: number, y2: number, styleId: number)
	local style = LINE_STYLES[styleId] or LINE_STYLES[1]
	local dx, dy = x2 - x1, y2 - y1
	Ui.frame({
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromOffset((x1 + x2) / 2, (y1 + y2) / 2),
		Size = UDim2.fromOffset(math.sqrt(dx * dx + dy * dy), style.thickness),
		Rotation = math.deg(math.atan2(dy, dx)),
		BackgroundColor3 = style.color,
		ZIndex = style.z,
		Parent = parent,
	})
end

-- Создаёт рамку с рисунком. Возвращает nil, если рисунка нет.
function Figure.render(figure: any, parent: Instance?): Frame?
	if type(figure) ~= "table" or type(figure.items) ~= "table" then
		return nil
	end
	local canvas = Ui.frame({
		Name = "Figure",
		Size = UDim2.fromOffset(figure.w or 420, figure.h or 260),
		BackgroundColor3 = C.surface,
		ClipsDescendants = true,
	}, { Ui.corner(6), Ui.stroke(C.line, 1) })

	for _, shape in figure.items do
		local kind = shape[1]
		if kind == "line" then
			drawLine(canvas, shape[2], shape[3], shape[4], shape[5], shape[6])
		elseif kind == "rect" then
			local style = LINE_STYLES[shape[6]] or LINE_STYLES[2]
			Ui.frame({
				Position = UDim2.fromOffset(shape[2], shape[3]),
				Size = UDim2.fromOffset(shape[4], shape[5]),
				BackgroundColor3 = style.color,
				ZIndex = style.z,
				Parent = canvas,
			})
		elseif kind == "circle" then
			local radius = shape[4]
			local filled = shape[5] == 2
			Ui.frame({
				AnchorPoint = Vector2.new(0.5, 0.5),
				Position = UDim2.fromOffset(shape[2], shape[3]),
				Size = UDim2.fromOffset(radius * 2, radius * 2),
				BackgroundColor3 = if filled then C.accent else C.surface,
				ZIndex = 4,
				Parent = canvas,
			}, { Ui.new("UICorner", { CornerRadius = UDim.new(1, 0) }), Ui.stroke(if filled then C.accent else C.ink, 2) })
		elseif kind == "text" then
			local alignment = ALIGNMENTS[shape[5]] or ALIGNMENTS.c
			Ui.label({
				Text = shape[4],
				Font = Ui.fonts.bold,
				TextSize = 14,
				TextWrapped = false,
				TextXAlignment = alignment.enum,
				AnchorPoint = Vector2.new(alignment.anchor, 0.5),
				Position = UDim2.fromOffset(shape[2], shape[3]),
				Size = UDim2.fromOffset(120, 18),
				ZIndex = 5,
				Parent = canvas,
			})
		end
	end

	canvas.Parent = parent
	return canvas
end

return Figure
