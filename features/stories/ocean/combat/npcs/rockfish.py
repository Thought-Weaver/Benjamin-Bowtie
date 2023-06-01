from __future__ import annotations

from math import ceil
import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability, NegativeAbilityResult
from features.shared.constants import DEX_DODGE_SCALE
from features.shared.effect import ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DexDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Armorbreaker(Ability):
    def __init__(self):
        super().__init__(
            icon="\ud83d\udee1\ufe0f",
            name="Armorbreaker",
            class_key=ExpertiseClass.Guardian,
            description="Destroy all of an enemy's armor.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = []
        for i, target in enumerate(targets):
            target_dodged = random.random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))

            armor_to_remove: int = target.get_dueling().armor
            target.get_dueling().armor = 0

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" had {armor_to_remove} Armor removed!"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_ability_used_against_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RockSlam(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA8",
            name="Rock Slam",
            class_key=ExpertiseClass.Guardian,
            description="Deal 45-50 damage to 1-2 enemies and decrease their Dexterity by 25 for 4 turns",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DexDebuff(
            turns_remaining=4,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(45, 50), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CrushingJaws(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Crushing Jaws",
            class_key=ExpertiseClass.Guardian,
            description="Deal 35% of an enemy's health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = ceil(0.35 * targets[0].get_expertise().max_hp)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Rockfish(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 42% chance of 4 player party (Lvl. 40-50) victory against 1

        super().__init__("Rockfish" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Guardian)
        self._expertise.constitution = 80
        self._expertise.strength = 60
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.RockfishJaws))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.RockfishForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Armorbreaker(), RockSlam(), CrushingJaws()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Rockfish"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {}
        
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
