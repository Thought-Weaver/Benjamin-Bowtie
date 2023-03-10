from __future__ import annotations

import random

from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import DEX_DMG_SCALE, POISONED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, WeaponStats
from features.shared.statuseffect import DexBuff, IntDebuff, LckDebuff, Poisoned, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class VenomSpit(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Venom Spit",
            class_key=ExpertiseClass.Alchemist,
            description="Spit toxungen that deals 4-6 damage to all enemies with a 90% chance to Poison them for 5% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=3200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.9:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
        
        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class TerrifyingHiss(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDEF\uFE0F",
            name="Terrifying Hiss",
            class_key=ExpertiseClass.Alchemist,
            description="Decrease a target's Strength, Intelligence, and Luck by 5 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=0,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = IntDebuff(
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

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Lunge(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Lunge",
            class_key=ExpertiseClass.Alchemist,
            description="Lunge forward at an enemy, dealing 150% of your weapon damage with a 80% chance to set Poisoned for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Dexterity]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects, max(0, level_req - caster.get_expertise().level))
        damage = ceil(1.3 * base_damage)
        damage += min(ceil(damage * DEX_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        poisoned = Poisoned(
            turns_remaining=1,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random.random() < 0.8:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Camouflage(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Camouflage",
            class_key=ExpertiseClass.Alchemist,
            description="Gain +175 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=175,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class SmallSnake(NPC):
    def __init__(self, name_suffix: str=""):
        persona = NPCDuelingPersonas.Mage if random.random() < 0.67 else NPCDuelingPersonas.Specialist
        super().__init__("Small Snake" + name_suffix, NPCRoles.DungeonEnemy, persona, {
            ItemKey.LesserPoison: 0.9
        })

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(20, ExpertiseClass.Alchemist)
        self._expertise.constitution = 8
        self._expertise.strength = 0
        self._expertise.dexterity = 0
        self._expertise.intelligence = 8
        self._expertise.luck = 0
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SmallSnakeFangs))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [VenomSpit(), TerrifyingHiss(), Lunge(), Camouflage()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Small Snake"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage if random.random() < 0.67 else NPCDuelingPersonas.Specialist
        self._dueling_rewards = {
            ItemKey.LesserPoison: 0.9
        }
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()
            self._setup_inventory()

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()
            self._setup_equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()
            self._setup_xp()

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()
            self._setup_abilities()

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
