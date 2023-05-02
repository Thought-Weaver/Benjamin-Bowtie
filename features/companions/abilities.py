from __future__ import annotations

from math import ceil
import random
from features.expertise import Attribute, ExpertiseClass
from features.shared.ability import Ability, NegativeAbilityResult

from features.shared.constants import BLEED_PERCENT_HP, DEX_DMG_SCALE, DEX_DODGE_SCALE, INT_DMG_SCALE, LCK_DMG_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, POISONED_PERCENT_HP, STR_DMG_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.statuseffect import AttackingChanceToApplyStatus, AttrBuffOnDamage, Bleeding, BonusDamageOnAttack, Charmed, ConBuff, ConDebuff, DexBuff, DexDebuff, DmgDebuff, DmgReduction, DmgReflect, LckBuff, LckDebuff, Marked, Poisoned, RegenerateHP, Sleeping, StackingDamage, StatusEffectKey, StrBuff, StrDebuff, TurnSkipChance, Undying

from typing import Dict, List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player

# -----------------------------------------------------------------------------
# TIDEWATER CRAB ABILITIES
# -----------------------------------------------------------------------------
# PINCH! (Dueling/Companion Battle)
# -----------------------------------------------------------------------------

class PINCHI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="PINCH! I",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Con by 2 for 2 turns and deals 1-2 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=2,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PINCHII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="PINCH! II",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Con by 2 for 2 turns and deals 2-3 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=2,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PINCHIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="PINCH! III",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Con by 2 for 2 turns and deals 3-4 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=2,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PINCHIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="PINCH! IV",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Con by 2 for 3 turns and deals 4-5 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=3,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PINCHV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="PINCH! V",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Con by 2 for 3 turns and deals 5-6 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=3,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SCUTTLE (Companion Battle)
# -----------------------------------------------------------------------------

class ScuttleI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Scuttle I",
            class_key=ExpertiseClass.Fisher,
            description="Gain +15 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScuttleII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Scuttle II",
            class_key=ExpertiseClass.Fisher,
            description="Gain +25 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScuttleIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Scuttle III",
            class_key=ExpertiseClass.Fisher,
            description="Gain +35 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScuttleIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Scuttle IV",
            class_key=ExpertiseClass.Fisher,
            description="Gain +45 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScuttleV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Scuttle V",
            class_key=ExpertiseClass.Fisher,
            description="Gain +55 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=55,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MINI CRABNADO (Companion Battle)
# -----------------------------------------------------------------------------

class MiniCrabnadoI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Mini Crabnado I",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-4 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MiniCrabnadoII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Mini Crabnado II",
            class_key=ExpertiseClass.Fisher,
            description="Deal 2-6 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MiniCrabnadoIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Mini Crabnado III",
            class_key=ExpertiseClass.Fisher,
            description="Deal 3-8 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MiniCrabnadoIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Mini Crabnado IV",
            class_key=ExpertiseClass.Fisher,
            description="Deal 4-10 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 10))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MiniCrabnadoV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Mini Crabnado V",
            class_key=ExpertiseClass.Fisher,
            description="Deal 5-12 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 12))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PONDLOVER FROG ABILITIES
# -----------------------------------------------------------------------------
# IS THAT A FLY (Dueling/Companion Battle)
# -----------------------------------------------------------------------------

class IsThatAFlyI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB0",
            name="Is That a Fly I",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Dex by 5 for 2 turns and deals 1-2 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IsThatAFlyII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB0",
            name="Is That a Fly II",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Dex by 5 for 2 turns and deals 2-3 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IsThatAFlyIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB0",
            name="Is That a Fly III",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Dex by 5 for 2 turns and deals 3-4 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IsThatAFlyIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB0",
            name="Is That a Fly IV",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Dex by 5 for 2 turns and deals 4-5 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IsThatAFlyV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB0",
            name="Is That a Fly V",
            class_key=ExpertiseClass.Fisher,
            description="Decreases the target's Dex by 5 for 2 turns and deals 5-6 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HIPPITY HOP (Companion Battle)
# -----------------------------------------------------------------------------

class HippityHopI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Hippity Hop I",
            class_key=ExpertiseClass.Fisher,
            description="Gain +15 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HippityHopII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Hippity Hop II",
            class_key=ExpertiseClass.Fisher,
            description="Gain +25 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HippityHopIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Hippity Hop III",
            class_key=ExpertiseClass.Fisher,
            description="Gain +35 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HippityHopIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Hippity Hop IV",
            class_key=ExpertiseClass.Fisher,
            description="Gain +45 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HippityHopV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Hippity Hop V",
            class_key=ExpertiseClass.Fisher,
            description="Gain +55 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=55,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BOUNCING KICK (Companion Battle)
# -----------------------------------------------------------------------------

class BouncingKickI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            name="Bouncing Kick I",
            class_key=ExpertiseClass.Fisher,
            description="Leap forward onto an enemy and bounce back, dealing 2-4 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BouncingKickII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            name="Bouncing Kick II",
            class_key=ExpertiseClass.Fisher,
            description="Leap forward onto an enemy and bounce back, dealing 3-5 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 5))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BouncingKickIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            name="Bouncing Kick III",
            class_key=ExpertiseClass.Fisher,
            description="Leap forward onto an enemy and bounce back, dealing 4-6 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BouncingKickIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            name="Bouncing Kick IV",
            class_key=ExpertiseClass.Fisher,
            description="Leap forward onto an enemy and bounce back, dealing 5-7 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 7))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BouncingKickV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC38",
            name="Bouncing Kick V",
            class_key=ExpertiseClass.Fisher,
            description="Leap forward onto an enemy and bounce back, dealing 6-8 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(6, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SUNBASK TURTLE ABILITIES
# -----------------------------------------------------------------------------
# Shellter (Companion Battle)
# -----------------------------------------------------------------------------

class ShellterI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1A",
            name="Shellter I",
            class_key=ExpertiseClass.Fisher,
            description="Gain +2 Constitution for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=2,
            value=2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShellterII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1A",
            name="Shellter II",
            class_key=ExpertiseClass.Fisher,
            description="Gain +4 Constitution for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=2,
            value=4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShellterIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1A",
            name="Shellter III",
            class_key=ExpertiseClass.Fisher,
            description="Gain +6 Constitution for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=2,
            value=6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShellterIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1A",
            name="Shellter IV",
            class_key=ExpertiseClass.Fisher,
            description="Gain +8 Constitution for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=2,
            value=8,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShellterV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1A",
            name="Shellter V",
            class_key=ExpertiseClass.Fisher,
            description="Gain +10 Constitution for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=2,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# TERRASPIN (Companion Battle)
# -----------------------------------------------------------------------------

class TerraspinI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            name="Terraspin I",
            class_key=ExpertiseClass.Fisher,
            description="Spin rapidly and bounce between up to 2 enemies, dealing 25% of your current Con as damage + 1 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().constitution) + 1

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TerraspinII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            name="Terraspin II",
            class_key=ExpertiseClass.Fisher,
            description="Spin rapidly and bounce between up to 2 enemies, dealing 25% of your current Con as damage + 2 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().constitution) + 2

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TerraspinIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            name="Terraspin III",
            class_key=ExpertiseClass.Fisher,
            description="Spin rapidly and bounce between up to 2 enemies, dealing 25% of your current Con as damage + 3 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().constitution) + 3

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TerraspinIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            name="Terraspin IV",
            class_key=ExpertiseClass.Fisher,
            description="Spin rapidly and bounce between up to 2 enemies, dealing 25% of your current Con as damage + 4 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().constitution) + 4

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TerraspinV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC22",
            name="Terraspin V",
            class_key=ExpertiseClass.Fisher,
            description="Spin rapidly and bounce between up to 2 enemies, dealing 25% of your current Con as damage + 5 damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().constitution) + 4

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DEFLECTION (Companion Battle)
# -----------------------------------------------------------------------------

class DeflectionI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Deflection I",
            class_key=ExpertiseClass.Fisher,
            description="Gain 15% damage reflection for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=1,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeflectionII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Deflection II",
            class_key=ExpertiseClass.Fisher,
            description="Gain 30% damage reflection for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=1,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeflectionIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Deflection III",
            class_key=ExpertiseClass.Fisher,
            description="Gain 45% damage reflection for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=1,
            value=0.45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeflectionIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Deflection IV",
            class_key=ExpertiseClass.Fisher,
            description="Gain 60% damage reflection for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=1,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeflectionV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Deflection V",
            class_key=ExpertiseClass.Fisher,
            description="Gain 75% damage reflection for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# FLYING FOX ABILITIES
# -----------------------------------------------------------------------------
# TO THE SKIES (Companion Battle)
# -----------------------------------------------------------------------------

class ToTheSkiesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="To The Skies I",
            class_key=ExpertiseClass.Guardian,
            description="Gain +15 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToTheSkiesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="To The Skies II",
            class_key=ExpertiseClass.Guardian,
            description="Gain +25 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToTheSkiesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="To The Skies III",
            class_key=ExpertiseClass.Guardian,
            description="Gain +35 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToTheSkiesIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="To The Skies IV",
            class_key=ExpertiseClass.Guardian,
            description="Gain +45 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToTheSkiesV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="To The Skies V",
            class_key=ExpertiseClass.Guardian,
            description="Gain +55 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=55,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GUST (Companion Battle)
