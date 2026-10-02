"""Русский язык, литература и английский язык: вторая часть. Все ответы развёрнутые, их оценивает соперник.

Сочинение по русскому языку пишется по тому же тексту, что и задания 23-26 (общее поле context).
Стихотворения для литературы взяты у авторов XIX века, их тексты находятся в общественном достоянии.
"""

import exam_russian
from exam_common import Entry, essay, essays

# ================================================================ русский язык, №27

ESSAY_CRITERIA = [
    "К1, 1 балл: верно сформулирована позиция автора по указанной проблеме.",
    "К2, до 3 баллов: комментарий с двумя примерами-иллюстрациями из текста, пояснениями к ним и указанной смысловой связью между примерами.",
    "К3, до 2 баллов: выражено собственное отношение к позиции автора и приведён пример-аргумент (из жизни, литературы или истории).",
    "К4, 1 балл: нет фактических ошибок.",
    "К5, до 2 баллов: логичность, связность, деление на абзацы.",
    "К6, 1 балл: соблюдены этические нормы.",
    "К7, до 3 баллов: орфография (3 балла без ошибок, далее по баллу за каждые одну-две ошибки).",
    "К8, до 3 баллов: пунктуация (по той же шкале).",
    "К9, до 3 баллов: грамматические нормы.",
    "К10, до 3 баллов: речевые нормы, точность и выразительность речи.",
    "Сочинение не по тексту, пересказ или объём меньше 70 слов: 0 баллов за всю работу.",
]

STORY_KEYS = [
    ("Проблема самостоятельности в воспитании: нужно ли давать человеку возможность сделать дело самому, даже если получится неидеально?",
     "Позиция автора: настоящая помощь иногда состоит в том, чтобы не вмешиваться; взрослый не должен отнимать у ребёнка радость первой собственной работы. "
     "Примеры из текста: дед молчит на крыльце, хотя ему хочется взять молоток (предложение 5); дед серьёзно хвалит кривой скворечник (7); "
     "повзрослевший рассказчик понимает цену этого молчания (10-12)."),
    ("Проблема роли учителя: чему на самом деле учит человека настоящий учитель?",
     "Позиция автора: главный урок учителя может быть шире предмета; Анна Павловна через музыку и выступления учила детей не бояться людей. "
     "Примеры из текста: обязательные концерты во дворе, которые сначала казались мучением (6-8); со временем «вчерашний трусишка» выходит к слушателям спокойно (9); "
     "вывод рассказчика о том, чему учила Анна Павловна (10-12)."),
    ("Проблема бескорыстного труда ради будущего: зачем делать дело, плодов которого не увидишь сам?",
     "Позиция автора: человек измеряется не тем, что он успел взять, а тем, что оставил другим. Примеры из текста: лесник под семьдесят сажает кедры, "
     "которые дадут шишки через сорок лет (1-3); он не спорит с насмешниками и кивает на старые кедры, посаженные не для себя (5-6); "
     "теперь в роще играют дети и собирают орехи (9-11)."),
]

assert len(STORY_KEYS) == len(exam_russian.STORIES)

RUSSIAN_TASKS = []
for story_index, (story, (problem, key)) in enumerate(zip(exam_russian.STORIES, STORY_KEYS)):
    made = essay(
        "Прочитайте текст и напишите по нему сочинение.\n\n" + story["text"] + "\n\n"
        "Сформулируйте позицию автора по одной из проблем текста. Прокомментируйте, как в тексте раскрывается эта позиция: приведите два примера-иллюстрации из прочитанного текста, "
        "поясните их и укажите смысловую связь между ними. Сформулируйте и обоснуйте своё отношение к позиции автора, приведите пример-аргумент.\n\n"
        "Объём сочинения в игре: не менее 100 слов (на экзамене не менее 150).",
        problem + " " + key,
        ESSAY_CRITERIA,
    )
    made["context"] = f"story:{story_index}"
    RUSSIAN_TASKS.append(made)

RUSSIAN = [Entry(27, "Сочинение по прочитанному тексту", 22, [essays("r27_essay", RUSSIAN_TASKS)])]

# ================================================================ литература

