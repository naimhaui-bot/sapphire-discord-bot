from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    name: str
    description: str
    traits: frozenset[str]


_CHARACTERS = (
    Character("Sherlock Holmes", "a brilliant detective", frozenset({"human", "fictional", "detective"})),
    Character("Harry Potter", "a young wizard", frozenset({"human", "fictional", "wizard"})),
    Character("Mario", "a heroic video-game plumber", frozenset({"human", "fictional", "game"})),
    Character("Batman", "a masked crime fighter", frozenset({"human", "fictional", "hero"})),
    Character("Darth Vader", "a powerful space villain", frozenset({"human", "fictional", "space", "villain"})),
)

_QUESTIONS = (
    ("Is your character fictional?", "fictional"),
    ("Is your character human?", "human"),
    ("Is your character associated with games?", "game"),
    ("Is your character a hero?", "hero"),
    ("Is your character a villain?", "villain"),
    ("Is your character associated with space?", "space"),
    ("Is your character a wizard?", "wizard"),
    ("Is your character a detective?", "detective"),
    ("Is your character known for a mask or disguise?", "hero"),
    ("Is your character from a popular franchise?", "fictional"),
)


class Game:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.question_index = 0
        self._answers: list[bool | None] = []
        self._candidates = list(_CHARACTERS)

    @property
    def question(self) -> tuple[str, str]:
        return _QUESTIONS[self.question_index]

    @property
    def finished(self) -> bool:
        return self.question_index >= len(_QUESTIONS)

    @property
    def guess(self) -> Character:
        if not self._candidates:
            return _CHARACTERS[0]
        return self._candidates[0]

    def answer(self, value: bool | None) -> None:
        if self.finished:
            return
        trait = self.question[1]
        self._answers.append(value)
        if value is not None:
            self._candidates = [
                character for character in self._candidates
                if (trait in character.traits) == value
            ] or self._candidates
        self.question_index += 1
