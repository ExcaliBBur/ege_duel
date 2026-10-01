-- Общие цвета и заготовки элементов интерфейса.
local Ui = {}

Ui.colors = {
	surface = Color3.fromRGB(255, 255, 255),
	sunken = Color3.fromRGB(240, 235, 242),
	ink = Color3.fromRGB(27, 20, 32),
	muted = Color3.fromRGB(107, 96, 114),
	line = Color3.fromRGB(224, 216, 228),
	accent = Color3.fromRGB(184, 21, 90), -- вы
	accentSoft = Color3.fromRGB(251, 227, 237),
	rival = Color3.fromRGB(13, 118, 128), -- соперник
	rivalSoft = Color3.fromRGB(221, 241, 242),
	ok = Color3.fromRGB(28, 127, 71),
	okSoft = Color3.fromRGB(223, 243, 231),
	warn = Color3.fromRGB(154, 98, 8),
	warnSoft = Color3.fromRGB(251, 239, 211),
	danger = Color3.fromRGB(190, 40, 40),
	dangerSoft = Color3.fromRGB(250, 226, 226),
}

Ui.fonts = {
	regular = Enum.Font.GothamMedium,
	bold = Enum.Font.GothamBold,
	display = Enum.Font.GothamBlack,
	mono = Enum.Font.RobotoMono,
}

-- Создаёт объект, задаёт свойства и вкладывает детей.
function Ui.new(className: string, props: { [string]: any }?, children: { Instance }?): any
	local instance = Instance.new(className)
	local parent = nil
	for key, value in props or {} do
		if key == "Parent" then
			parent = value
		else
			(instance :: any)[key] = value
		end
	end
	for _, child in children or {} do
		child.Parent = instance
	end
	if parent then
		instance.Parent = parent
	end
	return instance
end

function Ui.corner(radius: number): UICorner
	return Ui.new("UICorner", { CornerRadius = UDim.new(0, radius) })
end

function Ui.stroke(color: Color3, thickness: number?): UIStroke
	return Ui.new("UIStroke", {
		Color = color,
		Thickness = thickness or 1,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
	})
end

function Ui.frame(props: { [string]: any }?, children: { Instance }?): Frame
	local merged = { BackgroundColor3 = Ui.colors.surface, BorderSizePixel = 0 }
	for key, value in props or {} do
		merged[key] = value
	end
	return Ui.new("Frame", merged, children)
end

function Ui.label(props: { [string]: any }?): TextLabel
	local merged = {
		BackgroundTransparency = 1,
		Font = Ui.fonts.regular,
		TextSize = 16,
		TextColor3 = Ui.colors.ink,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextYAlignment = Enum.TextYAlignment.Center,
		TextWrapped = true,
		Text = "",
	}
	for key, value in props or {} do
		merged[key] = value
	end
	return Ui.new("TextLabel", merged)
end

-- Маленькая надпись заглавными буквами над блоком.
function Ui.caption(text: string, props: { [string]: any }?): TextLabel
	local merged = {
		Text = text,
		Font = Ui.fonts.bold,
		TextSize = 12,
		TextColor3 = Ui.colors.muted,
		Size = UDim2.new(1, 0, 0, 16),
	}
	for key, value in props or {} do
		merged[key] = value
	end
	return Ui.label(merged)
end

-- Цветная плашка с текстом.
function Ui.pill(text: string, textColor: Color3, backColor: Color3, props: { [string]: any }?): TextLabel
	local merged = {
		Text = text,
		Font = Ui.fonts.bold,
		TextSize = 14,
		TextColor3 = textColor,
		BackgroundColor3 = backColor,
		BackgroundTransparency = 0,
		TextXAlignment = Enum.TextXAlignment.Center,
		TextWrapped = false,
		TextTruncate = Enum.TextTruncate.AtEnd,
		Size = UDim2.fromOffset(200, 26),
	}
	for key, value in props or {} do
		merged[key] = value
	end
	local pill = Ui.label(merged)
	Ui.corner(13).Parent = pill
	return pill
end

local BUTTON_STYLES = {
	primary = { back = "accent", text = "surface", line = "accent" },
	plain = { back = "surface", text = "ink", line = "line" },
	selected = { back = "accentSoft", text = "accent", line = "accent" },
	rival = { back = "rivalSoft", text = "rival", line = "rival" },
	warn = { back = "warnSoft", text = "warn", line = "warn" },
	danger = { back = "dangerSoft", text = "danger", line = "danger" },
	disabled = { back = "sunken", text = "muted", line = "line" },
}

-- Меняет оформление кнопки: primary, plain, selected, rival, warn, danger, disabled.
function Ui.styleButton(button: TextButton, style: string)
	local spec = BUTTON_STYLES[style] or BUTTON_STYLES.plain
	button.BackgroundColor3 = Ui.colors[spec.back]
	button.TextColor3 = Ui.colors[spec.text]
	local stroke = button:FindFirstChildOfClass("UIStroke")
	if stroke then
		stroke.Color = Ui.colors[spec.line]
	end
	button.Active = style ~= "disabled"
	button.AutoButtonColor = style ~= "disabled"
end

function Ui.button(text: string, style: string, props: { [string]: any }?): TextButton
	local merged = {
		Text = text,
		Font = Ui.fonts.bold,
		TextSize = 16,
		BorderSizePixel = 0,
		Size = UDim2.fromOffset(160, 44),
		TextWrapped = true,
	}
	for key, value in props or {} do
		merged[key] = value
	end
	local button = Ui.new("TextButton", merged, { Ui.corner(8), Ui.stroke(Ui.colors.line, 1.5) })
	Ui.styleButton(button, style)
	return button
end

-- "мм:сс" из числа секунд.
function Ui.clock(seconds: number): string
	seconds = math.max(0, math.ceil(seconds))
	return string.format("%02d:%02d", seconds // 60, seconds % 60)
end

-- Форма слова по числу: plural(3, "задание", "задания", "заданий").
function Ui.plural(n: number, one: string, few: string, many: string): string
	local tens, units = n % 100, n % 10
	if tens >= 11 and tens <= 14 then
		return many
	elseif units == 1 then
		return one
	elseif units >= 2 and units <= 4 then
		return few
	end
	return many
end

return Ui