POEMS = [
    ("А. С. Пушкин", "Я вас любил…",
     "Я вас любил: любовь ещё, быть может,\nВ душе моей угасла не совсем;\nНо пусть она вас больше не тревожит;\nЯ не хочу печалить вас ничем.\n"
     "Я вас любил безмолвно, безнадежно,\nТо робостью, то ревностью томим;\nЯ вас любил так искренно, так нежно,\nКак дай вам Бог любимой быть другим.",
     "Каким предстаёт чувство лирического героя в этом стихотворении?",
     "Любовь героя бескорыстна и благородна: он не требует ответа, а желает любимой счастья с другим. Чувство не угасло («угасла не совсем»), но герой сдерживает его, "
     "чтобы не тревожить её. Анафора «Я вас любил» трижды возвращает к главной мысли, наречия «безмолвно, безнадежно», «искренно, нежно» раскрывают глубину и чистоту чувства; "
     "финальное пожелание превращает признание в самоотречение.",
     "В каких произведениях отечественной поэзии звучит тема любви и в чём эти произведения можно сопоставить со стихотворением Пушкина?",
     "Возможные произведения: «Я встретил вас…» Ф. И. Тютчева (чувство, оживающее спустя годы, светлая благодарность); «Я помню чудное мгновенье…» А. С. Пушкина "
     "(любовь как возрождение души); «Письмо к женщине» С. А. Есенина (прощание без упрёка); лирика М. Ю. Лермонтова («Нищий»: любовь отвергнутая и горькая, в отличие от пушкинского смирения). "
     "Нужно назвать автора и произведение и показать сходство или различие в раскрытии темы."),
    ("М. Ю. Лермонтов", "Парус",
     "Белеет парус одинокой\nВ тумане моря голубом!..\nЧто ищет он в стране далёкой?\nЧто кинул он в краю родном?..\n\n"
     "Играют волны — ветер свищет,\nИ мачта гнётся и скрыпит…\nУвы! он счастия не ищет\nИ не от счастия бежит!\n\n"
     "Под ним струя светлей лазури,\nНад ним луч солнца золотой…\nА он, мятежный, просит бури,\nКак будто в бурях есть покой!",
     "Какой смысл приобретает образ паруса в этом стихотворении?",
     "Парус символизирует одинокую мятежную душу романтического героя. Каждая строфа строится на контрасте пейзажа и размышления: спокойное море, буря, снова ясная картина, "
     "но герой не находит покоя ни в чём и «просит бури». Эпитеты «одинокой», «мятежный», риторические вопросы и восклицания, антитеза бури и покоя передают внутренний разлад, "
     "жажду борьбы и неудовлетворённость жизнью.",
     "В каких произведениях отечественной поэзии звучит тема одиночества и в чём эти произведения можно сопоставить со стихотворением Лермонтова?",
     "Возможные произведения: «Выхожу один я на дорогу…» и «Тучи» М. Ю. Лермонтова (одиночество, поиск покоя и свободы); «Узник» А. С. Пушкина (порыв к свободе); "
     "«Послушайте!» В. В. Маяковского (одиночество человека, которому нужна «звезда»); лирика А. А. Блока. Нужно назвать автора и произведение и показать, "
     "чем сходны или различны образы и настроение."),
    ("А. А. Фет", "Шёпот, робкое дыханье…",
     "Шёпот, робкое дыханье,\nТрели соловья,\nСеребро и колыханье\nСонного ручья,\n\nСвет ночной, ночные тени,\nТени без конца,\nРяд волшебных изменений\nМилого лица,\n\n"
     "В дымных тучках пурпур розы,\nОтблеск янтаря,\nИ лобзания, и слёзы,\nИ заря, заря!..",
     "Как в этом стихотворении связаны мир природы и мир человеческих чувств?",
     "Природа и чувства слиты в одно впечатление: ночное свидание показано через звуки и краски (шёпот, трели соловья, серебро ручья, пурпур зари), которые чередуются с переживаниями влюблённых. "
     "В стихотворении нет ни одного глагола: назывные предложения передают мгновенные ощущения, а смена ночи зарёй соответствует нарастанию чувства. "
     "Повторы («тени», «заря, заря»), эпитеты и метафоры создают музыкальность и ощущение счастья.",
     "В каких произведениях отечественной поэзии изображение природы связано с душевным состоянием человека и в чём эти произведения можно сопоставить со стихотворением Фета?",
     "Возможные произведения: «Есть в осени первоначальной…» и «Весенняя гроза» Ф. И. Тютчева (одушевлённая природа, созвучная чувству); «Зимнее утро» А. С. Пушкина "
     "(радость, слитая с пейзажем); «Отговорила роща золотая…» С. А. Есенина (осень как пора подведения итогов жизни). Нужно назвать автора и произведение и показать сходство или различие."),
]

