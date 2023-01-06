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

    def any_nonzero(self):
        return any(attr != 0 for attr in [self.constitution, self.strength, self.dexterity, self.intelligence, self.luck, self.memory])

    def get_short_comma_sep_str(self):
        short_attr_strs = []
        if self.constitution != 0:
            short_attr_strs.append(f"Con {self.constitution}")
        if self.strength != 0:
            short_attr_strs.append(f"Str {self.strength}")
        if self.dexterity != 0:
            short_attr_strs.append(f"Dex {self.dexterity}")
        if self.intelligence != 0:
            short_attr_strs.append(f"Int {self.intelligence}")
        if self.luck != 0:
            short_attr_strs.append(f"Lck {self.luck}")
        if self.memory != 0:
            short_attr_strs.append(f"Mem {self.memory}")
        return ", ".join(short_attr_strs)

    def __add__(self, other: Attributes):
        return Attributes(
            self.constitution + other.constitution,
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.luck + other.luck,
            self.memory + other.memory
        )

    def __str__(self) -> str:
        return f"Constitution: {self.constitution}\nStrength: {self.strength}\nDexterity: {self.dexterity}\nIntelligence: {self.intelligence}\nLuck: {self.luck}\nMemory: {self.memory}"

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.constitution = state.get("constitution", 0)
        self.strength = state.get("strength", 0)
        self.dexterity = state.get("dexterity", 0)
        self.intelligence = state.get("intelligence", 0)
        self.luck = state.get("luck", 0)
        self.memory = state.get("memory", 0)
