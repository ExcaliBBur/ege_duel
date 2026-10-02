"""Английский язык: задания №10-36 (чтение, грамматика и лексика) по структуре ЕГЭ 2026.

Задания 1-9 (аудирование) требуют звукозаписи и в игру не переносятся. Все тексты написаны для игры.
Задания 12-18 относятся к одному тексту: у них общее поле context, по нему игра подбирает их вместе.
"""

from exam_common import Entry, matching
from generators import task


def numbered(options):
    return "\n".join(f"{index}) {option}" for index, option in enumerate(options, start=1))


# ---------------------------------------------------------------- №10 Заголовки

HEADINGS = [
    ("A long way to school", "Every morning Tim wakes up at five. His village has no school, so he walks three miles to the bus stop and then spends an hour on the bus. "
                             "He says the journey gives him time to think."),
    ("Food from the roof", "In big cities there is little space for gardens, so people have started growing vegetables on the tops of buildings. "
                           "A restaurant in the centre now serves salads picked just a few floors above its kitchen."),
    ("An unusual pet", "Most families choose a cat or a dog. The Greens keep a small pig called Rosie. She sleeps in a basket, follows the children around the house "
                       "and even comes when she is called."),
    ("Music that heals", "Doctors in one hospital noticed that patients who listened to quiet songs needed less medicine and slept better. "
                         "Now a guitarist visits the wards twice a week."),
    ("The price of fame", "The young actor cannot go shopping or sit in a café without being photographed. He says he sometimes misses the days when nobody knew his name."),
    ("Learning without a classroom", "Anna has never been to school. Her parents teach her at home, and she takes lessons online. She studies on trains, in parks and even on the beach."),
    ("A festival of light", "For three nights in winter the old town is covered with lanterns. Visitors walk through the glowing streets, and children carry candles "
                            "they have made themselves."),
    ("Saved by a dog", "When the fire started, everyone in the house was asleep. The family's dog barked until they woke up and then led them to the door through the smoke."),
    ("Too much screen time", "A study shows that teenagers spend about seven hours a day looking at phones and computers. Experts advise switching devices off "
                             "at least an hour before bed."),
    ("A job for the brave", "Cleaning the windows of a skyscraper means hanging on a rope three hundred metres above the street. Workers train for months before their first day."),
    ("The oldest tree", "Scientists believe the pine on the hill is over four thousand years old. Its exact location is kept secret to protect it from tourists."),
    ("Books on wheels", "An old bus has been turned into a library. It travels between villages that have no bookshop, and people can borrow novels for a month."),
]


def e10_headings(r):
    picked = r.sample(HEADINGS, 5)
    texts = picked[:4]
    headings = [heading for heading, _ in picked]
    r.shuffle(headings)
    return matching(
        "Установите соответствие между текстами и заголовками: к каждому тексту, обозначенному буквой, подберите соответствующий заголовок, обозначенный цифрой. "
        "Один заголовок лишний.",
        [text for _, text in texts], headings, "".join(str(headings.index(heading) + 1) for heading, _ in texts),
        "; ".join(f"{letter}: {heading}" for letter, (heading, _) in zip("АБВГ", texts)) + ".")


# ---------------------------------------------------------------- №11 Пропущенные части предложений

GAPPED = [
    ("Iceland is a country (A)______. Although it lies close to the Arctic Circle, the climate is milder (B)______ because of a warm ocean current. "
     "Most Icelanders live in the capital, (C)______. Hot water from under the ground heats their homes, (D)______.",
     ["where volcanoes and glaciers exist side by side", "than many people expect", "which is the northernmost capital in the world", "so the air in the city stays clean"],
     "who have never seen snow"),
    ("The bicycle was invented about two hundred years ago, (A)______. Early models had no pedals, (B)______. Today millions of people cycle to work (C)______. "
     "Many cities are building special lanes (D)______.",
     ["but it became popular only at the end of the nineteenth century", "so riders had to push themselves along with their feet", "because it is cheap and good for their health",
      "to make cycling safer"],
     "which was made of gold"),
    ("Honey never goes bad. Jars found in ancient tombs, (A)______, were still good to eat. Bees make honey from nectar, (B)______. To produce one kilogram of honey, (C)______. "
     "That is why beekeepers say (D)______.",
     ["which were thousands of years old", "which they collect from flowers", "bees have to visit millions of flowers", "that every spoonful is precious"],
     "although they dislike sweet food"),
    ("Chess is one of the oldest games in the world. It appeared in India, (A)______. From there it travelled to Persia and Europe, (B)______. "
     "Today computers play chess so well (C)______. Still, people continue to play (D)______.",
     ["where it was played by four people", "changing its rules on the way", "that even champions cannot beat them", "because they enjoy the battle of minds"],
     "which is why the board is round"),
    ("The first underground railway was opened in London in 1863, (A)______. The trains were pulled by steam engines, (B)______. Electric trains appeared later (C)______. "
     "Today the system carries millions of passengers (D)______.",
     ["when the streets above were full of horses and carts", "so the tunnels were always full of smoke", "and made the journey much cleaner", "who would otherwise travel by car"],
     "that nobody wanted to build"),
]


