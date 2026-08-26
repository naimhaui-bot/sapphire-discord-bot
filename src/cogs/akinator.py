from dataclasses import dataclass, field


@dataclass(frozen=True)
class Character:
    name: str
    description: str
    traits: frozenset[str]


CHARACTERS = (
    Character("Steve", "the iconic Minecraft survivor", frozenset({"game", "minecraft", "male", "hero"})),
    Character("Alex", "the Minecraft adventurer", frozenset({"game", "minecraft", "female", "hero"})),
    Character("Mario", "the famous Italian platforming hero", frozenset({"game", "italy", "male", "hero", "mustache"})),
    Character("Princess Zelda", "the wise ruler of Hyrule", frozenset({"game", "fantasy", "female", "royal", "hero"})),
    Character("Batman", "Gotham's masked detective", frozenset({"comic", "male", "hero", "masked"})),
    Character("Spider-Man", "the web-slinging superhero", frozenset({"comic", "male", "hero", "masked", "young"})),
    Character("Elsa", "the ice-powered Disney queen", frozenset({"movie", "female", "royal", "magic"})),
    Character("Sherlock Holmes", "the legendary consulting detective", frozenset({"book", "male", "detective", "british"})),
    Character("Harry Potter", "the young wizard from Hogwarts", frozenset({"book", "male", "magic", "young", "hero"})),
    Character("Taylor Swift", "a globally known singer-songwriter", frozenset({"real", "female", "singer", "american"})),
)

QUESTIONS = (
    ("Is your character fictional?", "fictional"),
    ("Is your character from a video game?", "game"),
    ("Is your character a superhero or hero?", "hero"),
    ("Is your character male?", "male"),
    ("Is your character female?", "female"),
    ("Is your character from a movie?", "movie"),
    ("Is your character associated with magic?", "magic"),
    ("Is your character masked?", "masked"),
    ("Is your character young?", "young"),
    ("Is your character a detective?", "detective"),
    ("Is your character real?", "real"),
    ("Is your character a singer?", "singer"),
)


@dataclass
class Game:
    user_id: int
    candidates: list[Character] = field(default_factory=lambda: list(CHARACTERS))
    question_index: int = 0
    answers: dict[str, bool | None] = field(default_factory=dict)

    @property
    def question(self) -> tuple[str, str]:
        return QUESTIONS[self.question_index % len(QUESTIONS)]

    def answer(self, value: bool | None) -> None:
        trait = self.question[1]
        self.answers[trait] = value
        if value is not None:
            self.candidates = [
                candidate for candidate in self.candidates
                if (trait in candidate.traits) == value
            ] or self.candidates
        self.question_index += 1

    @property
    def guess(self) -> Character:
        return self.candidates[0]

    @property
    def finished(self) -> bool:
        return len(self.candidates) <= 1 or self.question_index >= 10