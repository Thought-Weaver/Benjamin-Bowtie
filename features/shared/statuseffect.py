from __future__ import annotations

from strenum import StrEnum

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

BLEED_PERCENT_HP = 0.01
POISONED_PERCENT_HP = 0.01

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class StatusEffectKey(StrEnum):
    Bleeding = "Bleeding"
    Poisoned = "Poisoned"
    
    ConBuff = "ConBuff"
    StrBuff = "StrBuff"
    DexBuff = "DexBuff"
    IntBuff = "IntBuff"
    LckBuff = "LckBuff"

    ConDebuff = "ConDebuff"
    StrDebuff = "StrDebuff"
    DexDebuff = "DexDebuff"
    IntDebuff = "IntDebuff"
    LckDebuff = "LckDebuff"

    DmgReduction = "DmgReduction"
    DmgVulnerability = "DmgVulnerability"

    FixedDmgTick = "FixedDmgTick"

    TurnSkipChance = "TurnSkipChance"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class StatusEffect():
    def __init__(self, turns_remaining: int, value: (float | int), name: str, key: str, source_ability_str: str=None):
        self.turns_remaining = turns_remaining
        self.value = value
        self.name = name
        self.key = key
        self.source_ability_str = source_ability_str

    def decrement_turns_remaining(self):
        self.turns_remaining = max(0, self.turns_remaining - 1)

    def get_singular_or_plural_turns(self):
        if self.turns_remaining == 1:
            return "turn"
        return "turns"

    def __str__(self):
        # This should get overriden for a more informative string in each class
        return f"{self.name}: {self.value} ({self.turns_remaining} turns left)"


class Bleeding(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Bleeding", StatusEffectKey.Bleeding, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: Lose {self.value}% health every turn for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class Poisoned(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Poisoned", StatusEffectKey.Poisoned, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: Lose {self.value}% health every turn for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str

    
class ConBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Fortified", StatusEffectKey.ConBuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Con for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class StrBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Bolstered", StatusEffectKey.StrBuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Str for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DexBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Hastened", StatusEffectKey.DexBuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Dex for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class IntBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Insightful", StatusEffectKey.IntBuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Int for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class LckBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Lucky", StatusEffectKey.LckBuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Lck for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class ConDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Frail", StatusEffectKey.ConDebuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: -{self.value} Con for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class StrDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Weakened", StatusEffectKey.StrDebuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: -{self.value} Str for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DexDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Slowed", StatusEffectKey.DexDebuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: -{self.value} Dex for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class IntDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Enfeebled", StatusEffectKey.IntDebuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: -{self.value} Int for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class LckDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Unlucky", StatusEffectKey.LckDebuff, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: -{self.value} Lck for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DmgReduction(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Protected", StatusEffectKey.DmgReduction, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage reduction for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DmgVulnerability(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Vulnerable", StatusEffectKey.DmgReduction, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage taken increase for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class FixedDmgTick(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Echoing", StatusEffectKey.FixedDmgTick, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: Take {self.value} damage at the start of your turn for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class TurnSkipChance(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str=None):
        super().__init__(turns_remaining, value, "Paralyzing", StatusEffectKey.TurnSkipChance, source_ability_str)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% chance to skip a turn for {self.turns_remaining} {self.get_singular_or_plural_turns()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str