# -----------------------------------------------------------------------------

class GustI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Gust I",
            class_key=ExpertiseClass.Guardian,
            description="Summon a gale against up to 2 enemies that decreases their Dex by 3 for 2 turns and deals 1-3 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GustII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Gust II",
            class_key=ExpertiseClass.Guardian,
            description="Summon a gale against up to 2 enemies that decreases their Dex by 3 for 2 turns and deals 2-4 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GustIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Gust III",
            class_key=ExpertiseClass.Guardian,
            description="Summon a gale against up to 2 enemies that decreases their Dex by 3 for 2 turns and deals 3-5 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GustIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Gust IV",
            class_key=ExpertiseClass.Guardian,
            description="Summon a gale against up to 2 enemies that decreases their Dex by 3 for 2 turns and deals 4-6 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GustV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Gust V",
            class_key=ExpertiseClass.Guardian,
            description="Summon a gale against up to 2 enemies that decreases their Dex by 3 for 2 turns and deals 5-7 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 7), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# LUNGE (Companion Battle)
# -----------------------------------------------------------------------------

class LungeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Lunge I",
            class_key=ExpertiseClass.Guardian,
            description="Leap towards an enemy and bite, dealing 1 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = 1

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LungeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Lunge II",
            class_key=ExpertiseClass.Guardian,
            description="Leap towards an enemy and bite, dealing 2 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = 2

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LungeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Lunge III",
            class_key=ExpertiseClass.Guardian,
            description="Leap towards an enemy and bite, dealing 3 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = 3

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LungeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Lunge IV",
            class_key=ExpertiseClass.Guardian,
            description="Leap towards an enemy and bite, dealing 4 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = 4

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LungeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Lunge V",
            class_key=ExpertiseClass.Guardian,
            description="Leap towards an enemy and bite, dealing 5 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = 5

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SHADOWFOOT RACCOON ABILITIES
# -----------------------------------------------------------------------------
# SNEAKY MANEUVERS (Dueling)
# -----------------------------------------------------------------------------

class SneakyManeuversI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Sneaky Maneuvers I",
            class_key=ExpertiseClass.Merchant,
            description="Gain 1 coin for each enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        adjusted_coins: int = 1 * len(targets)
        caster.get_inventory().add_coins(adjusted_coins)
        
        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SneakyManeuversII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Sneaky Maneuvers II",
            class_key=ExpertiseClass.Merchant,
            description="Gain 2 coins for each enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        adjusted_coins: int = 2 * len(targets)
        caster.get_inventory().add_coins(adjusted_coins)

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SneakyManeuversIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Sneaky Maneuvers III",
            class_key=ExpertiseClass.Merchant,
            description="Gain 3 coins for each enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        adjusted_coins: int = 3 * len(targets)
        caster.get_inventory().add_coins(adjusted_coins)

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SneakyManeuversIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Sneaky Maneuvers IV",
            class_key=ExpertiseClass.Merchant,
            description="Gain 4 coins for each enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        adjusted_coins: int = 4 * len(targets)
        caster.get_inventory().add_coins(adjusted_coins)

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SneakyManeuversV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="Sneaky Maneuvers V",
            class_key=ExpertiseClass.Merchant,
            description="Gain 5 coins for each enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        adjusted_coins: int = 5 * len(targets)
        caster.get_inventory().add_coins(adjusted_coins)

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# INTO THE SHADOWS (Companion Battle)
# -----------------------------------------------------------------------------

class IntoTheShadowsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Into The Shadows I",
            class_key=ExpertiseClass.Merchant,
            description="Gain +15 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IntoTheShadowsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Into The Shadows II",
            class_key=ExpertiseClass.Merchant,
            description="Gain +25 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IntoTheShadowsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Into The Shadows III",
            class_key=ExpertiseClass.Merchant,
            description="Gain +35 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IntoTheShadowsIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Into The Shadows IV",
            class_key=ExpertiseClass.Merchant,
            description="Gain +45 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IntoTheShadowsV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Into The Shadows V",
            class_key=ExpertiseClass.Merchant,
            description="Gain +55 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=55,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# STRIKE FROM BEHIND (Companion Battle)
# -----------------------------------------------------------------------------

class StrikeFromBehindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Strike From Behind I",
            class_key=ExpertiseClass.Merchant,
            description="Suddenly appear from the shadows, dealing 1-2 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity, Attribute.Luck]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class StrikeFromBehindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Strike From Behind II",
            class_key=ExpertiseClass.Merchant,
            description="Suddenly appear from the shadows, dealing 2-3 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class StrikeFromBehindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Strike From Behind III",
            class_key=ExpertiseClass.Merchant,
            description="Suddenly appear from the shadows, dealing 1-2 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class StrikeFromBehindIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Strike From Behind IV",
            class_key=ExpertiseClass.Merchant,
            description="Suddenly appear from the shadows, dealing 1-2 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class StrikeFromBehindV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Strike From Behind V",
            class_key=ExpertiseClass.Merchant,
            description="Suddenly appear from the shadows, dealing 5-6 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# LUCKY PAWS (Companion Battle)
# -----------------------------------------------------------------------------

class LuckyPawsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Lucky Paws I",
            class_key=ExpertiseClass.Merchant,
            description="Gain +15 Luck for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LuckyPawsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Lucky Paws II",
            class_key=ExpertiseClass.Merchant,
            description="Gain +30 Luck for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=2,
            value=30,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LuckyPawsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Lucky Paws III",
            class_key=ExpertiseClass.Merchant,
            description="Gain +45 Luck for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=2,
            value=45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LuckyPawsIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Lucky Paws IV",
            class_key=ExpertiseClass.Merchant,
            description="Gain +60 Luck for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
            value=60,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class LuckyPawsV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Lucky Paws V",
            class_key=ExpertiseClass.Merchant,
            description="Gain +75 Luck for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = LckBuff(
            turns_remaining=2,
            value=75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# TANGLEWEB SPIDER ABILITIES
# -----------------------------------------------------------------------------
# WEB SHOT (Dueling)
# -----------------------------------------------------------------------------

class WebShotI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Web Shot I",
            class_key=ExpertiseClass.Guardian,
            description="Launch a web at an enemy, decreasing their Dexterity by 3 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WebShotII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Web Shot II",
            class_key=ExpertiseClass.Guardian,
            description="Launch a web at an enemy, decreasing their Dexterity by 6 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WebShotIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Web Shot III",
            class_key=ExpertiseClass.Guardian,
            description="Launch a web at an enemy, decreasing their Dexterity by 9 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-9,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WebShotIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Web Shot IV",
            class_key=ExpertiseClass.Guardian,
            description="Launch a web at an enemy, decreasing their Dexterity by 12 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-12,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WebShotV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Web Shot V",
            class_key=ExpertiseClass.Guardian,
            description="Launch a web at an enemy, decreasing their Dexterity by 15 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CRAFT WEB (Companion Battle)
# -----------------------------------------------------------------------------

class CraftWebI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Craft Web I",
            class_key=ExpertiseClass.Guardian,
            description="Spin an entangling web, decreasing the Dexterity of all enemies by 5 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CraftWebII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Craft Web II",
            class_key=ExpertiseClass.Guardian,
            description="Spin an entangling web, decreasing the Dexterity of all enemies by 10 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CraftWebIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Craft Web III",
            class_key=ExpertiseClass.Guardian,
            description="Spin an entangling web, decreasing the Dexterity of all enemies by 15 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CraftWebIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Craft Web IV",
            class_key=ExpertiseClass.Guardian,
            description="Spin an entangling web, decreasing the Dexterity of all enemies by 20 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CraftWebV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD78\uFE0F",
            name="Craft Web V",
            class_key=ExpertiseClass.Guardian,
            description="Spin an entangling web, decreasing the Dexterity of all enemies by 25 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WRAP THE MEAL (Companion Battle)
# -----------------------------------------------------------------------------

class WrapTheMealI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2F",
            name="Wrap the Meal I",
            class_key=ExpertiseClass.Guardian,
            description="Choose an enemy. If they have a Dexterity debuff, cause Faltering for 2 turns and deal 1 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        valid_targets = list(filter(lambda x: any(se.key == StatusEffectKey.DexDebuff for se in x.get_dueling().status_effects), targets))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, valid_targets, range(1, 1), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrapTheMealII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2F",
            name="Wrap the Meal II",
            class_key=ExpertiseClass.Guardian,
            description="Choose an enemy. If they have a Dexterity debuff, cause Faltering for 2 turns and deal 2 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        valid_targets = list(filter(lambda x: any(se.key == StatusEffectKey.DexDebuff for se in x.get_dueling().status_effects), targets))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, valid_targets, range(2, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrapTheMealIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2F",
            name="Wrap the Meal III",
            class_key=ExpertiseClass.Guardian,
            description="Choose an enemy. If they have a Dexterity debuff, cause Faltering for 2 turns and deal 3 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        valid_targets = list(filter(lambda x: any(se.key == StatusEffectKey.DexDebuff for se in x.get_dueling().status_effects), targets))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, valid_targets, range(3, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrapTheMealIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2F",
            name="Wrap the Meal IV",
            class_key=ExpertiseClass.Guardian,
            description="Choose an enemy. If they have a Dexterity debuff, cause Faltering for 2 turns and deal 4 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        valid_targets = list(filter(lambda x: any(se.key == StatusEffectKey.DexDebuff for se in x.get_dueling().status_effects), targets))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, valid_targets, range(4, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrapTheMealV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2F",
            name="Wrap the Meal V",
            class_key=ExpertiseClass.Guardian,
            description="Choose an enemy. If they have a Dexterity debuff, cause Faltering for 2 turns and deal 5 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        valid_targets = list(filter(lambda x: any(se.key == StatusEffectKey.DexDebuff for se in x.get_dueling().status_effects), targets))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, valid_targets, range(5, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PATIENT STRIKE (Companion Battle)
