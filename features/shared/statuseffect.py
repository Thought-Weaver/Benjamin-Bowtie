from __future__ import annotations

from strenum import StrEnum

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player

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

    # Both of these happen at the start of the turn
    FixedDmgTick = "FixedDmgTick"
    TurnSkipChance = "TurnSkipChance"

    AttrBuffOnDamage = "AttrBuffOnDamage"

    Taunted = "Taunted"
    CannotTarget = "CannotTarget"

    Generating = "Generating"
    Tarnished = "Tarnished"

    ManaToHP = "ManaToHP"

    # TODO: Implement this on item usage
    PotionBuff = "PotionBuff"

    PoisonHeals = "PoisonHeals"

    RegenerateHP = "RegenerateHP"

    RestrictedToItems = "RestrictedToItems"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class StatusEffect():
    def __init__(self, turns_remaining: int, value: (float | int), name: str, key: str, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        # If this is -1, then the buff applies for the rest of the duel
        self.turns_remaining = turns_remaining
        self.value = value
        self.name = name
        self.key = key
        self.source_ability_str = source_ability_str
        self.trigger_first_turn = trigger_first_turn
        
    def decrement_turns_remaining(self):
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
            return "the end of the duel"
        return f"{self.turns_remaining} turns"

    def __str__(self):
        # This should get overriden for a more informative string in each class
        return f"{self.name}: {self.value} ({self.turns_remaining} turns left)"


class Bleeding(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Bleeding", StatusEffectKey.Bleeding, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Lose {self.value}% health every turn for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class Poisoned(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Poisoned", StatusEffectKey.Poisoned, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Lose {self.value}% health every turn for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str

    
class ConBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Fortified", StatusEffectKey.ConBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class StrBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Bolstered", StatusEffectKey.StrBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DexBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Hastened", StatusEffectKey.DexBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Dex for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class IntBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Insightful", StatusEffectKey.IntBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class LckBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Lucky", StatusEffectKey.LckBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class ConDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Frail", StatusEffectKey.ConDebuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class StrDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Weakened", StatusEffectKey.StrDebuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DexDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Slowed", StatusEffectKey.DexDebuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Dex for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class IntDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Enfeebled", StatusEffectKey.IntDebuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class LckDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Unlucky", StatusEffectKey.LckDebuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DmgReduction(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Protected", StatusEffectKey.DmgReduction, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage reduction for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class DmgVulnerability(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Vulnerable", StatusEffectKey.DmgReduction, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage taken increase for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class FixedDmgTick(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Echoing", StatusEffectKey.FixedDmgTick, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {self.value} damage at the start of your turn for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class TurnSkipChance(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Faltering", StatusEffectKey.TurnSkipChance, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% chance to skip a turn for {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class AttrBuffOnDamage(StatusEffect):
    def __init__(self, turns_remaining: int, on_being_hit_buffs: List[StatusEffect], source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Enraged", StatusEffectKey.AttrBuffOnDamage, source_ability_str, trigger_first_turn)
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
        display_str = f"{self.name}: Gain {buffs_str} whenever you're damaged for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class Taunted(StatusEffect):
    def __init__(self, turns_remaining: int, forced_to_attack: Player | NPC, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Taunted", StatusEffectKey.Taunted, source_ability_str, trigger_first_turn)
        self.forced_to_attack = forced_to_attack

    def __str__(self):
        display_str = f"{self.name}: Forced to attack the caster for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class CannotTarget(StatusEffect):
    def __init__(self, turns_remaining: int, cant_target: Player | NPC, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Convinced", StatusEffectKey.CannotTarget, source_ability_str, trigger_first_turn)
        self.cant_target = cant_target

    def __str__(self):
        display_str = f"{self.name}: Can't target the caster for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class Generating(StatusEffect):
    def __init__(self, turns_remaining: int, targets_that_generate_on_hit: List[Player | NPC], value: int, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Generating", StatusEffectKey.Generating, source_ability_str, trigger_first_turn)
        self.targets_that_generate_on_hit = targets_that_generate_on_hit

    def __str__(self):
        display_str = f"{self.name}: The chosen targets generate coins when hit for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class Tarnished(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Tarnished", StatusEffectKey.Tarnished, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Whenever you gain coins, deal damage relative to the amount gained for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class ManaToHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Sanguinated", StatusEffectKey.ManaToHP, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: All your abilities that use Mana instead use HP for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class PotionBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Eureka", StatusEffectKey.PotionBuff, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Potions you use are {self.value * 100}% more powerful for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class PoisonHeals(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Absorbing", StatusEffectKey.PoisonHeals, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Poison damage heals you for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class RestrictedToItems(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Acervophilic", StatusEffectKey.RestrictedToItems, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can only use items for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str


class RegenerateHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_ability_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Regenerating", StatusEffectKey.RegenerateHP, source_ability_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You regain {self.value}% of your health for the next {self.get_turns_remaining_str()}"
        
        if self.source_ability_str is not None:
            display_str += f" (from {self.source_ability_str})"
        
        return display_str
