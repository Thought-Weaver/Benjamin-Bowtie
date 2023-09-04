from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import ConDebuff, DexDebuff, IntDebuff, StrDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class CurseOfFrailty(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDB4",
            name="Curse of Frailty",
            class_key=ExpertiseClass.Alchemist,
            description="Unavoidably reduce an enemy's Con to 0 for 3 turns.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            debuff = ConDebuff(
                turns_remaining=3,
                value=-targets[0].get_combined_attributes().constitution,
                source_str=self.get_icon_and_name()
            )
            target.get_dueling().status_effects.append(debuff)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and " + "{1}'s Con was reduced to 0!"

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CurseOfWeakness(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD40",
            name="Curse of Weakness",
            class_key=ExpertiseClass.Alchemist,
            description="Unavoidably reduce an enemy's Int and Str to 0 for 3 turns.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            int_debuff = IntDebuff(
                turns_remaining=3,
                value=-targets[0].get_combined_attributes().intelligence,
                source_str=self.get_icon_and_name()
            )

            str_debuff = StrDebuff(
                turns_remaining=3,
                value=-targets[0].get_combined_attributes().strength,
                source_str=self.get_icon_and_name()
            )

            target.get_dueling().status_effects += [int_debuff, str_debuff]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and " + "{1}'s Int and Str were reduced to 0!"

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CurseOfLethargy(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA4",
            name="Curse of Lethargy",
            class_key=ExpertiseClass.Alchemist,
            description="Unavoidably reduce an enemy's Dex to 0 for 3 turns.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            debuff = DexDebuff(
                turns_remaining=3,
                value=-targets[0].get_combined_attributes().dexterity,
                source_str=self.get_icon_and_name()
            )
            target.get_dueling().status_effects.append(debuff)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and " + "{1}'s Dex was reduced to 0!"

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class HenOfTheCaverns(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # ?% chance of 4 player party (Lvl. 70-80) victory against 1
        # Avg Number of Turns (per entity): ?

        super().__init__("Hen of the Caverns" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(320, ExpertiseClass.Alchemist)
        self._expertise.constitution = 120
        self._expertise.strength = 0
        self._expertise.dexterity = 20
        self._expertise.intelligence = 100
        self._expertise.luck = 77
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.HenFungus))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [CurseOfFrailty(), CurseOfWeakness(), CurseOfLethargy()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Hen of the Caverns"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
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