# -----------------------------------------------------------------------------

class PatientStrikeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Patient Strike I",
            class_key=ExpertiseClass.Guardian,
            description="Gain +1 damage on your next attack. This buff is removed when attacking and lasts for 10 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=10,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PatientStrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Patient Strike II",
            class_key=ExpertiseClass.Guardian,
            description="Gain +2 damage on your next attack. This buff is removed when attacking and lasts for 10 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=10,
            value=2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PatientStrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Patient Strike III",
            class_key=ExpertiseClass.Guardian,
            description="Gain +3 damage on your next attack. This buff is removed when attacking and lasts for 10 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=10,
            value=3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PatientStrikeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Patient Strike IV",
            class_key=ExpertiseClass.Guardian,
            description="Gain +4 damage on your next attack. This buff is removed when attacking and lasts for 10 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=10,
            value=4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PatientStrikeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1",
            name="Patient Strike V",
            class_key=ExpertiseClass.Guardian,
            description="Gain +5 damage on your next attack. This buff is removed when attacking and lasts for 10 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=10,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PALE WALKER SPIDER ABILITIES
# -----------------------------------------------------------------------------
# VENOMOUS BITE (Dueling)
# -----------------------------------------------------------------------------

class VenomousBiteI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Venomous Bite I",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 1-2 damage with a 15% chance to cause Poisoned for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        
        poisoned = Poisoned(
            turns_remaining=3,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.15:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VenomousBiteII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Venomous Bite II",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 2-3 damage with a 30% chance to cause Poisoned for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        
        poisoned = Poisoned(
            turns_remaining=3,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.3:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VenomousBiteIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Venomous Bite III",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 3-4 damage with a 45% chance to cause Poisoned for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        
        poisoned = Poisoned(
            turns_remaining=3,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.45:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VenomousBiteIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Venomous Bite IV",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 4-5 damage with a 60% chance to cause Poisoned for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        
        poisoned = Poisoned(
            turns_remaining=3,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.6:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VenomousBiteV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Venomous Bite V",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 5-6 damage with a 75% chance to cause Poisoned for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        poisoned = Poisoned(
            turns_remaining=3,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.75:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GHOSTLY MOVEMENT (Companion Battle)
# -----------------------------------------------------------------------------

class GhostlyMovementI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC7B",
            name="Ghostly Movement I",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 5% damage resistance per point of Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=1,
            value=0.05 * caster.get_combined_attributes().dexterity,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GhostlyMovementII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC7B",
            name="Ghostly Movement II",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 4% damage resistance per point of Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=1,
            value=0.04 * caster.get_combined_attributes().dexterity,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GhostlyMovementIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC7B",
            name="Ghostly Movement III",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 3% damage resistance per point of Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.03 * caster.get_combined_attributes().dexterity,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GhostlyMovementIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC7B",
            name="Ghostly Movement IV",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 2% damage resistance per point of Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.02 * caster.get_combined_attributes().dexterity,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GhostlyMovementV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC7B",
            name="Ghostly Movement V",
            class_key=ExpertiseClass.Alchemist,
            description="Gain 1% damage resistance per point of Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=3,
            value=0.01 * caster.get_combined_attributes().dexterity,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DEADLY VENOM (Companion Battle)
# -----------------------------------------------------------------------------

class DeadlyVenomI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Deadly Venom I",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 1-2 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        
        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeadlyVenomII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Deadly Venom II",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 2-3 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        
        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeadlyVenomIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Deadly Venom III",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 3-4 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        
        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeadlyVenomIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Deadly Venom IV",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 4-5 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        
        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeadlyVenomV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Deadly Venom V",
            class_key=ExpertiseClass.Alchemist,
            description="Leap towards an enemy and bite, dealing 5-6 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GLASS PIERCE (Companion Battle)
# -----------------------------------------------------------------------------

class GlassPierceI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Glass Pierce I",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 1-2 damage to an enemy + 3 additional damage if they're poisoned.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        any_poisoned = any(se.key == StatusEffectKey.Poisoned for target in targets for se in target.get_dueling().status_effects)

        damage = range(1, 2) if not any_poisoned else range(3, 5)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GlassPierceII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Glass Pierce II",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2-3 damage to an enemy + 5 additional damage if they're poisoned.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        any_poisoned = any(se.key == StatusEffectKey.Poisoned for target in targets for se in target.get_dueling().status_effects)

        damage = range(2, 3) if not any_poisoned else range(7, 8)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GlassPierceIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Glass Pierce III",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 3-4 damage to an enemy + 7 additional damage if they're poisoned.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        any_poisoned = any(se.key == StatusEffectKey.Poisoned for target in targets for se in target.get_dueling().status_effects)

        damage = range(3, 4) if not any_poisoned else range(10, 11)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GlassPierceIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Glass Pierce IV",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 4-5 damage to an enemy + 9 additional damage if they're poisoned.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        any_poisoned = any(se.key == StatusEffectKey.Poisoned for target in targets for se in target.get_dueling().status_effects)

        damage = range(4, 5) if not any_poisoned else range(13, 14)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GlassPierceV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Glass Pierce V",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 5-6 damage to an enemy + 11 additional damage if they're poisoned.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        any_poisoned = any(se.key == StatusEffectKey.Poisoned for target in targets for se in target.get_dueling().status_effects)

        damage = range(5, 6) if not any_poisoned else range(16, 17)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# VERDANT SLITHERER ABILITIES
# -----------------------------------------------------------------------------
# TOXUNGEN (Companion Battle)
# -----------------------------------------------------------------------------

class ToxungenI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxungen I",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxin at an enemy, dealing 1-2 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToxungenII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxungen II",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxin at an enemy, dealing 2-3 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToxungenIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxungen III",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxin at an enemy, dealing 3-4 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToxungenIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxungen IV",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxin at an enemy, dealing 4-5 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToxungenV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxungen V",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxin at an enemy, dealing 5-6 damage and causing Poisoned for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HYPNOTIC GAZE (Companion Battle)
# -----------------------------------------------------------------------------

class HypnoticGazeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFF",
            name="Hypnotic Gaze I",
            class_key=ExpertiseClass.Alchemist,
            description="Stare deeply into an enemy, decreasing their Strength, Dexterity, and Luck by 5 for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HypnoticGazeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFF",
            name="Hypnotic Gaze II",
            class_key=ExpertiseClass.Alchemist,
            description="Stare deeply into an enemy, decreasing their Strength, Dexterity, and Luck by 10 for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HypnoticGazeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFF",
            name="Hypnotic Gaze III",
            class_key=ExpertiseClass.Alchemist,
            description="Stare deeply into an enemy, decreasing their Strength, Dexterity, and Luck by 15 for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HypnoticGazeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFF",
            name="Hypnotic Gaze IV",
            class_key=ExpertiseClass.Alchemist,
            description="Stare deeply into an enemy, decreasing their Strength, Dexterity, and Luck by 20 for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HypnoticGazeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFF",
            name="Hypnotic Gaze V",
            class_key=ExpertiseClass.Alchemist,
            description="Stare deeply into an enemy, decreasing their Strength, Dexterity, and Luck by 25 for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-25,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-25,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# COILED STRIKE (Companion Battle)
# -----------------------------------------------------------------------------

class CoiledStrikeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            name="Coiled Strike I",
            class_key=ExpertiseClass.Alchemist,
            description="Rear up and strike an enemy, dealing 2-4 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CoiledStrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            name="Coiled Strike II",
            class_key=ExpertiseClass.Alchemist,
            description="Rear up and strike an enemy, dealing 3-5 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 5))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CoiledStrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            name="Coiled Strike III",
            class_key=ExpertiseClass.Alchemist,
            description="Rear up and strike an enemy, dealing 4-6 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CoiledStrikeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            name="Coiled Strike IV",
            class_key=ExpertiseClass.Alchemist,
            description="Rear up and strike an enemy, dealing 5-7 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 7))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CoiledStrikeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC0D",
            name="Coiled Strike V",
            class_key=ExpertiseClass.Alchemist,
            description="Rear up and strike an enemy, dealing 6-8 damage.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(6, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GNASHTUSK BOAR ABILITIES
# -----------------------------------------------------------------------------
# GORE (Companion Battle)
# -----------------------------------------------------------------------------

class GoreI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 1-2 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GoreII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GoreIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 3-4 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GoreIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 4-5 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GoreV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Gore V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-6 damage with a 50% chance to cause Bleeding for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        bleed = Bleeding(
            turns_remaining=2,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# THICK HIDE (Companion Battle)
# -----------------------------------------------------------------------------

class ThickHideI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            name="Thick Hide I",
            class_key=ExpertiseClass.Guardian,
            description="Restore 15% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.15)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThickHideII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            name="Thick Hide II",
            class_key=ExpertiseClass.Guardian,
            description="Restore 30% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.3)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThickHideIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            name="Thick Hide III",
            class_key=ExpertiseClass.Guardian,
            description="Restore 45% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.45)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThickHideIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            name="Thick Hide IV",
            class_key=ExpertiseClass.Guardian,
            description="Restore 60% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.6)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThickHideV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC17",
            name="Thick Hide V",
            class_key=ExpertiseClass.Guardian,
            description="Restore 75% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.75)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CHARGE (Companion Battle)
# -----------------------------------------------------------------------------

class ChargeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 1-2 damage and cause Faltering with a 10% chance for 2 turns. Reduce your Dexterity and Strength by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity and Strength is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects += [dex_debuff, str_debuff]
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ChargeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage and cause Faltering with a 20% chance for 2 turns. Reduce your Dexterity and Strength by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity and Strength is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects += [dex_debuff, str_debuff]
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ChargeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 3-4 damage and cause Faltering with a 30% chance for 2 turns. Reduce your Dexterity and Strength by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity and Strength is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects += [dex_debuff, str_debuff]
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ChargeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 4-5 damage and cause Faltering with a 40% chance for 2 turns. Reduce your Dexterity and Strength by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity and Strength is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects += [dex_debuff, str_debuff]
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ChargeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD31",
            name="Charge V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-6 damage and cause Faltering with a 50% chance for 2 turns. Reduce your Dexterity and Strength by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity and Strength is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects += [dex_debuff, str_debuff]
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# VOIDSEEN CAT ABILITIES
# -----------------------------------------------------------------------------
# EXPOSE TUMMY (Companion Battle)
# -----------------------------------------------------------------------------

class ExposeTummyI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC08",
            name="Expose Tummy I",
            class_key=ExpertiseClass.Fisher,
            description="Roll over on the ground, causing an enemy to be Charmed for 1 turn.",
            flavor_text="",
            mana_cost=15,
            cooldown=6,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=1,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ExposeTummyII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC08",
            name="Expose Tummy II",
            class_key=ExpertiseClass.Fisher,
            description="Roll over on the ground, causing an enemy to be Charmed for 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=6,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ExposeTummyIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC08",
            name="Expose Tummy III",
            class_key=ExpertiseClass.Fisher,
            description="Roll over on the ground, causing an enemy to be Charmed for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=6,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ExposeTummyIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC08",
            name="Expose Tummy IV",
            class_key=ExpertiseClass.Fisher,
            description="Roll over on the ground, causing an enemy to be Charmed for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=5,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ExposeTummyV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC08",
            name="Expose Tummy V",
            class_key=ExpertiseClass.Fisher,
            description="Roll over on the ground, causing an enemy to be Charmed for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MANA BURN (Companion Battle)
# -----------------------------------------------------------------------------

class ManaBurnI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Burn I",
            class_key=ExpertiseClass.Fisher,
            description="Unleash a burst of power, dealing 10% of your current mana as damage against up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.1 * caster.get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaBurnII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Burn II",
            class_key=ExpertiseClass.Fisher,
            description="Unleash a burst of power, dealing 20% of your current mana as damage against up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.2 * caster.get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaBurnIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Burn III",
            class_key=ExpertiseClass.Fisher,
            description="Unleash a burst of power, dealing 30% of your current mana as damage against up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.3 * caster.get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaBurnIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Burn IV",
            class_key=ExpertiseClass.Fisher,
            description="Unleash a burst of power, dealing 40% of your current mana as damage against up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.4 * caster.get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaBurnV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Burn V",
            class_key=ExpertiseClass.Fisher,
            description="Unleash a burst of power, dealing 50% of your current mana as damage against up to 2 enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.5 * caster.get_expertise().mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SIPHONING SWIPE (Companion Battle)
# -----------------------------------------------------------------------------

class SiphoningSwipeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Siphoning Swipe I",
            class_key=ExpertiseClass.Fisher,
            description="Strike with your claws at all enemies, dealing 1-2 damage and stealing 1 mana from each.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        mana_to_steal = 1
        for i, target in enumerate(targets):
            if target.get_expertise().mana > mana_to_steal:
                target.get_expertise().remove_mana(mana_to_steal)
                caster.get_expertise().restore_mana(mana_to_steal)
                result_str += "\n{0} stole " + f"{mana_to_steal} mana from " + "{" + f"{i + 1}" + "}"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SiphoningSwipeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Siphoning Swipe II",
            class_key=ExpertiseClass.Fisher,
            description="Strike with your claws at all enemies, dealing 2-3 damage and stealing 2 mana from each.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        mana_to_steal = 2
        for i, target in enumerate(targets):
            if target.get_expertise().mana > mana_to_steal:
                target.get_expertise().remove_mana(mana_to_steal)
                caster.get_expertise().restore_mana(mana_to_steal)
                result_str += "\n{0} stole " + f"{mana_to_steal} mana from " + "{" + f"{i + 1}" + "}"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SiphoningSwipeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Siphoning Swipe III",
            class_key=ExpertiseClass.Fisher,
            description="Strike with your claws at all enemies, dealing 3-4 damage and stealing 3 mana from each.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        mana_to_steal = 3
        for i, target in enumerate(targets):
            if target.get_expertise().mana > mana_to_steal:
                target.get_expertise().remove_mana(mana_to_steal)
                caster.get_expertise().restore_mana(mana_to_steal)
                result_str += "\n{0} stole " + f"{mana_to_steal} mana from " + "{" + f"{i + 1}" + "}"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SiphoningSwipeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Siphoning Swipe IV",
            class_key=ExpertiseClass.Fisher,
            description="Strike with your claws at all enemies, dealing 4-5 damage and stealing 4 mana from each.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        mana_to_steal = 4
        for i, target in enumerate(targets):
            if target.get_expertise().mana > mana_to_steal:
                target.get_expertise().remove_mana(mana_to_steal)
                caster.get_expertise().restore_mana(mana_to_steal)
                result_str += "\n{0} stole " + f"{mana_to_steal} mana from " + "{" + f"{i + 1}" + "}"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SiphoningSwipeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Siphoning Swipe IV",
            class_key=ExpertiseClass.Fisher,
            description="Strike with your claws at all enemies, dealing 5-6 damage and stealing 5 mana from each.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        mana_to_steal = 5
        for i, target in enumerate(targets):
            if target.get_expertise().mana > mana_to_steal:
                target.get_expertise().remove_mana(mana_to_steal)
                caster.get_expertise().restore_mana(mana_to_steal)
                result_str += "\n{0} stole " + f"{mana_to_steal} mana from " + "{" + f"{i + 1}" + "}"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# VOIDSEEN PUP ABILITIES
# -----------------------------------------------------------------------------
# MIGHT OF THE VOID (Dueling/Companion Battle)
# -----------------------------------------------------------------------------

class MightOfTheVoidI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Might of the Void I",
            class_key=ExpertiseClass.Guardian,
            description="Gain +1 Strength for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = StrBuff(
            turns_remaining=5,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightOfTheVoidII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Might of the Void II",
            class_key=ExpertiseClass.Guardian,
            description="Gain +2 Strength for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = StrBuff(
            turns_remaining=5,
            value=2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightOfTheVoidIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Might of the Void III",
            class_key=ExpertiseClass.Guardian,
            description="Gain +3 Strength for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = StrBuff(
            turns_remaining=5,
            value=3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightOfTheVoidIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Might of the Void IV",
            class_key=ExpertiseClass.Guardian,
            description="Gain +4 Strength for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = StrBuff(
            turns_remaining=5,
            value=4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightOfTheVoidV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Might of the Void V",
            class_key=ExpertiseClass.Guardian,
            description="Gain +5 Strength for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = StrBuff(
            turns_remaining=5,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# RECKLESS BITE (Companion Battle)
# -----------------------------------------------------------------------------

class RecklessBiteI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Reckless Bite I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 10% of your current Strength as damage to an enemy. Decrease your Dexterity by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.1 * caster.get_combined_attributes().strength)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity is reduced by 5 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects.append(dex_debuff)
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RecklessBiteII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Reckless Bite II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 20% of your current Strength as damage to an enemy. Decrease your Dexterity by 10 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.2 * caster.get_combined_attributes().strength)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity is reduced by 10 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects.append(dex_debuff)
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RecklessBiteIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Reckless Bite III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 30% of your current Strength as damage to an enemy. Decrease your Dexterity by 15 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.3 * caster.get_combined_attributes().strength)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity is reduced by 15 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects.append(dex_debuff)
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RecklessBiteIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Reckless Bite IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 40% of your current Strength as damage to an enemy. Decrease your Dexterity by 20 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.4 * caster.get_combined_attributes().strength)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity is reduced by 20 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects.append(dex_debuff)
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RecklessBiteV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Reckless Bite IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 50% of your current Strength as damage to an enemy. Decrease your Dexterity by 25 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.5 * caster.get_combined_attributes().strength)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}! Your Dexterity is reduced by 25 for 2 turns.\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-25,
            source_str=self.get_icon_and_name()
        )

        caster.get_dueling().status_effects.append(dex_debuff)
        caster.get_expertise().update_stats(caster.get_combined_attributes())

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# THE DARK BARK (Companion Battle)
# -----------------------------------------------------------------------------