SIX_POINTS = [
    "До 2 баллов: дан прямой связный ответ на вопрос, авторская позиция не искажена.",
    "До 2 баллов: для аргументации привлекается текст произведения (анализ деталей, образов, средств выразительности), без фактических ошибок.",
    "До 2 баллов: логичность и речевая грамотность ответа.",
    "Если ответ не соответствует вопросу, вся работа оценивается в 0 баллов. Рекомендуемый объём: 5-10 предложений.",
]

EIGHT_POINTS = [
    "До 2 баллов: названо произведение и его автор, произведение подходит для сопоставления.",
    "До 2 баллов: выбранное произведение убедительно сопоставлено с исходным в заданном направлении.",
    "До 2 баллов: привлекается текст обоих произведений, нет фактических ошибок.",
    "До 2 баллов: логичность и речевая грамотность ответа.",
    "Если произведение не названо или не подходит, вся работа оценивается в 0 баллов.",
]

LYRIC_TASKS, COMPARE_TASKS = [], []
for poem_index, (author, title, text, question, key, compare_question, compare_key) in enumerate(POEMS):
    head = f"Прочитайте стихотворение.\n\n{author}. «{title}»\n\n{text}\n\n"
    first = essay(head + question + " Дайте прямой связный ответ (5-10 предложений), опираясь на текст.", key, SIX_POINTS)
    second = essay(head + compare_question + " Назовите одно произведение и его автора, обоснуйте свой выбор (5-10 предложений).", compare_key, EIGHT_POINTS)
    first["context"] = second["context"] = f"lyric:{poem_index}"
    LYRIC_TASKS.append(first)
    COMPARE_TASKS.append(second)

PROSE = [
    ("Почему Пётр Гринёв в повести А. С. Пушкина «Капитанская дочка» отказывается присягнуть Пугачёву, хотя это грозит ему казнью, и как этот поступок характеризует героя?",
     "Гринёв верен дворянской присяге и отцовскому наказу беречь честь смолоду: для него клятва императрице важнее жизни. Он не лжёт Пугачёву даже ради спасения "
     "и прямо говорит, что не может обещать не воевать против него. Поступок показывает нравственную стойкость, честность и взросление героя; именно прямота вызывает уважение Пугачёва."),
    ("Почему Печорин, герой романа М. Ю. Лермонтова «Герой нашего времени», приносит несчастье людям, с которыми сближается?",
     "Печорин незаурядная личность, не нашедшая применения своим силам: от скуки он вмешивается в чужие судьбы и ставит над людьми опыты (Бэла, княжна Мери, Грушницкий). "
     "Он эгоистичен, не способен жертвовать собой ради другого, но при этом беспощадно судит себя в дневнике. Автор показывает в нём болезнь поколения: ум и воля тратятся впустую."),
    ("Что объединяет помещиков, которых посещает Чичиков в поэме Н. В. Гоголя «Мёртвые души», и почему поэма названа именно так?",
     "Манилов, Коробочка, Ноздрёв, Собакевич и Плюшкин различны по характеру, но все духовно мертвы: живут пустыми мечтами, накопительством, буйством или скупостью, "
     "не думая ни о людях, ни о пользе. «Мёртвые души» это не только умершие крестьяне, которых скупает Чичиков, но и сами помещики и чиновники. "
     "Галерея выстроена по нарастанию омертвения, вершиной которого становится Плюшкин."),
    ("Почему Катерина, героиня драмы А. Н. Островского «Гроза», публично признаётся в своём грехе?",
     "Катерина искренна и глубоко религиозна, она не умеет лгать и жить двойной жизнью, как Варвара. Тайная любовь к Борису для неё грех, муки совести усиливаются грозой, "
     "которую она воспринимает как божью кару, и словами сумасшедшей барыни. Признание становится протестом цельной натуры против лжи «тёмного царства» и ведёт к трагической развязке."),
]

PROSE_TASKS = [essay(text + " Дайте прямой связный ответ (5-10 предложений), опираясь на текст произведения.", key, SIX_POINTS) for text, key in PROSE]

COMPOSITION_POINTS = [
    "До 3 баллов: сочинение соответствует теме, тема раскрыта глубоко и многосторонне.",
    "До 3 баллов: привлекается текст произведения (эпизоды, образы, детали), нет фактических ошибок.",
    "До 3 баллов: уместно использованы теоретико-литературные понятия.",
    "До 3 баллов: композиционная цельность и логичность.",
    "До 3 баллов: соблюдение речевых норм.",
    "До 3 баллов: грамотность (орфография, пунктуация, грамматика).",
    "Если сочинение не соответствует теме или его объём меньше 100 слов, вся работа оценивается в 0 баллов.",
]