def e11_gaps(r):
    text, parts, extra = r.choice(GAPPED)
    options = parts + [extra]
    r.shuffle(options)
    made = task(
        "Прочитайте текст и заполните пропуски A-D частями предложений, обозначенными цифрами. Одна из частей лишняя. Запишите цифры в порядке букв ABCD, без пробелов.\n\n"
        f"{text}\n\n{numbered(options)}",
        "".join(str(options.index(part) + 1) for part in parts),
        "; ".join(f"{letter}: {part}" for letter, part in zip("ABCD", parts)) + ".")
    made["kind"] = "order"
    made["key"] = text
    return made


# ---------------------------------------------------------------- №12-18 Полное понимание текста

PASSAGES = [
    ("Mia had always been the quietest girl in her class. She sat at the back, answered only when asked, and spent the breaks reading. So when Mr Hall, the drama teacher, "
     "put her name on the list for the school play, everyone was surprised, and Mia most of all. She was sure it was a mistake and went to tell him so. "
     "'It is not a mistake,' he said. 'I heard you reading a poem to your little brother in the library. You have a voice people want to listen to.' "
     "Mia wanted to refuse, but she could not find the words. The rehearsals were hard. Her hands shook, and she forgot her lines twice. One evening she decided to give up, "
     "but her brother asked her to read him the part of the queen, and he listened with his mouth open. On the night of the play Mia was still afraid. "
     "Yet when she stepped onto the stage and saw her brother in the first row, the fear melted. The audience clapped for a long time. "
     "Later Mr Hall only smiled and said, 'I told you.'",
     [("Before the play, Mia was known as a girl who", "hardly spoke in class", ["liked to argue with teachers", "often acted on stage", "had many friends"]),
      ("Why was Mia surprised to see her name on the list?", "She thought she was not suited for acting.",
       ["She had asked for a different part.", "She did not know Mr Hall.", "She was too busy with her studies."]),
      ("Mr Hall chose Mia because he", "had heard her read aloud", ["wanted to punish her", "was asked to do so by her brother", "needed someone tall"]),
      ("The rehearsals were hard for Mia because she", "was nervous and forgot her words", ["disliked the other actors", "had no time to learn the part", "was ill"]),
      ("What stopped Mia from giving up?", "Her brother's interest in her reading.", ["Mr Hall's promise.", "Her parents' advice.", "The fear of being punished."]),
      ("The phrase 'the fear melted' means that Mia", "stopped being afraid", ["became more frightened", "started to cry", "forgot her lines"]),
      ("Mr Hall's words 'I told you' show that he", "had believed in Mia from the start", ["was angry with Mia", "was surprised by her success", "wanted her to leave the theatre"])]),
    ("When the factory closed, the piece of land behind it turned into a dump. People threw old furniture and broken bicycles there, and the children were told to stay away. "
     "Only Mr Brook, a retired bus driver, kept looking at it from his window. One spring morning he took a spade and began to clear a corner. The neighbours laughed: "
     "the land did not belong to him, and nobody would thank him. Mr Brook did not argue. He planted potatoes and a row of sunflowers. By July the sunflowers were taller "
     "than he was, and people began to stop at the fence. First a boy offered to carry water. Then two women brought seeds. By autumn twenty families had their own beds, "
     "and the dump had become a garden. The town council, which had planned to sell the land for a car park, changed its mind after hundreds of residents signed a letter. "
     "Mr Brook was asked to give a speech at the opening ceremony. He said only one sentence: 'I just did not like the view.'",
     [("After the factory closed, the land behind it", "became a place for rubbish", ["was sold to a farmer", "was turned into a playground", "was used as a car park"]),
      ("Who was Mr Brook?", "A former bus driver.", ["The owner of the factory.", "A member of the town council.", "A professional gardener."]),
      ("How did the neighbours react at first?", "They made fun of him.", ["They helped him at once.", "They called the police.", "They gave him money."]),
      ("What made people change their attitude?", "The sight of the tall sunflowers.", ["An article in a newspaper.", "A speech by the mayor.", "A prize given to Mr Brook."]),
      ("The town council had originally planned to", "sell the land for a car park", ["build a school", "reopen the factory", "plant a forest"]),
      ("The phrase 'changed its mind' means that the council", "made a different decision", ["repeated its decision", "forgot about the land", "asked for more money"]),
      ("Mr Brook's speech shows that he was", "modest", ["proud and talkative", "disappointed", "angry with the council"])]),
    ("For most of history sailors had a serious problem: they could tell how far north or south they were, but not how far east or west. Many ships were lost because "
     "their captains simply did not know where they were. In 1714 the British government offered a huge prize to anyone who could solve the problem. "
     "Famous astronomers believed the answer was in the stars. John Harrison, a carpenter who had taught himself to make clocks, thought differently. "
     "He realised that a ship needed a clock that would keep exact time at sea, in spite of storms and changes of temperature. Nobody had managed to build one. "
     "Harrison worked on his clocks for more than forty years. Each new model was smaller and more accurate than the one before. His fourth clock looked like a large pocket watch, "
     "and on a voyage to Jamaica it lost only five seconds. The scientists who judged the prize did not want to give it to a simple craftsman and kept demanding new tests. "
     "Harrison received the full reward only when he was eighty, after the king himself had taken his side.",
     [("What was the sailors' main problem?", "They could not find their east-west position.",
       ["They had no maps of the stars.", "Their ships were too slow.", "They did not have enough food."]),
      ("The British government", "promised a large reward", ["built a new observatory", "banned long voyages", "hired John Harrison"]),
      ("Unlike the astronomers, Harrison believed the solution was", "an accurate clock", ["a better telescope", "a new kind of ship", "a detailed map"]),
      ("Harrison had learnt to make clocks", "by himself", ["at university", "from his father, an astronomer", "in the navy"]),
      ("What do we learn about Harrison's fourth clock?", "It was very accurate on a long voyage.", ["It was the largest of all.", "It was lost at sea.", "It was made by astronomers."]),
      ("Why was Harrison not given the prize at once?", "The judges did not want to reward a craftsman.",
       ["His clock did not work.", "He refused to take the money.", "The king was against him."]),
      ("Harrison finally got the reward thanks to", "the king's support", ["the astronomers", "his son's letters", "a new test in Jamaica"])]),
]