class TheDarkBarkI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="The Dark Bark I",
            class_key=ExpertiseClass.Guardian,
            description="Bark with the power of the Void, causing Faltering on up to 3 enemies for 2 turns. The chance to Falter is equal to 50% of your current Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        chance = 0.5 * caster.get_combined_attributes().strength / 100
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=chance,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TheDarkBarkII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="The Dark Bark II",
            class_key=ExpertiseClass.Guardian,
            description="Bark with the power of the Void, causing Faltering on up to 3 enemies for 2 turns. The chance to Falter is equal to 75% of your current Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        chance = 0.75 * caster.get_combined_attributes().strength / 100
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=chance,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TheDarkBarkIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="The Dark Bark III",
            class_key=ExpertiseClass.Guardian,
            description="Bark with the power of the Void, causing Faltering on up to 3 enemies for 2 turns. The chance to Falter is equal to 100% of your current Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        chance = 1 * caster.get_combined_attributes().strength / 100
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=chance,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TheDarkBarkIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="The Dark Bark IV",
            class_key=ExpertiseClass.Guardian,
            description="Bark with the power of the Void, causing Faltering on up to 3 enemies for 2 turns. The chance to Falter is equal to 125% of your current Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        chance = 1.25 * caster.get_combined_attributes().strength / 100
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=chance,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TheDarkBarkV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="The Dark Bark V",
            class_key=ExpertiseClass.Guardian,
            description="Bark with the power of the Void, causing Faltering on up to 3 enemies for 2 turns. The chance to Falter is equal to 150% of your current Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        chance = 1.5 * caster.get_combined_attributes().strength / 100
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=chance,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DEEPWOOD CUB ABILITIES
# -----------------------------------------------------------------------------
# BEAR DOWN (Companion Battle)
# -----------------------------------------------------------------------------