COMPOSITIONS = [
    ("Тема «маленького человека» в русской литературе XIX века (на примере одного-двух произведений).",
     "Возможные произведения: «Станционный смотритель» А. С. Пушкина (Самсон Вырин), «Шинель» Н. В. Гоголя (Акакий Акакиевич Башмачкин), «Бедные люди» Ф. М. Достоевского (Макар Девушкин). "
     "Нужно показать: незаметное положение героя в обществе, его беззащитность, сочувствие автора, гуманистический пафос («Я брат твой» у Гоголя), развитие темы от Пушкина к Достоевскому."),
    ("Проблема чести и долга в повести А. С. Пушкина «Капитанская дочка».",
     "Нужно показать: смысл эпиграфа «Береги честь смолоду»; поведение Гринёва (отказ присягать Пугачёву, верность Маше), противопоставление Гринёва и Швабрина; "
     "верность долгу капитана Миронова и его жены; честь как нравственный закон, а не сословная привилегия (отношения Гринёва и Пугачёва)."),
    ("Образ «лишнего человека» в русской литературе XIX века (по роману «Евгений Онегин» или «Герой нашего времени»).",
     "Нужно показать: незаурядность героя и его разлад с обществом; разочарование, скуку, неспособность найти дело и счастье; испытание любовью и дружбой "
     "(Онегин и Татьяна, Ленский; Печорин и Вера, Мери, Грушницкий); отношение автора к герою, связь образа с эпохой."),
    ("Тема подвига и нравственного выбора человека на войне в отечественной литературе XX века (на примере одного-двух произведений).",
     "Возможные произведения: «Судьба человека» М. А. Шолохова, «Василий Тёркин» А. Т. Твардовского, «А зори здесь тихие…» Б. Л. Васильева, «Сотников» В. В. Быкова. "
     "Нужно показать: испытания героя, цену выбора между жизнью и долгом, источник стойкости (любовь к Родине, ответственность за других), авторскую оценку."),
]

COMPOSITION_TASKS = [
    essay(f"Напишите сочинение на тему: «{theme}»\n\nОпирайтесь на текст произведений, используйте литературоведческие понятия. "
          "Объём сочинения в игре: не менее 100 слов (на экзамене не менее 200).", key, COMPOSITION_POINTS)
    for theme, key in COMPOSITIONS
]

LITERATURE = [
    Entry(4, "Развёрнутый ответ по эпическому или драматическому произведению", 6, [essays("l4_prose", PROSE_TASKS)]),
    Entry(10, "Анализ лирического произведения", 6, [essays("l10_lyric", LYRIC_TASKS)]),
    Entry(11, "Сопоставление произведений", 8, [essays("l11_compare", COMPARE_TASKS)]),
    Entry(12, "Сочинение на литературную тему", 18, [essays("l12_composition", COMPOSITION_TASKS)]),
]

# ================================================================ английский язык

EMAIL_POINTS = [
    "Up to 2 points: the content is complete: all three questions of the friend are answered and three questions on the given topic are asked; the style is informal.",
    "Up to 2 points: the text is logical and well organised: greeting, thanks for the email, paragraphs, a closing line and a signature.",
    "Up to 2 points: vocabulary, grammar and spelling are appropriate, with no more than a few minor mistakes.",
    "0 points for the whole task if the content does not match the task or the text is shorter than 90 words.",
]

EMAILS = [
    ("Ben", "…Last weekend I finally learned to cook a real dinner for my family, and they loved it! Can you cook? What dishes are popular in your country? "
            "Who usually cooks at home in your family?\n\nBy the way, we have just got a puppy…", "the puppy",
     "A good answer thanks Ben for his email, answers the three questions (whether the writer can cook, which dishes are popular in Russia, for example borscht or pelmeni, "
     "and who cooks at home) and asks three questions about the puppy (for example its name, breed and who looks after it)."),
    ("Emily", "…Our school has started a recycling project, and my class is collecting plastic bottles. Do you sort rubbish at home? What environmental problems are there "
              "in your town? What can teenagers do to protect nature?\n\nNext month I am going on a school trip to Scotland…", "the school trip",
     "A good answer thanks Emily, answers the three questions (sorting rubbish at home, local environmental problems such as air pollution or litter, "
     "what teenagers can do: clean-up days, saving water and energy) and asks three questions about the trip to Scotland (for example how long it lasts, what they will visit, who is going)."),
    ("Tom", "…I have joined the school chess club, and now I play almost every evening. What do you usually do after school? Which hobby would you like to take up, and why? "
            "Do you prefer spending free time alone or with friends?\n\nMy elder sister has just passed her driving test…", "his sister's driving test",
     "A good answer thanks Tom, answers the three questions (after-school activities, a hobby the writer would like to try with a reason, preference for free time alone or with friends) "
     "and asks three questions about the driving test (for example how long she studied, whether it was difficult, whether she has a car)."),
]