def reading_question(position):
    def generator(r):
        index = r.randrange(len(PASSAGES))
        passage, questions = PASSAGES[index]
        question, right, wrong = questions[position]
        options = [right] + wrong
        r.shuffle(options)
        made = task(
            f"Прочитайте текст и выполните задание. Запишите цифру, соответствующую выбранному варианту ответа.\n\n{passage}\n\n{question}\n{numbered(options)}",
            str(options.index(right) + 1), f"Верный ответ: {right}")
        made["kind"] = "exact"
        made["context"] = f"reading:{index}"
        made["key"] = f"{index}:{position}"
        return made
    generator.__name__ = f"e{12 + position}_reading"
    return generator


# ---------------------------------------------------------------- №19-24 Грамматика

GRAMMAR = [
    [("My sister ______ in London since 2015.", "LIVE", ["has lived", "has been living"]), ("When I came home, my mother ______ dinner.", "COOK", ["was cooking"]),
     ("This castle ______ in the 12th century.", "BUILD", ["was built"]), ("If I ______ you, I would accept the offer.", "BE", ["were"]),
     ("He is the ______ student in our class.", "GOOD", ["best"])],
    [("There are a lot of ______ in the park today.", "CHILD", ["children"]), ("She ______ to school by bus every day.", "GO", ["goes"]),
     ("We ______ each other for ten years.", "KNOW", ["have known"]), ("The letter ______ yesterday morning.", "SEND", ["was sent"]),
     ("I wish I ______ more free time.", "HAVE", ["had"])],
    [("This is the ______ film I have ever seen.", "BAD", ["worst"]), ("He ______ the book before he saw the film.", "READ", ["had read"]),
     ("Look! It ______ .", "SNOW", ["is snowing"]), ("The ______ are grazing in the field.", "SHEEP", ["sheep"]),
     ("English ______ all over the world.", "SPEAK", ["is spoken"])],
    [("If it ______ tomorrow, we will stay at home.", "RAIN", ["rains"]), ("She said that she ______ tired.", "BE", ["was"]),
     ("It was his ______ visit to Moscow, he had never been there before.", "ONE", ["first"]), ("They ______ football when it started to rain.", "PLAY", ["were playing"]),
     ("The new bridge ______ next year.", "BUILD", ["will be built"])],
    [("He didn't want ______ late for the meeting.", "BE", ["to be"]), ("I enjoy ______ detective stories.", "READ", ["reading"]),
     ("Both ______ were tired after the journey.", "WOMAN", ["women"]), ("This task is ______ than the previous one.", "EASY", ["easier"]),
     ("We ______ our homework yet.", "NOT FINISH", ["have not finished", "haven't finished"])],
    [("Tom ______ his keys. He can't find them anywhere.", "LOSE", ["has lost"]), ("Be quiet! The room ______ at the moment.", "CLEAN", ["is being cleaned"]),
     ("She asked me where I ______ .", "LIVE", ["lived"]), ("These are ______ books, not ours.", "THEY", ["their"]),
     ("It was the ______ day of my life.", "HAPPY", ["happiest"])],
]