class BearDownI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Bear Down I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 1-2 damage to an enemy twice.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 2))
        results += self._use_damage_ability(caster, targets, range(1, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BearDownII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Bear Down II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to an enemy twice.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 3))
        results += self._use_damage_ability(caster, targets, range(2, 3))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BearDownIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Bear Down III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 3-4 damage to an enemy twice.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 4))
        results += self._use_damage_ability(caster, targets, range(3, 4))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BearDownIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Bear Down IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 4-5 damage to an enemy twice.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 5))
        results += self._use_damage_ability(caster, targets, range(4, 5))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BearDownV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC3E",
            name="Bear Down V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-6 damage to an enemy twice.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 6))
        results += self._use_damage_ability(caster, targets, range(5, 6))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BULK ENDURANCE (Companion Battle)
# -----------------------------------------------------------------------------

class BulkEnduranceI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDF8",
            name="Bulk Endurance I",
            class_key=ExpertiseClass.Guardian,
            description="Restore your Armor equal to 5% of your current health. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = ceil(0.05 * caster.get_expertise().hp)
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BulkEnduranceII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDF8",
            name="Bulk Endurance II",
            class_key=ExpertiseClass.Guardian,
            description="Restore your Armor equal to 10% of your current health. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = ceil(0.1 * caster.get_expertise().hp)
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BulkEnduranceIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDF8",
            name="Bulk Endurance III",
            class_key=ExpertiseClass.Guardian,
            description="Restore your Armor equal to 15% of your current health. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = ceil(0.15 * caster.get_expertise().hp)
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BulkEnduranceIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDF8",
            name="Bulk Endurance IV",
            class_key=ExpertiseClass.Guardian,
            description="Restore your Armor equal to 20% of your current health. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = ceil(0.2 * caster.get_expertise().hp)
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BulkEnduranceV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDF8",
            name="Bulk Endurance V",
            class_key=ExpertiseClass.Guardian,
            description="Restore your Armor equal to 25% of your current health. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = ceil(0.25 * caster.get_expertise().hp)
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HIBERNATE (Companion Battle)
# -----------------------------------------------------------------------------

class HibernateI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Hibernate I",
            class_key=ExpertiseClass.Guardian,
            description="Put yourself to Sleep for 2 turns and regenerate 10% of your health at the start of each turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping = Sleeping(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [sleeping, regenerating])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HibernateII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Hibernate II",
            class_key=ExpertiseClass.Guardian,
            description="Put yourself to Sleep for 2 turns and regenerate 15% of your health at the start of each turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping = Sleeping(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [sleeping, regenerating])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HibernateIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Hibernate III",
            class_key=ExpertiseClass.Guardian,
            description="Put yourself to Sleep for 2 turns and regenerate 20% of your health at the start of each turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping = Sleeping(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [sleeping, regenerating])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HibernateIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Hibernate IV",
            class_key=ExpertiseClass.Guardian,
            description="Put yourself to Sleep for 2 turns and regenerate 25% of your health at the start of each turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping = Sleeping(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [sleeping, regenerating])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HibernateV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Hibernate V",
            class_key=ExpertiseClass.Guardian,
            description="Put yourself to Sleep for 2 turns and regenerate 30% of your health at the start of each turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        sleeping = Sleeping(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [sleeping, regenerating])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# FLEETFOOT RABBIT ABILITIES
# -----------------------------------------------------------------------------
# QUICKENING PACE (Dueling)
# -----------------------------------------------------------------------------

class QuickeningPaceI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Quickening Pace I",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity by 10% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=ceil(0.1 * caster.get_combined_attributes().dexterity),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class QuickeningPaceII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Quickening Pace II",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity by 20% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=ceil(0.2 * caster.get_combined_attributes().dexterity),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class QuickeningPaceIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Quickening Pace III",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity by 30% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=ceil(0.3 * caster.get_combined_attributes().dexterity),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class QuickeningPaceIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Quickening Pace IV",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity by 40% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=ceil(0.4 * caster.get_combined_attributes().dexterity),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class QuickeningPaceV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Quickening Pace V",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Dexterity by 50% for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=ceil(0.5 * caster.get_combined_attributes().dexterity),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# FLEE! (Companion Battle)
# -----------------------------------------------------------------------------

class FleeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Flee! I",
            class_key=ExpertiseClass.Guardian,
            description="Gain 50 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FleeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Flee! II",
            class_key=ExpertiseClass.Guardian,
            description="Gain 75 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FleeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Flee! III",
            class_key=ExpertiseClass.Guardian,
            description="Gain 100 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=100,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FleeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Flee! IV",
            class_key=ExpertiseClass.Guardian,
            description="Gain 125 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=125,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FleeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Flee! V",
            class_key=ExpertiseClass.Guardian,
            description="Gain 150 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=2,
            value=150,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PUMMEL (Companion Battle)
# -----------------------------------------------------------------------------

class PummelI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pummel I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PummelII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pummel II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2 damage to an enemy 2 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PummelIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pummel III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2 damage to an enemy 3 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(2):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PummelIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pummel IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2 damage to an enemy 4 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(3):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PummelV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pummel V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2 damage to an enemy 5 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(4):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WHAT LUCK (Companion Battle)
# -----------------------------------------------------------------------------

