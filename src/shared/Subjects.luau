-- Список предметов. id совпадает с именем файла в bank/dist.
local Subjects = {}

Subjects.list = {
	{ id = "russian", name = "Русский язык" },
	{ id = "math_base", name = "Математика, база" },
	{ id = "math_prof", name = "Математика, профиль" },
	{ id = "physics", name = "Физика" },
	{ id = "chemistry", name = "Химия" },
	{ id = "biology", name = "Биология" },
	{ id = "informatics", name = "Информатика" },
	{ id = "history", name = "История" },
	{ id = "social", name = "Обществознание" },
	{ id = "geography", name = "География" },
	{ id = "literature", name = "Литература" },
	{ id = "english", name = "Английский язык" },
}

Subjects.byId = {}
for _, subject in Subjects.list do
	Subjects.byId[subject.id] = subject
end

function Subjects.nameOf(id: string?): string
	local subject = id and Subjects.byId[id]
	return if subject then subject.name else "не выбран"
end

return Subjects