def gap_generator(name, group, instruction):
    def generator(r):
        sentence, word, answers = r.choice(group)
        made = task(f"{instruction}\n\n{sentence}\n\n{word}", answers[0], f"Правильная форма: {answers[0]}.")
        made["answers"] = answers
        made["kind"] = "exact"
        made["key"] = sentence
        return made
    generator.__name__ = name
    return generator


GRAMMAR_ASK = ("Преобразуйте слово, напечатанное заглавными буквами, так, чтобы оно грамматически соответствовало содержанию предложения. "
               "Запишите получившуюся форму (если в ней несколько слов, запишите их через пробел).")
WORD_ASK = ("Образуйте от слова, напечатанного заглавными буквами, однокоренное слово так, чтобы оно грамматически и лексически соответствовало содержанию предложения. "
            "Запишите получившееся слово.")

# ---------------------------------------------------------------- №25-29 Словообразование

WORD_FORMATION = [
    [("The film was really ______ : I nearly fell asleep.", "BORE", ["boring"]), ("Thank you for your ______ .", "KIND", ["kindness"]),
     ("He is a famous ______ who studies the stars.", "SCIENCE", ["scientist"]), ("The ______ of the new school took two years.", "CONSTRUCT", ["construction"]),
     ("It is ______ to cross the street here.", "DANGER", ["dangerous"])],
    [("The weather was ______ , so we stayed at home.", "RAIN", ["rainy"]), ("She smiled ______ when she saw the present.", "HAPPY", ["happily"]),
     ("His ______ to leave the team surprised everybody.", "DECIDE", ["decision"]), ("This old map is ______ : half of the roads on it no longer exist.", "USE", ["useless"]),
     ("London is famous for its ______ buildings.", "HISTORY", ["historical", "historic"])],
    [("The ______ of the population lives in cities.", "MAJOR", ["majority"]), ("It was ______ to open the window: it was stuck.", "POSSIBLE", ["impossible"]),
     ("She felt ______ when she failed the test.", "HAPPY", ["unhappy"]), ("He works as a ______ in a big orchestra.", "MUSIC", ["musician"]),
     ("The ______ of the telephone changed the world.", "INVENT", ["invention"])],
    [("Be ______ ! The floor is wet.", "CARE", ["careful"]), ("My ______ was spent in a small village.", "CHILD", ["childhood"]),
     ("They live in a ______ house near the sea.", "BEAUTY", ["beautiful"]), ("The ______ between the two towns is fifty miles.", "DISTANT", ["distance"]),
     ("He answered all the questions ______ .", "CORRECT", ["correctly"])],
    [("Tourism is important for the ______ of the region.", "DEVELOP", ["development"]), ("He wants to become a professional ______ .", "PHOTOGRAPH", ["photographer"]),
     ("The exhibition was a great ______ .", "SUCCEED", ["success"]), ("People were very ______ and helped us find the way.", "FRIEND", ["friendly"]),
     ("Her ______ of French is excellent.", "KNOW", ["knowledge"])],
]

# ---------------------------------------------------------------- №30-36 Лексика