class WhatLuckI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="What Luck I",
            class_key=ExpertiseClass.Guardian,
            description="Reduce an enemy's Luck by 15% and increase your own by the amount taken for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        total_lck_reduction: int = 0
        for target in targets:
            lck_reduction = ceil(0.15 * target.get_combined_attributes().luck)
            debuff = LckDebuff(
                turns_remaining=2,
                value=-lck_reduction,
                source_str=self.get_icon_and_name()
            )
            total_lck_reduction += lck_reduction

            results += self._use_negative_status_effect_ability(caster, [target], [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        buff = LckBuff(
            turns_remaining=2,
            value=total_lck_reduction,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [buff])
        result_str += "\n".join(buff_result)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhatLuckII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="What Luck II",
            class_key=ExpertiseClass.Guardian,
            description="Reduce an enemy's Luck by 30% and increase your own by the amount taken for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        total_lck_reduction: int = 0
        for target in targets:
            lck_reduction = ceil(0.3 * target.get_combined_attributes().luck)
            debuff = LckDebuff(
                turns_remaining=2,
                value=-lck_reduction,
                source_str=self.get_icon_and_name()
            )
            total_lck_reduction += lck_reduction

            results += self._use_negative_status_effect_ability(caster, [target], [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        buff = LckBuff(
            turns_remaining=2,
            value=total_lck_reduction,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [buff])
        result_str += "\n".join(buff_result)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhatLuckIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="What Luck III",
            class_key=ExpertiseClass.Guardian,
            description="Reduce an enemy's Luck by 45% and increase your own by the amount taken for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        total_lck_reduction: int = 0
        for target in targets:
            lck_reduction = ceil(0.45 * target.get_combined_attributes().luck)
            debuff = LckDebuff(
                turns_remaining=2,
                value=-lck_reduction,
                source_str=self.get_icon_and_name()
            )
            total_lck_reduction += lck_reduction

            results += self._use_negative_status_effect_ability(caster, [target], [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        buff = LckBuff(
            turns_remaining=2,
            value=total_lck_reduction,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [buff])
        result_str += "\n".join(buff_result)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhatLuckIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="What Luck IV",
            class_key=ExpertiseClass.Guardian,
            description="Reduce an enemy's Luck by 60% and increase your own by the amount taken for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        total_lck_reduction: int = 0
        for target in targets:
            lck_reduction = ceil(0.6 * target.get_combined_attributes().luck)
            debuff = LckDebuff(
                turns_remaining=2,
                value=-lck_reduction,
                source_str=self.get_icon_and_name()
            )
            total_lck_reduction += lck_reduction

            results += self._use_negative_status_effect_ability(caster, [target], [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        buff = LckBuff(
            turns_remaining=2,
            value=total_lck_reduction,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [buff])
        result_str += "\n".join(buff_result)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhatLuckV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="What Luck IV",
            class_key=ExpertiseClass.Guardian,
            description="Reduce an enemy's Luck by 75% and increase your own by the amount taken for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []

        total_lck_reduction: int = 0
        for target in targets:
            lck_reduction = ceil(0.75 * target.get_combined_attributes().luck)
            debuff = LckDebuff(
                turns_remaining=2,
                value=-lck_reduction,
                source_str=self.get_icon_and_name()
            )
            total_lck_reduction += lck_reduction

            results += self._use_negative_status_effect_ability(caster, [target], [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        buff = LckBuff(
            turns_remaining=2,
            value=total_lck_reduction,
            source_str=self.get_icon_and_name()
        )

        buff_result = self._use_positive_status_effect_ability(caster, [caster], [buff])
        result_str += "\n".join(buff_result)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GIANT TOWER BEETLE ABILITIES
# -----------------------------------------------------------------------------
# TOWERING ARMOR (Dueling)
# -----------------------------------------------------------------------------

class ToweringArmorI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Towering Armor I",
            class_key=ExpertiseClass.Guardian,
            description="Restore 5 Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 5
        max_reduced_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_expertise().get_all_attributes() + caster.get_equipment().get_total_attribute_mods())

        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = min(caster.get_dueling().armor + armor_to_restore, max_reduced_armor)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {post_armor - org_armor} Armor!\n\n"

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToweringArmorII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Towering Armor II",
            class_key=ExpertiseClass.Guardian,
            description="Restore 10 Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 10
        max_reduced_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_expertise().get_all_attributes() + caster.get_equipment().get_total_attribute_mods())

        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = min(caster.get_dueling().armor + armor_to_restore, max_reduced_armor)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {post_armor - org_armor} Armor!\n\n"

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToweringArmorIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Towering Armor III",
            class_key=ExpertiseClass.Guardian,
            description="Restore 15 Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 15
        max_reduced_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_expertise().get_all_attributes() + caster.get_equipment().get_total_attribute_mods())

        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = min(caster.get_dueling().armor + armor_to_restore, max_reduced_armor)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {post_armor - org_armor} Armor!\n\n"

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToweringArmorIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Towering Armor IV",
            class_key=ExpertiseClass.Guardian,
            description="Restore 20 Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 20
        max_reduced_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_expertise().get_all_attributes() + caster.get_equipment().get_total_attribute_mods())

        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = min(caster.get_dueling().armor + armor_to_restore, max_reduced_armor)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {post_armor - org_armor} Armor!\n\n"

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str
        
        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToweringArmorV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Towering Armor V",
            class_key=ExpertiseClass.Guardian,
            description="Restore 25 Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 25
        max_reduced_armor: int = caster.get_equipment().get_total_reduced_armor(caster.get_expertise().level, caster.get_expertise().get_all_attributes() + caster.get_equipment().get_total_attribute_mods())

        org_armor = caster.get_dueling().armor
        caster.get_dueling().armor = min(caster.get_dueling().armor + armor_to_restore, max_reduced_armor)
        post_armor = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {post_armor - org_armor} Armor!\n\n"

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# TOWER STANCE (Companion Battle)
# -----------------------------------------------------------------------------

class TowerStanceI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Tower Stance I",
            class_key=ExpertiseClass.Guardian,
            description="Restore 5 Armor. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 5
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TowerStanceII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Tower Stance II",
            class_key=ExpertiseClass.Guardian,
            description="Restore 10 Armor. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 10
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TowerStanceIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Tower Stance III",
            class_key=ExpertiseClass.Guardian,
            description="Restore 15 Armor. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 15
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TowerStanceIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Tower Stance IV",
            class_key=ExpertiseClass.Guardian,
            description="Restore 20 Armor. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 20
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TowerStanceV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Tower Stance V",
            class_key=ExpertiseClass.Guardian,
            description="Restore 25 Armor. This can restore more than your maximum Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        armor_to_restore: int = 25
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()} and restored {armor_to_restore} Armor!\n\n"

        caster.get_dueling().armor += armor_to_restore

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            result_str += mana_cd_result_str

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BEETLE BASH (Companion Battle)
# -----------------------------------------------------------------------------

class BeetleBashI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            name="Beetle Bash I",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 20% of your current Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = ceil(0.2 * caster.get_dueling().armor)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BeetleBashII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            name="Beetle Bash II",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 40% of your current Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = ceil(0.4 * caster.get_dueling().armor)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BeetleBashIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            name="Beetle Bash III",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 60% of your current Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = ceil(0.6 * caster.get_dueling().armor)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BeetleBashIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            name="Beetle Bash IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 80% of your current Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = ceil(0.8 * caster.get_dueling().armor)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BeetleBashV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB2",
            name="Beetle Bash V",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 100% of your current Armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = caster.get_dueling().armor

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PLATED ARMOR (Companion Battle)
# -----------------------------------------------------------------------------

class PlatedArmorI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Plated Armor I",
            class_key=ExpertiseClass.Guardian,
            description="Gain 15% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PlatedArmorII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Plated Armor II",
            class_key=ExpertiseClass.Guardian,
            description="Gain 30% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PlatedArmorIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Plated Armor III",
            class_key=ExpertiseClass.Guardian,
            description="Gain 45% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PlatedArmorIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Plated Armor IV",
            class_key=ExpertiseClass.Guardian,
            description="Gain 60% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PlatedArmorV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD30",
            name="Plated Armor V",
            class_key=ExpertiseClass.Guardian,
            description="Gain 75% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MINIATURE BONE GOLEM ABILITIES
# -----------------------------------------------------------------------------
# THROW THE BONES (Dueling)
# -----------------------------------------------------------------------------

class ThrowTheBonesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Throw the Bones I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to up to 4 enemies and cause them to become Reverberating for 8 turns. This deals 50% more damage for each Reverberating status on the target.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=4,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StackingDamage(
            turns_remaining=8,
            value=0.5,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThrowTheBonesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Throw the Bones II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to up to 4 enemies and cause them to become Reverberating for 8 turns. This deals 75% more damage for each Reverberating status on the target.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=4,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StackingDamage(
            turns_remaining=8,
            value=0.75,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThrowTheBonesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Throw the Bones III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to up to 4 enemies and cause them to become Reverberating for 8 turns. This deals 100% more damage for each Reverberating status on the target.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=4,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StackingDamage(
            turns_remaining=8,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThrowTheBonesIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Throw the Bones IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to up to 4 enemies and cause them to become Reverberating for 8 turns. This deals 125% more damage for each Reverberating status on the target.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=4,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StackingDamage(
            turns_remaining=8,
            value=1.25,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThrowTheBonesV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Throw the Bones V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage to up to 4 enemies and cause them to become Reverberating for 8 turns. This deals 150% more damage for each Reverberating status on the target.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=4,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StackingDamage(
            turns_remaining=8,
            value=1.5,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MIGHTY BONE FIST (Companion Battle)
# -----------------------------------------------------------------------------

class MightyBoneFistI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Mighty Bone Fist I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 1-2 damage and cause Faltering with a 75% chance to trigger for 1 turn.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightyBoneFistII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Mighty Bone Fist II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 2-3 damage and cause Faltering with a 75% chance to trigger for 1 turn.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(2, 3), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightyBoneFistIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Mighty Bone Fist III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 3-4 damage and cause Faltering with a 75% chance to trigger for 1 turn.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 4), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightyBoneFistIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Mighty Bone Fist IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 4-5 damage and cause Faltering with a 75% chance to trigger for 1 turn.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 5), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MightyBoneFistV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Mighty Bone Fist V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-6 damage and cause Faltering with a 75% chance to trigger for 1 turn.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 6), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# UNDEATH IS JUST THE BEGINNING (Companion Battle)
# -----------------------------------------------------------------------------

class UndeathIsJustTheBeginningI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA6",
            name="Undeath is Just the Beginning I",
            class_key=ExpertiseClass.Guardian,
            description="Become Undying for 1 turn. You can't be reduced below 1 HP while this is active.",
            flavor_text="",
            mana_cost=20,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=1,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UndeathIsJustTheBeginningII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA6",
            name="Undeath is Just the Beginning II",
            class_key=ExpertiseClass.Guardian,
            description="Become Undying for 2 turns. You can't be reduced below 1 HP while this is active.",
            flavor_text="",
            mana_cost=20,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UndeathIsJustTheBeginningIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA6",
            name="Undeath is Just the Beginning III",
            class_key=ExpertiseClass.Guardian,
            description="Become Undying for 3 turns. You can't be reduced below 1 HP while this is active.",
            flavor_text="",
            mana_cost=20,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UndeathIsJustTheBeginningIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA6",
            name="Undeath is Just the Beginning IV",
            class_key=ExpertiseClass.Guardian,
            description="Become Undying for 3 turns. You can't be reduced below 1 HP while this is active.",
            flavor_text="",
            mana_cost=15,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UndeathIsJustTheBeginningV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA6",
            name="Undeath is Just the Beginning V",
            class_key=ExpertiseClass.Guardian,
            description="Become Undying for 3 turns. You can't be reduced below 1 HP while this is active.",
            flavor_text="",
            mana_cost=10,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = Undying(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# ERUPTION OF BONE (Companion Battle)
# -----------------------------------------------------------------------------

class EruptionOfBoneI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Eruption of Bone I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 5-8 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EruptionOfBoneII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Eruption of Bone II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 6-9 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(6, 9))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EruptionOfBoneIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Eruption of Bone III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 7-10 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(7, 10))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EruptionOfBoneIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Eruption of Bone IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 8-11 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(8, 11))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EruptionOfBoneV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Eruption of Bone V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 9-12 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=-2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(9, 12))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SILVERWING OWL ABILITIES
# -----------------------------------------------------------------------------
# MYSTIC SHROUD (Companion Battle)
# -----------------------------------------------------------------------------

class MysticShroudI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mystic Shroud I",
            class_key=ExpertiseClass.Fisher,
            description="Gain 10% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MysticShroudII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mystic Shroud II",
            class_key=ExpertiseClass.Fisher,
            description="Gain 20% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MysticShroudIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mystic Shroud III",
            class_key=ExpertiseClass.Fisher,
            description="Gain 30% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MysticShroudIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mystic Shroud IV",
            class_key=ExpertiseClass.Fisher,
            description="Gain 40% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MysticShroudV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mystic Shroud V",
            class_key=ExpertiseClass.Fisher,
            description="Gain 50% damage resistance for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=2,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# FEATHERS FLY (Companion Battle)
# -----------------------------------------------------------------------------

class FeathersFlyI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Feathers Fly I",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-2 damage to all enemies and Mark each with a silver feather for 5 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Marked(
            turns_remaining=5,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FeathersFlyII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Feathers Fly II",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-2 damage to all enemies and Mark each with a silver feather for 10 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Marked(
            turns_remaining=10,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FeathersFlyIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Feathers Fly III",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-2 damage to all enemies and Mark each with a silver feather for 10 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Marked(
            turns_remaining=10,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FeathersFlyIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Feathers Fly IV",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-2 damage to all enemies and Mark each with a silver feather for 10 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Marked(
            turns_remaining=10,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FeathersFlyV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Feathers Fly V",
            class_key=ExpertiseClass.Fisher,
            description="Deal 1-2 damage to all enemies and Mark each with a silver feather for 10 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Marked(
            turns_remaining=10,
            value=1,
            caster=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(1, 2), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WITH THE WIND (Companion Battle)
# -----------------------------------------------------------------------------

class WithTheWindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="With the Wind I",
            class_key=ExpertiseClass.Fisher,
            description="Deal 2-3 damage to each enemy multiplied by the number of Marks on them + 1, then remove that condition.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = random.randint(2, 3)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            num_marks: int = 1
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
                elif se.key == StatusEffectKey.Marked:
                    assert(isinstance(se, Marked))
                    if se.caster == caster:
                        num_marks += 1
                
            target_dueling.status_effects = [se for se in target_dueling.status_effects if (isinstance(se, Marked) and se.caster == caster)]

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage * num_marks)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            results += [NegativeAbilityResult(s, False) for s in caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, None if self._num_targets == 0 else self._target_own_group)]

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            if actual_damage_dealt > 0:
                results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct()

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({caster_dmg_reduct * 100}% Reduction)" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage{se_str}", False))

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WithTheWindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="With the Wind II",
            class_key=ExpertiseClass.Fisher,
            description="Deal 3-4 damage to each enemy multiplied by the number of Marks on them + 1, then remove that condition.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = random.randint(3, 4)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            num_marks: int = 1
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
                elif se.key == StatusEffectKey.Marked:
                    assert(isinstance(se, Marked))
                    if se.caster == caster:
                        num_marks += 1

            target_dueling.status_effects = [se for se in target_dueling.status_effects if (isinstance(se, Marked) and se.caster == caster)]

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage * num_marks)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            results += [NegativeAbilityResult(s, False) for s in caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, None if self._num_targets == 0 else self._target_own_group)]

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            if actual_damage_dealt > 0:
                results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct()

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({caster_dmg_reduct * 100}% Reduction)" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage{se_str}", False))

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WithTheWindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="With the Wind III",
            class_key=ExpertiseClass.Fisher,
            description="Deal 4-5 damage to each enemy multiplied by the number of Marks on them + 1, then remove that condition.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value
        
        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = random.randint(4, 5)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            num_marks: int = 1
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
                elif se.key == StatusEffectKey.Marked:
                    assert(isinstance(se, Marked))
                    if se.caster == caster:
                        num_marks += 1

            target_dueling.status_effects = [se for se in target_dueling.status_effects if (isinstance(se, Marked) and se.caster == caster)]

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage * num_marks)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            results += [NegativeAbilityResult(s, False) for s in caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, None if self._num_targets == 0 else self._target_own_group)]

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            if actual_damage_dealt > 0:
                results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct()

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({caster_dmg_reduct * 100}% Reduction)" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage{se_str}", False))

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WithTheWindIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="With the Wind IV",
            class_key=ExpertiseClass.Fisher,
            description="Deal 5-6 damage to each enemy multiplied by the number of Marks on them + 1, then remove that condition.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = random.randint(5, 6)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            num_marks: int = 1
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
                elif se.key == StatusEffectKey.Marked:
                    assert(isinstance(se, Marked))
                    if se.caster == caster:
                        num_marks += 1

            target_dueling.status_effects = [se for se in target_dueling.status_effects if (isinstance(se, Marked) and se.caster == caster)]

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage * num_marks)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            results += [NegativeAbilityResult(s, False) for s in caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, None if self._num_targets == 0 else self._target_own_group)]

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            if actual_damage_dealt > 0:
                results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct()

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({caster_dmg_reduct * 100}% Reduction)" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage{se_str}", False))

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WithTheWindV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="With the Wind V",
            class_key=ExpertiseClass.Fisher,
            description="Deal 6-7 damage to each enemy multiplied by the number of Marks on them + 1, then remove that condition.",
            flavor_text="",
            mana_cost=15,
            cooldown=2,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = random.randint(6, 7)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            num_marks: int = 1
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
                elif se.key == StatusEffectKey.Marked:
                    assert(isinstance(se, Marked))
                    if se.caster == caster:
                        num_marks += 1

            target_dueling.status_effects = [se for se in target_dueling.status_effects if (isinstance(se, Marked) and se.caster == caster)]

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage * num_marks)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.dexterity, 0)), damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            results += [NegativeAbilityResult(s, False) for s in caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, None if self._num_targets == 0 else self._target_own_group)]

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            if actual_damage_dealt > 0:
                results += [NegativeAbilityResult(s, False) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, None if self._num_targets == 0 else self._target_own_group)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct()

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({caster_dmg_reduct * 100}% Reduction)" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage{se_str}", False))

        mana_cd_result_str = self.remove_mana_and_set_cd(caster)
        if mana_cd_result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BLUE FLITTERWING BUTTERFLY ABILITIES
