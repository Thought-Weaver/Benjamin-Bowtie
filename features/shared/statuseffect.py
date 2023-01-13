from __future__ import annotations

from strenum import StrEnum

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
    StatusEffectKey.BonusDamageOnAttack
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
    StatusEffectKey.StackingDamage
]

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class StatusEffect():
    def __init__(self, turns_remaining: int, value: (float | int), name: str, key: str, source_str: str | None=None, trigger_first_turn: bool=True):
        # If this is -1, then the buff applies for the rest of the duel
        self.turns_remaining = turns_remaining
        self.value = value
        self.name = name
        self.key = key
        self.source_str = source_str
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


class Poisoned(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Poisoned", StatusEffectKey.Poisoned, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {round(self.value * 100, 2)}% max health as damage every turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str

    
class ConBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Fortified", StatusEffectKey.ConBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class StrBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Bolstered", StatusEffectKey.StrBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DexBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Hastened", StatusEffectKey.DexBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Dex for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class IntBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Insightful", StatusEffectKey.IntBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class LckBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Lucky", StatusEffectKey.LckBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class MemBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Retentive", StatusEffectKey.MemBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: +{self.value} Mem for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class ConDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Frail", StatusEffectKey.ConDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Con for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class StrDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Weakened", StatusEffectKey.StrDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Str for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


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
        super().__init__(turns_remaining, value, "Enfeebled", StatusEffectKey.IntDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Int for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class LckDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Unlucky", StatusEffectKey.LckDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class MemDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Forgetful", StatusEffectKey.MemDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value} Lck for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DmgReduction(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Protected", StatusEffectKey.DmgReduction, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage reduction for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DmgVulnerability(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Vulnerable", StatusEffectKey.DmgReduction, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% damage taken increase for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class FixedDmgTick(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Echoing", StatusEffectKey.FixedDmgTick, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Take {self.value} damage at the start of your turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class TurnSkipChance(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Faltering", StatusEffectKey.TurnSkipChance, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: {self.value * 100}% chance to skip a turn for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


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
        display_str = f"{self.name}: Gain {buffs_str} whenever you're damaged for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Taunted(StatusEffect):
    def __init__(self, turns_remaining: int, forced_to_attack: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Taunted", StatusEffectKey.Taunted, source_str, trigger_first_turn)
        self.forced_to_attack = forced_to_attack

    def __str__(self):
        display_str = f"{self.name}: Forced to attack the caster for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class CannotTarget(StatusEffect):
    def __init__(self, turns_remaining: int, cant_target: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, 0, "Convinced", StatusEffectKey.CannotTarget, source_str, trigger_first_turn)
        self.cant_target = cant_target

    def __str__(self):
        display_str = f"{self.name}: Can't target the caster for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Generating(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Generating", StatusEffectKey.Generating, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Whenever you successfully attack a target, coins are generated for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Tarnished(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Tarnished", StatusEffectKey.Tarnished, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Whenever you gain coins, deal damage relative to the amount gained for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class ManaToHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Sanguinated", StatusEffectKey.ManaToHP, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: All your abilities that use Mana instead use HP for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class PotionBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Eureka", StatusEffectKey.PotionBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Potions you use are {self.value * 100}% more powerful for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class PoisonHeals(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Absorbing", StatusEffectKey.PoisonHeals, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Poison damage heals you for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class RestrictedToItems(StatusEffect):
    def __init__(self, turns_remaining: int, value: int, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Acervophilic", StatusEffectKey.RestrictedToItems, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can only use items for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class RegenerateHP(StatusEffect):
    def __init__(self, turns_remaining: int, value: float, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Regenerating", StatusEffectKey.RegenerateHP, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You regain {self.value * 100}% of your health for the next {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DmgBuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Empowered", StatusEffectKey.DmgBuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Deal {self.value * 100}% additional damage for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DmgDebuff(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Diminished", StatusEffectKey.DmgDebuff, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Deal {self.value * 100}% less damage for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Charmed(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Charmed", StatusEffectKey.Charmed, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Your enemies are your allies and vice versa for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class CannotAttack(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Atrophied", StatusEffectKey.CannotAttack, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't attack for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Sleeping(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Sleeping", StatusEffectKey.Sleeping, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't take actions for {self.get_turns_remaining_str()} (this status effect is removed after taking damage)"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Decaying(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Decaying", StatusEffectKey.Decaying, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Healing effects are {self.value * 100}% less effective instead for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class Undying(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Undying", StatusEffectKey.Undying, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't be reduced below 1 HP for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class CannotUseAbilities(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Enfeebled", StatusEffectKey.CannotUseAbilities, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You can't use abilities for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class DmgReflect(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Reflecting", StatusEffectKey.DmgReflect, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: You reflect {self.value} damage you take for {self.get_turns_remaining_str()}"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class BonusDamageOnAttack(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Patient", StatusEffectKey.BonusDamageOnAttack, source_str, trigger_first_turn)

    def __str__(self):
        display_str = f"{self.name}: Your next attack deals {self.value} more damage (lasts until attacking or for {self.get_turns_remaining_str()})"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str


class StackingDamage(StatusEffect):
    def __init__(self, turns_remaining: int, value: (float | int), caster: Player | NPC, source_str: str | None=None, trigger_first_turn: bool=True):
        super().__init__(turns_remaining, value, "Reverberating", StatusEffectKey.StackingDamage, source_str, trigger_first_turn)
        self.caster = caster

    def __str__(self):
        display_str = f"{self.name}: Attacking or using the ability that caused this again against this target deals {self.value * 100}% more damage (lasts for {self.get_turns_remaining_str()})"
        
        if self.source_str is not None:
            display_str += f" (from {self.source_str})"
        
        return display_str
