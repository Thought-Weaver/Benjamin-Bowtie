from __future__ import annotations

from enum import StrEnum

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player

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
    MemBuff = "MemBuff"

    ConDebuff = "ConDebuff"
    StrDebuff = "StrDebuff"
    DexDebuff = "DexDebuff"
    IntDebuff = "IntDebuff"
    LckDebuff = "LckDebuff"
    MemDebuff = "MemDebuff"

    DmgReduction = "DmgReduction"
    DmgVulnerability = "DmgVulnerability"

    # Both of these happen at the start of the turn
    FixedDmgTick = "FixedDmgTick"
    TurnSkipChance = "TurnSkipChance"

    AttrBuffOnDamage = "AttrBuffOnDamage"

    Taunted = "Taunted"
    CannotTarget = "CannotTarget"

    Generating = "Generating"
    Tarnished = "Tarnished"

    ManaToHP = "ManaToHP"

    PotionBuff = "PotionBuff"

    PoisonHeals = "PoisonHeals"

    RegenerateHP = "RegenerateHP"

    RestrictedToItems = "RestrictedToItems"

    DmgBuff = "DmgBuff"
    DmgDebuff = "DmgDebuff"
    DmgReflect = "DmgReflect"

    Charmed = "Charmed"
    CannotAttack = "CannotAttack"
    Sleeping = "Sleeping"
    Decaying = "Decaying"
    Undying = "Undying"
    CannotUseAbilities = "CannotUseAbilities"

    BonusDamageOnAttack = "BonusDamageOnAttack"
    StackingDamage = "StackingDamage"
    Marked = "Marked"

    AttackingChanceToApplyStatus = "AttackingChanceToApplyStatus"

    RegenerateArmor = "RegenerateArmor"

    Corrupted = "Corrupted"
    StatsHidden = "StatsHidden"
    DamageSplit = "DamageSplit"

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

POSITIVE_STATUS_EFFECTS_ON_SELF: List[StatusEffectKey] = [
    StatusEffectKey.ConBuff,
    StatusEffectKey.StrBuff,
    StatusEffectKey.DexBuff,
    StatusEffectKey.IntBuff,
    StatusEffectKey.LckBuff,
    StatusEffectKey.MemBuff,
    StatusEffectKey.AttrBuffOnDamage,
    StatusEffectKey.Generating,
    StatusEffectKey.Tarnished,
    StatusEffectKey.ManaToHP,
    StatusEffectKey.PotionBuff,
    StatusEffectKey.PoisonHeals,
    StatusEffectKey.RegenerateHP,
    StatusEffectKey.RestrictedToItems, # Since this can only happen with Quick Access
    StatusEffectKey.DmgBuff,
    StatusEffectKey.Undying,
    StatusEffectKey.DmgReflect,
    StatusEffectKey.BonusDamageOnAttack,
    StatusEffectKey.AttackingChanceToApplyStatus,
    StatusEffectKey.RegenerateArmor,
    StatusEffectKey.DmgReduction,
    StatusEffectKey.DamageSplit
]