# -----------------------------------------------------------------------------
# MANA LEECH (Dueling)
# -----------------------------------------------------------------------------

class ManaLeechI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Leech I",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 1 mana from an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        
        results: List[str] = []
        for i, target in enumerate(targets):
            cur_mana = target.get_expertise().mana
            target.get_expertise().remove_mana(1)
            stolen_mana = cur_mana - target.get_expertise().mana

            results.append("{0} stole " + f"{stolen_mana}" + " mana from {" + f"{i + 1}" + "}")

        result_str += "\n".join(results)

        self.remove_mana_and_set_cd(caster)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaLeechII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Leech II",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 2 mana from an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        
        results: List[str] = []
        for i, target in enumerate(targets):
            cur_mana = target.get_expertise().mana
            target.get_expertise().remove_mana(2)
            stolen_mana = cur_mana - target.get_expertise().mana

            results.append("{0} stole " + f"{stolen_mana}" + " mana from {" + f"{i + 1}" + "}")

        result_str += "\n".join(results)

        self.remove_mana_and_set_cd(caster)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaLeechIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Leech III",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 3 mana from an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        
        results: List[str] = []
        for i, target in enumerate(targets):
            cur_mana = target.get_expertise().mana
            target.get_expertise().remove_mana(3)
            stolen_mana = cur_mana - target.get_expertise().mana

            results.append("{0} stole " + f"{stolen_mana}" + " mana from {" + f"{i + 1}" + "}")

        result_str += "\n".join(results)

        self.remove_mana_and_set_cd(caster)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaLeechIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Leech IV",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 4 mana from an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        
        results: List[str] = []
        for i, target in enumerate(targets):
            cur_mana = target.get_expertise().mana
            target.get_expertise().remove_mana(4)
            stolen_mana = cur_mana - target.get_expertise().mana

            results.append("{0} stole " + f"{stolen_mana}" + " mana from {" + f"{i + 1}" + "}")

        result_str += "\n".join(results)

        self.remove_mana_and_set_cd(caster)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ManaLeechV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Mana Leech V",
            class_key=ExpertiseClass.Alchemist,
            description="Steal 5 mana from an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        
        results: List[str] = []
        for i, target in enumerate(targets):
            cur_mana = target.get_expertise().mana
            target.get_expertise().remove_mana(5)
            stolen_mana = cur_mana - target.get_expertise().mana

            results.append("{0} stole " + f"{stolen_mana}" + " mana from {" + f"{i + 1}" + "}")

        result_str += "\n".join(results)

        self.remove_mana_and_set_cd(caster)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MESMERIZE (Companion Battle)