VOCABULARY = [
    [("She ______ me that she would be late.", "told", ["said", "spoke", "talked"]), ("I'm looking ______ to seeing you.", "forward", ["ahead", "on", "up"]),
     ("He ______ a mistake in his test.", "made", ["did", "took", "gave"]), ("Could you ______ me a favour?", "do", ["make", "take", "give"]),
     ("The plane took ______ on time.", "off", ["out", "up", "away"])],
    [("It ______ me two hours to get there.", "took", ["spent", "lasted", "passed"]), ("She is interested ______ modern art.", "in", ["on", "at", "for"]),
     ("We have run ______ of milk.", "out", ["off", "away", "over"]), ("He ______ his keys at home.", "left", ["forgot", "stayed", "missed"]),
     ("Please ______ attention to the teacher.", "pay", ["give", "take", "put"])],
    [("He ______ up smoking last year.", "gave", ["took", "put", "made"]), ("She ______ in love with the city.", "fell", ["dropped", "got", "went"]),
     ("The concert was put ______ because of the rain.", "off", ["out", "away", "down"]), ("I can't ______ the difference between them.", "tell", ["say", "speak", "talk"]),
     ("He is good ______ maths.", "at", ["in", "on", "with"])],
    [("They ______ a decision quickly.", "made", ["did", "gave", "put"]), ("She ______ a photo of the bridge.", "took", ["made", "did", "gave"]),
     ("It depends ______ the weather.", "on", ["of", "from", "at"]), ("The teacher ______ us to open our books.", "told", ["said", "spoke", "talked"]),
     ("Turn ______ the light, please. It's dark in here.", "on", ["in", "at", "up"])],
    [("I ______ my grandmother every weekend.", "visit", ["attend", "go", "come"]), ("The shop is ______ front of the bank.", "in", ["on", "at", "by"]),
     ("She has been ______ of flying since childhood.", "afraid", ["frightening", "scare", "fear"]), ("He ______ the exam with excellent marks.", "passed", ["went", "gave", "made"]),
     ("We arrived ______ the airport late.", "at", ["to", "in", "on"])],
    [("The film is based ______ a true story.", "on", ["in", "at", "of"]), ("I ______ you were here!", "wish", ["want", "hope", "like"]),
     ("Hurry ______ ! We are late.", "up", ["on", "out", "off"]), ("She ______ her bike to school.", "rides", ["drives", "goes", "takes"]),
     ("He ______ the bus and was late for work.", "missed", ["lost", "passed", "failed"])],
    [("What ______ ? You look sad.", "happened", ["passed", "went", "became"]), ("The children were ______ by the clown's tricks.", "amused", ["amusing", "amuse", "amusement"]),
     ("She ______ me of my aunt.", "reminds", ["remembers", "recalls", "memorises"]), ("Can you ______ me your pen for a minute?", "lend", ["borrow", "owe", "rent"]),
     ("He ______ to be a doctor when he grows up.", "wants", ["enjoys", "dreams", "likes"])],
]


def choice_generator(name, group):
    def generator(r):
        sentence, right, wrong = r.choice(group)
        options = [right] + wrong
        r.shuffle(options)
        made = task(f"Выберите слово, которое должно стоять на месте пропуска. Запишите цифру, соответствующую выбранному варианту ответа.\n\n{sentence}\n\n{numbered(options)}",
                    str(options.index(right) + 1), f"Верный вариант: {right}.")
        made["kind"] = "exact"
        made["key"] = sentence
        return made
    generator.__name__ = name
    return generator


NUMBERS = (
    [Entry(10, "Понимание основного содержания текста", 2, [e10_headings]), Entry(11, "Понимание структурно-смысловых связей в тексте", 2, [e11_gaps])]
    + [Entry(12 + position, "Полное понимание текста", 1, [reading_question(position)]) for position in range(7)]
    + [Entry(19 + index, "Грамматические навыки", 1, [gap_generator(f"e{19 + index}_grammar", group, GRAMMAR_ASK)]) for index, group in enumerate(GRAMMAR)]
    + [Entry(25 + index, "Словообразование", 1, [gap_generator(f"e{25 + index}_words", group, WORD_ASK)]) for index, group in enumerate(WORD_FORMATION)]
    + [Entry(30 + index, "Лексические навыки", 1, [choice_generator(f"e{30 + index}_vocabulary", group)]) for index, group in enumerate(VOCABULARY)]
)
