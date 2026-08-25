import re
from typing import Any

VARIABLES = {
    "user": lambda member: str(member),
    "username": lambda member: member.display_name,
    "server": lambda member: member.guild.name,
    "memberCount": lambda member: str(member.guild.member_count),
    "mention": lambda member: member.mention,
}


def render(text: str, member: Any, **extra: Any) -> str:
    values = {name: function(member) for name, function in VARIABLES.items()}
    values.update({key: str(value) for key, value in extra.items()})
    return re.sub(r"\{([A-Za-z][A-Za-z0-9_]*)\}", lambda m: values.get(m.group(1), m.group(0)), text)[:2000]