# -----------------------------------------------------------------------------

class MesmerizeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC96",
            name="Mesmerize I",
            class_key=ExpertiseClass.Alchemist,
            description="Flitter in front of an enemy, Charming them for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=6,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MesmerizeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC96",
            name="Mesmerize II",
            class_key=ExpertiseClass.Alchemist,
            description="Flitter in front of an enemy, Charming them for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MesmerizeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC96",
            name="Mesmerize III",
            class_key=ExpertiseClass.Alchemist,
            description="Flitter in front of an enemy, Charming them for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MesmerizeIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC96",
            name="Mesmerize IV",
            class_key=ExpertiseClass.Alchemist,
            description="Flitter in front of an enemy, Charming them for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MesmerizeV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC96",
            name="Mesmerize V",
            class_key=ExpertiseClass.Alchemist,
            description="Flitter in front of an enemy, Charming them for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Charmed(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# INNERVATE (Companion Battle)
# -----------------------------------------------------------------------------

class InnervateI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Innervate I",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 15% of your missing mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_restore: int = ceil(0.15 * (caster.get_expertise().max_mana - caster.get_expertise().mana))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {mana_to_restore} mana!\n\n"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InnervateII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Innervate II",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 30% of your missing mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_restore: int = ceil(0.3 * (caster.get_expertise().max_mana - caster.get_expertise().mana))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {mana_to_restore} mana!\n\n"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InnervateIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Innervate III",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 45% of your missing mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_restore: int = ceil(0.45 * (caster.get_expertise().max_mana - caster.get_expertise().mana))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {mana_to_restore} mana!\n\n"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InnervateIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Innervate IV",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 60% of your missing mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_restore: int = ceil(0.6 * (caster.get_expertise().max_mana - caster.get_expertise().mana))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {mana_to_restore} mana!\n\n"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class InnervateV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Innervate V",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 75% of your missing mana.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_restore: int = ceil(0.75 * (caster.get_expertise().max_mana - caster.get_expertise().mana))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and restored {mana_to_restore} mana!\n\n"

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WINGBEAT (Companion Battle)
# -----------------------------------------------------------------------------

class WingbeatI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            name="Wingbeat I",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Constitution, Dexterity, and Luck by 3 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff, con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WingbeatII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            name="Wingbeat II",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Constitution, Dexterity, and Luck by 6 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-6,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-6,
            source_str=self.get_icon_and_name()
        )

        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-6,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff, con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WingbeatIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            name="Wingbeat III",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Constitution, Dexterity, and Luck by 9 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-9,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-9,
            source_str=self.get_icon_and_name()
        )

        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-9,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-9,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff, con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WingbeatIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            name="Wingbeat IV",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Constitution, Dexterity, and Luck by 12 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-12,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-12,
            source_str=self.get_icon_and_name()
        )

        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-12,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-12,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff, con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WingbeatV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8B",
            name="Wingbeat V",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Constitution, Dexterity, and Luck by 15 for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=1,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [dex_debuff, str_debuff, lck_debuff, con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SCUTTLEDARK SCORPION ABILITIES
# -----------------------------------------------------------------------------
# INTO THE SHADOWS (Companion Battle) -- See implementation above
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# POWERFUL PIERCE (Companion Battle)
# -----------------------------------------------------------------------------

class PowerfulPierceI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            name="Powerful Pierce I",
            class_key=ExpertiseClass.Guardian,
            description="Deal 10% of an enemy's current health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []
        
        for target in targets:
            damage: int = ceil(0.1 * target.get_expertise().hp)
            results += self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PowerfulPierceII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            name="Powerful Pierce II",
            class_key=ExpertiseClass.Guardian,
            description="Deal 20% of an enemy's current health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []
        
        for target in targets:
            damage: int = ceil(0.2 * target.get_expertise().hp)
            results += self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PowerfulPierceIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            name="Powerful Pierce III",
            class_key=ExpertiseClass.Guardian,
            description="Deal 30% of an enemy's current health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []
        
        for target in targets:
            damage: int = ceil(0.3 * target.get_expertise().hp)
            results += self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PowerfulPierceIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            name="Powerful Pierce IV",
            class_key=ExpertiseClass.Guardian,
            description="Deal 40% of an enemy's current health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []
        
        for target in targets:
            damage: int = ceil(0.4 * target.get_expertise().hp)
            results += self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PowerfulPierceV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD82",
            name="Powerful Pierce V",
            class_key=ExpertiseClass.Guardian,
            description="Deal 50% of an enemy's current health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = []
        
        for target in targets:
            damage: int = ceil(0.5 * target.get_expertise().hp)
            results += self._use_damage_ability(caster, targets, range(damage, damage))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GRASPING CLAWS (Companion Battle)
# -----------------------------------------------------------------------------

class GraspingClawsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Grasping Claws I",
            class_key=ExpertiseClass.Guardian,
            description="For the next 3 turns, your attacks have a 5% chance to cause Faltering that lasts 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=3,
            value=0.05,
            status_effect=TurnSkipChance(
                turns_remaining=1,
                value=1,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GraspingClawsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Grasping Claws II",
            class_key=ExpertiseClass.Guardian,
            description="For the next 3 turns, your attacks have a 15% chance to cause Faltering that lasts 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=3,
            value=0.15,
            status_effect=TurnSkipChance(
                turns_remaining=1,
                value=1,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GraspingClawsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Grasping Claws III",
            class_key=ExpertiseClass.Guardian,
            description="For the next 3 turns, your attacks have a 25% chance to cause Faltering that lasts 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=3,
            value=0.25,
            status_effect=TurnSkipChance(
                turns_remaining=1,
                value=1,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GraspingClawsIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Grasping Claws IV",
            class_key=ExpertiseClass.Guardian,
            description="For the next 3 turns, your attacks have a 35% chance to cause Faltering that lasts 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=3,
            value=0.35,
            status_effect=TurnSkipChance(
                turns_remaining=1,
                value=1,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class GraspingClawsV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Grasping Claws V",
            class_key=ExpertiseClass.Guardian,
            description="For the next 3 turns, your attacks have a 45% chance to cause Faltering that lasts 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=0,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = AttackingChanceToApplyStatus(
            turns_remaining=3,
            value=0.45,
            status_effect=TurnSkipChance(
                turns_remaining=1,
                value=1,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WANDERBOUND RAVEN ABILITIES
# -----------------------------------------------------------------------------
# PECK PECK PECK (Companion Battle)
# -----------------------------------------------------------------------------

class PeckPeckPeckI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            name="Peck Peck Peck I",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2 damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PeckPeckPeckII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            name="Peck Peck Peck II",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2 damage to an enemy 2 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PeckPeckPeckIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            name="Peck Peck Peck III",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2 damage to an enemy 3 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(2):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PeckPeckPeckIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            name="Peck Peck Peck IV",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2 damage to an enemy 4 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(3):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PeckPeckPeckV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC26",
            name="Peck Peck Peck V",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 2 damage to an enemy 5 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 2))
        
        for _ in range(4):
            results += self._use_damage_ability(caster, targets, range(2, 2))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SHRIEKING CAW (Companion Battle)
# -----------------------------------------------------------------------------

class ShriekingCawI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Shrieking Caw I",
            class_key=ExpertiseClass.Alchemist,
            description="Emit a powerful caw, causing all enemies to deal 10% less damage for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=2,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShriekingCawII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Shrieking Caw II",
            class_key=ExpertiseClass.Alchemist,
            description="Emit a powerful caw, causing all enemies to deal 15% less damage for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=2,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShriekingCawIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Shrieking Caw III",
            class_key=ExpertiseClass.Alchemist,
            description="Emit a powerful caw, causing all enemies to deal 20% less damage for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=2,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShriekingCawIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Shrieking Caw IV",
            class_key=ExpertiseClass.Alchemist,
            description="Emit a powerful caw, causing all enemies to deal 25% less damage for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=2,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShriekingCawV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Shrieking Caw V",
            class_key=ExpertiseClass.Alchemist,
            description="Emit a powerful caw, causing all enemies to deal 30% less damage for 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=4,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgDebuff(
            turns_remaining=2,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DIVE (Companion Battle)
# -----------------------------------------------------------------------------

class DiveI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Dive I",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 10% of your current Dexterity as damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.1 * caster.get_combined_attributes().dexterity)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DiveII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Dive II",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 15% of your current Dexterity as damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.15 * caster.get_combined_attributes().dexterity)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DiveIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Dive III",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 20% of your current Dexterity as damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.2 * caster.get_combined_attributes().dexterity)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DiveIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Dive IV",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 25% of your current Dexterity as damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.25 * caster.get_combined_attributes().dexterity)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DiveV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB6",
            name="Dive V",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 30% of your current Dexterity as damage to an enemy.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage = ceil(0.3 * caster.get_combined_attributes().dexterity)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore