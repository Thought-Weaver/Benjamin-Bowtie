from __future__ import annotations
from math import ceil

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Absorption(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Absorption",
            class_key=ExpertiseClass.Guardian,
            description="Steal 25% of the average enemy health from all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        
        damage: int = ceil(0.25 * sum(target.get_expertise().max_hp for target in targets) / len(targets))
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        heal_results: List[str] = self._use_heal_ability(caster, [caster], range(damage * len(targets), damage * len(targets)))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        result_str += "\n"
        # Replace since these start from {1} but it's healing the caster
        result_str += "\n".join([s.replace("{1}", "{0}") for s in heal_results])

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Pulverize(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Pulverize",
            class_key=ExpertiseClass.Guardian,
            description="Deal damage to an enemy equal to 75% of its max health.",
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

        damage: int = ceil(0.75 * targets[0].get_expertise().max_hp)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Amass(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEB8",
            name="Amass",
            class_key=ExpertiseClass.Guardian,
            description="Increase your Con by 20 for the rest of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=20,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class BloodcoralBehemoth(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 15% chance of 4 player party (Lvl. 50-60) victory against 1
        # Avg Number of Turns (per entity): 13

        super().__init__("Bloodcoral Behemoth" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(550, ExpertiseClass.Guardian)
        self._expertise.constitution = 250
        self._expertise.strength = 150
        self._expertise.dexterity = 0
        self._expertise.intelligence = 100
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.BehemothTendrils))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.BehemothCoralArmor))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
            self._dueling.is_legendary = True
        
        self._dueling.abilities = [Absorption(), Pulverize(), Amass()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Bloodcoral Behemoth"
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
