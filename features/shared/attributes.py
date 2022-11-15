from __future__ import annotations

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

# This is a convenient container for handling merging attributes from various
# sources. One day, I might update the Expertise class to use this.
class Attributes():
    def __init__(self, constitution, strength, dexterity, intelligence, luck, memory):
        self.constitution: int = constitution
        self.strength: int = strength
        self.dexterity: int = dexterity
        self.intelligence: int = intelligence
        self.luck: int = luck
        self.memory: int = memory

    def __add__(self, other: Attributes):
        return Attributes(
            self.constitution + other.constitution,
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.luck + other.luck,
            self.memory + other.memory
        )