NEGATIVE_STATUS_EFFECTS: List[StatusEffectKey] = [
    StatusEffectKey.ConDebuff,
    StatusEffectKey.StrDebuff,
    StatusEffectKey.DexDebuff,
    StatusEffectKey.IntDebuff,
    StatusEffectKey.LckDebuff,
    StatusEffectKey.MemDebuff,
    StatusEffectKey.DmgVulnerability,
    StatusEffectKey.FixedDmgTick,
    StatusEffectKey.TurnSkipChance,
    StatusEffectKey.Taunted,
    StatusEffectKey.DmgDebuff,
    StatusEffectKey.Charmed,
    StatusEffectKey.CannotAttack,
    StatusEffectKey.Sleeping,
    StatusEffectKey.Decaying,
    StatusEffectKey.Undying,
    StatusEffectKey.CannotUseAbilities,
    StatusEffectKey.StackingDamage,
    StatusEffectKey.Corrupted,
    StatusEffectKey.StatsHidden
]

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class StatusEffect():
    def __init__(self, turns_remaining: int, value: (float | int), name: str, key: StatusEffectKey, source_str: str | None=None, trigger_first_turn: bool=True, value_stackable: bool=False):
        # If this is -1, then the buff applies for the rest of the duel
        self.turns_remaining: int = turns_remaining
        self.value: float | int = value
        self.name: str = name
        self.key: StatusEffectKey = key
        self.source_str: str | None = source_str
        self.trigger_first_turn: bool = trigger_first_turn
        self.value_stackable: bool = value_stackable
        
    def decrement_turns_remaining(self):
        if isinstance(self, DamageSplit):
            self.triggered_this_turn = False

        if not self.trigger_first_turn:
            self.trigger_first_turn = True
            return

        if self.turns_remaining != -1:
            self.turns_remaining = max(0, self.turns_remaining - 1)

    def set_trigger_first_turn(self, is_self_cast: bool):
        # Used for mapping this to account for self-cast abilities
        self.trigger_first_turn = is_self_cast
        return self

    def get_turns_remaining_str(self):
        if self.turns_remaining == 1:
            return "1 turn"
        if self.turns_remaining == -1:
            return "the rest of the duel"
        return f"{self.turns_remaining} turns"

    def __str__(self):
        # This should get overriden for a more informative string in each class
        return f"{self.name}: {self.value} ({self.turns_remaining} turns left)"


