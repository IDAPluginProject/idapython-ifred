from dataclasses import dataclass

@dataclass
class Action:
    id: str
    name: str
    shortcut: str
    description: str
