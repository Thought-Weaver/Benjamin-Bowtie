from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DmgBuff, FixedDmgTick, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class CrushThemMyKing(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Crush Them My King!",
            class_key=ExpertiseClass.Fisher,
            description="Increase an ally's damage dealt by 25% for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=3,
            value=0.25,
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


class CRABKINGCRABKING(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC51",
            name="CRAB KING! CRAB KING!",
            class_key=ExpertiseClass.Fisher,
            description="Restore 15-20 health to all allies.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(15, 20))
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class CrabServant(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 18% chance of 4 player party (Lvl. 30-40) victory against 1
        # Avg Number of Turns (per entity): 16
        
        super().__init__("Crab Servant" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Healer, {
            ItemKey.Crab: 0.85
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
        
        self._expertise.add_xp_to_class_until_level(75, ExpertiseClass.Fisher)
        self._expertise.constitution = 30
        self._expertise.strength = 0
        self._expertise.dexterity = 12
        self._expertise.intelligence = 30
        self._expertise.luck = 0
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.CrabClaws))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [CrushThemMyKing(), CRABKINGCRABKING()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Crab Servant"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Healer
        self._dueling_rewards = {
            ItemKey.Crab: 0.85
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