class Bleeding(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Bleeding", StatusEffectKey.Bleeding, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {round(self.value * 100, 2)}% max health as damage every turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Bleeding"
        self.key = StatusEffectKey.Bleeding
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Poisoned(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Poisoned", StatusEffectKey.Poisoned, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {round(self.value * 100, 2)}% max health as damage every turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Poisoned"
        self.key = StatusEffectKey.Poisoned
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)

    
class ConBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Fortified", StatusEffectKey.ConBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Fortified"
        self.key = StatusEffectKey.ConBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class StrBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Bolstered", StatusEffectKey.StrBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Bolstered"
        self.key = StatusEffectKey.StrBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DexBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Hastened", StatusEffectKey.DexBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Dex for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Hastened"
        self.key = StatusEffectKey.DexBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class IntBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Insightful", StatusEffectKey.IntBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Insightful"
        self.key = StatusEffectKey.IntBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class LckBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Lucky", StatusEffectKey.LckBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Lucky"
        self.key = StatusEffectKey.LckBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class MemBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Retentive", StatusEffectKey.MemBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Mem for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Retentive"
        self.key = StatusEffectKey.MemDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class ConDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Frail", StatusEffectKey.ConDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Frail"
        self.key = StatusEffectKey.ConDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class StrDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Weakened", StatusEffectKey.StrDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Weakened"
        self.key = StatusEffectKey.StrDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DexDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Slowed", StatusEffectKey.DexDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Dex for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class IntDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Drained", StatusEffectKey.IntDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Drained"
        self.key = StatusEffectKey.IntDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class LckDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Unlucky", StatusEffectKey.LckDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Unlucky"
        self.key = StatusEffectKey.LckDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class MemDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Forgetful", StatusEffectKey.MemDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Forgetful"
        self.key = StatusEffectKey.MemDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DmgReduction(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Protected", StatusEffectKey.DmgReduction, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage resistance for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Protected"
        self.key = StatusEffectKey.DmgReduction
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DmgVulnerability(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Vulnerable", StatusEffectKey.DmgVulnerability, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage taken increase for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Vulnerable"
        self.key = StatusEffectKey.DmgVulnerability
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class FixedDmgTick(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Echoing", StatusEffectKey.FixedDmgTick, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {self.value} damage at the start of your turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Echoing"
        self.key = StatusEffectKey.FixedDmgTick
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class TurnSkipChance(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Faltering", StatusEffectKey.TurnSkipChance, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% chance to skip a turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Faltering"
        self.key = StatusEffectKey.TurnSkipChance
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class AttrBuffOnDamage(StatusEffect):
    def __init__(self, turns_remaining: int, on_being_hit_buffs: List[StatusEffect], source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Enraged", StatusEffectKey.AttrBuffOnDamage, source_str, trigger_first_turn)
        self.on_being_hit_buffs = on_being_hit_buffs

    def _get_attr_for_buff(self, buff: StatusEffect):
        if buff.key == StatusEffectKey.ConBuff:
            return "Constitution"
        if buff.key == StatusEffectKey.StrBuff:
            return "Strength"
        if buff.key == StatusEffectKey.DexBuff:
            return "Dexterity"
        if buff.key == StatusEffectKey.IntBuff:
            return "Intelligence"
        if buff.key == StatusEffectKey.LckBuff:
            return "Luck"
        return "Unknown"

    def get_buffs_str(self):
        return ", ".join([f"+{buff.value} {self._get_attr_for_buff(buff)}" for buff in self.on_being_hit_buffs])

    def __str__(self):
        buffs_str = self.get_buffs_str()
        display_str = f"{self.name}: Gain {buffs_str} whenever you're damaged for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Enraged"
        self.key = StatusEffectKey.AttrBuffOnDamage
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.on_being_hit_buffs = state.get("on_being_hit_buffs", [])


class Taunted(StatusEffect):
    def __init__(self, turns_remaining: int, forced_to_attack: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Taunted", StatusEffectKey.Taunted, source_str, trigger_first_turn)
        self.forced_to_attack = forced_to_attack

    def __str__(self):
        display_str = f"{self.name}: Forced to attack the caster for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Taunted"
        self.key = StatusEffectKey.Taunted
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.forced_to_attack = state.get("forced_to_attack", None)


class CannotTarget(StatusEffect):
    def __init__(self, turns_remaining: int, cant_target: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Convinced", StatusEffectKey.CannotTarget, source_str, trigger_first_turn)
        self.cant_target = cant_target

    def __str__(self):
        display_str = f"{self.name}: Can't target the caster for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Convinced"
        self.key = StatusEffectKey.CannotTarget
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.cant_target = state.get("cant_target", None)


class Generating(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Generating", StatusEffectKey.Generating, source_str, trigger_first_turn)

    def __str__(self):
        coin_str = "coins" if self.value != 1 else "coin"
        display_str = f"{self.name}: Whenever you successfully attack a target, {self.value} {coin_str} are generated for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Generating"
        self.key = StatusEffectKey.Generating
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Tarnished(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Tarnished", StatusEffectKey.Tarnished, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Whenever you gain coins, deal damage relative to the amount gained for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Tarnished"
        self.key = StatusEffectKey.Tarnished
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class ManaToHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Sanguinated", StatusEffectKey.ManaToHP, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: All your abilities that use Mana instead use HP for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Sanguinated"
        self.key = StatusEffectKey.ManaToHP
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class PotionBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Eureka", StatusEffectKey.PotionBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Potions you use are {self.value * 100}% more powerful for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Eureka"
        self.key = StatusEffectKey.PotionBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class PoisonHeals(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Absorbing", StatusEffectKey.PoisonHeals, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Poison damage heals you for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Absorbing"
        self.key = StatusEffectKey.PoisonHeals
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class RestrictedToItems(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Acervophilic", StatusEffectKey.RestrictedToItems, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can only use items for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Acervophilic"
        self.key = StatusEffectKey.RestrictedToItems
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class RegenerateHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Regenerating", StatusEffectKey.RegenerateHP, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You regain {self.value * 100}% of your health for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Regenerating"
        self.key = StatusEffectKey.RegenerateHP
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DmgBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Empowered", StatusEffectKey.DmgBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Deal {self.value * 100}% additional damage for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Empowered"
        self.key = StatusEffectKey.DmgBuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DmgDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Diminished", StatusEffectKey.DmgDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Deal {self.value * 100}% less damage for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Diminished"
        self.key = StatusEffectKey.DmgDebuff
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Charmed(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Charmed", StatusEffectKey.Charmed, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Your enemies are your allies and vice versa for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Charmed"
        self.key = StatusEffectKey.Charmed
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class CannotAttack(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Atrophied", StatusEffectKey.CannotAttack, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't attack for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Atrophied"
        self.key = StatusEffectKey.CannotAttack
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Sleeping(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Sleeping", StatusEffectKey.Sleeping, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't take actions for {self.get_turns_remaining_str()} (this status effect is removed after taking damage)"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Sleeping"
        self.key = StatusEffectKey.Sleeping
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Decaying(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Decaying", StatusEffectKey.Decaying, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Healing effects are {self.value * 100}% less effective instead for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Decaying"
        self.key = StatusEffectKey.Decaying
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Undying(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Undying", StatusEffectKey.Undying, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't be reduced below 1 HP for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Undying"
        self.key = StatusEffectKey.Undying
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class CannotUseAbilities(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Enfeebled", StatusEffectKey.CannotUseAbilities, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't use abilities for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Enfeebled"
        self.key = StatusEffectKey.CannotUseAbilities
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class DmgReflect(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Reflecting", StatusEffectKey.DmgReflect, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You reflect {self.value * 100}% damage you take for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Reflecting"
        self.key = StatusEffectKey.DmgReflect
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class BonusDamageOnAttack(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Patient", StatusEffectKey.BonusDamageOnAttack, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Your next attack deals {self.value} more damage (lasts until attacking or for {self.get_turns_remaining_str()})"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Patient"
        self.key = StatusEffectKey.BonusDamageOnAttack
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class StackingDamage(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), caster: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Reverberating", StatusEffectKey.StackingDamage, source_str, trigger_first_turn)
        self.caster = caster

    def __str__(self):
        display_str = f"{self.name}: Attacking or using the ability that caused this again against this target deals {self.value * 100}% more damage (lasts for {self.get_turns_remaining_str()})"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Reverberating"
        self.key = StatusEffectKey.StackingDamage
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.caster = state.get("caster", None)


class Marked(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), caster: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Marked", StatusEffectKey.Marked, source_str, trigger_first_turn)
        self.caster = caster

    def __str__(self):
        display_str = f"{self.name}: This target is marked for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Marked"
        self.key = StatusEffectKey.Marked
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.caster = state.get("caster", None)


class AttackingChanceToApplyStatus(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), status_effect: StatusEffect, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, f"Applying ({status_effect.name})", StatusEffectKey.AttackingChanceToApplyStatus, source_str, trigger_first_turn)
        self.status_effect = status_effect

    def __str__(self):
        display_str = f"{self.name}: You have a {self.value * 100}% chance to apply {self.status_effect.name} on successful attacks for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.key = StatusEffectKey.AttackingChanceToApplyStatus
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.status_effect = state.get("status_effect", None)
        self.name = f"Applying ({self.status_effect.name if self.status_effect is not None else ''})"


class RegenerateArmor(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Restoring", StatusEffectKey.RegenerateArmor, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You regain {self.value * 100}% of your armor for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Restoring"
        self.key = StatusEffectKey.RegenerateArmor
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)


class Corrupted(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        # Corrupted is a special case where turns_remaining should always be -1, so we can trivially get value
        # stacking.
        super().__init__(turns_remaining, value, "Corrupted", StatusEffectKey.Corrupted, source_str, trigger_first_turn, value_stackable=True)

    def __str__(self):
        display_str = f"{self.name}: You have {self.value} stacks of corruption, making it easier for certain enemies to influence you"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Corrupted"
        self.key = StatusEffectKey.Corrupted
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", True)


class StatsHidden(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Confused", StatusEffectKey.StatsHidden, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Your health, mana, and armor are hidden for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DamageSplit(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, linked_targets: List[Player | NPC], source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Fatebound", StatusEffectKey.DamageSplit, source_str, trigger_first_turn)
        self.linked_targets = linked_targets
        self.triggered_this_turn = False

    def __str__(self):
        display_str = f"{self.name}: You are linked to your allies, splitting all damage evenly between you for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.turns_remaining = state.get("turns_remaining", 0)
        self.value = state.get("value", 0)
        self.name = "Fatebound"
        self.key = StatusEffectKey.DamageSplit
        self.source_str = state.get("source_str", None)
        self.trigger_first_turn = state.get("trigger_first_turn", True)
        self.value_stackable = state.get("value_stackable", False)
        self.linked_targets = state.get("linked_targets", [])
        self.triggered_this_turn = state.get("triggered_this_turn", False)