EMAIL_TASKS = [
    essay(f"You have received an email message from your English-speaking pen-friend {name}:\n\n{letter}\n\n"
          f"Write an email to {name}. In your message answer the questions and ask 3 questions about {topic}.\n\n"
          "Write 100-140 words. Remember the rules of email writing.", key, EMAIL_POINTS)
    for name, letter, topic, key in EMAILS
]

PROJECT_POINTS = [
    "Up to 3 points: all five points of the plan are covered and the data from the table are used correctly.",
    "Up to 3 points: the text is logical, divided into paragraphs and uses linking words.",
    "Up to 3 points: the vocabulary is varied and appropriate.",
    "Up to 3 points: the grammar is accurate and varied.",
    "Up to 2 points: spelling and punctuation.",
    "0 points for the whole task if the content does not match the task or the text is shorter than 150 words.",
]

PROJECTS = [
    ("how teenagers in Zetland spend their free time", "Free time activity: share of teenagers (%)",
     [("Surfing the Internet", 42), ("Doing sports", 21), ("Reading books", 14), ("Meeting friends", 18), ("Volunteering", 5)],
     "a problem that can arise with spending free time",
     "A good answer opens with an introduction to the topic; reports two or three facts (the Internet is the most popular activity with 42%, volunteering is the least popular with 5%); "
     "makes one or two comparisons (for example, sport is half as popular as the Internet, and reading is less popular than meeting friends); "
     "names a problem (for example too much screen time harms health) and suggests a solution; ends with a conclusion and the writer's opinion on the role of free time."),
    ("why students in Zetland learn foreign languages", "Reason: share of students (%)",
     [("To get a good job", 38), ("To travel", 27), ("To study abroad", 16), ("To watch films and read books", 12), ("To make friends", 7)],
     "a problem that can arise in learning a foreign language",
     "A good answer opens with an introduction; reports two or three facts (a good job is the main reason with 38%, making friends is the least common with 7%); "
     "makes one or two comparisons (for example, travelling is almost twice as popular a reason as studying abroad); names a problem (for example lack of speaking practice) "
     "and suggests a solution (language clubs, online conversations); ends with a conclusion and the writer's opinion on the importance of languages."),
    ("what kinds of books teenagers in Zetland prefer", "Kind of books: share of teenagers (%)",
     [("Fantasy", 35), ("Detective stories", 24), ("Science fiction", 19), ("Classics", 13), ("Poetry", 9)],
     "a problem that can arise with reading books",
     "A good answer opens with an introduction; reports two or three facts (fantasy is the most popular kind with 35%, poetry is the least popular with 9%); "
     "makes one or two comparisons (for example, detective stories are more popular than science fiction, classics are read almost three times less than fantasy); "
     "names a problem (for example teenagers read less because of gadgets) and suggests a solution; ends with a conclusion and the writer's opinion on reading."),
]

PROJECT_TASKS = [
    essay(f"Imagine that you are doing a project on {topic}. You have found some data on the subject, the results of an opinion poll:\n\n{header}\n"
          + "\n".join(f"{name}: {value}" for name, value in rows)
          + "\n\nComment on the data and give your opinion on the subject of the project. Write 200-250 words. Use the following plan:\n"
          "- make an opening statement on the subject of the project;\n- select and report 2-3 facts;\n- make 1-2 comparisons where relevant and give your comments;\n"
          f"- outline {problem} and suggest a way of solving it;\n- conclude by giving and explaining your opinion on the subject.", key, PROJECT_POINTS)
    for topic, header, rows, problem, key in PROJECTS
]

ENGLISH = [
    Entry(37, "Электронное письмо личного характера", 6, [essays("e37_email", EMAIL_TASKS)]),
    Entry(38, "Письменное высказывание с элементами рассуждения по таблице", 14, [essays("e38_project", PROJECT_TASKS)]),
]
