from __future__ import annotations

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
from features.shared.statuseffect import ConBuff, ConDebuff, DexBuff, DmgBuff, IntBuff, LckBuff, StrBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SomeMutation(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC1F",
            name="Some Mutation",
            class_key=ExpertiseClass.Fisher,
            description="Increase all of your allies' stats by 8 for the rest of the duel.",
            flavor_text="",
            mana_cost=10,
            cooldown=1,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=8,
            source_str=self.get_icon_and_name()
        )

        str_buff = StrBuff(
            turns_remaining=-1,
            value=8,
            source_str=self.get_icon_and_name()
        )

        dex_buff = DexBuff(
            turns_remaining=-1,
            value=8,
            source_str=self.get_icon_and_name()
        )

        int_buff = IntBuff(
            turns_remaining=-1,
            value=8,
            source_str=self.get_icon_and_name()
        )

        lck_buff = LckBuff(
            turns_remaining=-1,
            value=8,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff, str_buff, dex_buff, int_buff, lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FarTooManyEyes(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC41\uFE0F",
            name="Far Too Many Eyes",
            class_key=ExpertiseClass.Fisher,
            description="Increase the damage all allies deal by 50% for the rest of the duel.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=-1,
            value=0.5,
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


class ShadowsGrowingLonger(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC65",
            name="Shadows Growing Longer",
            class_key=ExpertiseClass.Fisher,
            description="Decrease the Con of all enemies by 10 for the rest of the duel.",
            flavor_text="",
            mana_cost=10,
            cooldown=1,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=-1,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class FishMaybe(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 25% chance of 4 player party (Lvl. 50-60) victory against 2
        # 20% and 13 turns for new item adjustments
        # Avg Number of Turns (per entity): 13

        super().__init__("Fish?" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.FishMaybe: 0.8
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
        
        self._expertise.add_xp_to_class_until_level(180, ExpertiseClass.Fisher)
        self._expertise.constitution = 80
        self._expertise.strength = 20
        self._expertise.dexterity = 20
        self._expertise.intelligence = 30
        self._expertise.luck = 27
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.FinsMaybe))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.FishForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SomeMutation(), ShadowsGrowingLonger(), FarTooManyEyes()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Fish?"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {
            ItemKey.FishMaybe: 0.8
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
