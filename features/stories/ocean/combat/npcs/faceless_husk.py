from __future__ import annotations

from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.player import Player
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConBuff, DexBuff, DexDebuff, DmgReduction, LckBuff, StrBuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Stranglehook(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF3F",
            name="Stranglehook",
            class_key=ExpertiseClass.Fisher,
            description="Deal 70-75 damage to an enemy and decrease their Dex and Str by 30 for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=30,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=30,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(70, 75), [dex_debuff, str_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShiftingForm(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B\uFE0F",
            name="Shifting Form",
            class_key=ExpertiseClass.Fisher,
            description="Gain 60% damage resistance for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=8,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=4,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Mimicry(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDFAD",
            name="Mimicry",
            class_key=ExpertiseClass.Fisher,
            description="Copy 25% of an enemy's stats for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and copied part of " + "{1}'s" " stats!\n\n"
        
        target_expertise = targets[0].get_expertise()

        con_buff = ConBuff(
            turns_remaining=5,
            value=ceil(0.25 * target_expertise.constitution),
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=5,
            value=ceil(0.25 * target_expertise.strength),
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=5,
            value=ceil(0.25 * target_expertise.dexterity),
            source_str=self.get_icon_and_name()
        )

        int_buff = DexBuff(
            turns_remaining=5,
            value=ceil(0.25 * target_expertise.intelligence),
            source_str=self.get_icon_and_name()
        )

        lck_buff = LckBuff(
            turns_remaining=5,
            value=ceil(0.25 * target_expertise.luck),
            source_str=self.get_icon_and_name()
        )
        
        results: List[str] = self._use_positive_status_effect_ability(caster, [caster], [con_buff, str_buff, dex_buff, int_buff, lck_buff])
        result_str += "\n".join([s.replace("{1}", "{0}") for s in results])

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class FacelessHusk(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 47% chance of 4 player party (Lvl. 50-60) victory against 2
        # 35% and 18 turns for new item adjustments
        # Avg Number of Turns (per entity): 21

        super().__init__("Faceless Husk" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(180, ExpertiseClass.Fisher)
        self._expertise.constitution = 80
        self._expertise.strength = 20
        self._expertise.dexterity = 20
        self._expertise.intelligence = 0
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.HuskFists))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.HuskForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [ShiftingForm(), Stranglehook(), Mimicry()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Faceless Husk"
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
