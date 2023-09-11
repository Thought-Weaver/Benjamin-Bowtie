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
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class BloodToGold(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Blood to Gold",
            class_key=ExpertiseClass.Merchant,
            description="Deal 20% of your remaining HP as damage to all enemies.",
            flavor_text="",
            mana_cost=50,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = int(0.2 * caster.get_expertise().hp)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage proportional to their remaining health!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhispersOfAvarice(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC51",
            name="Whispers of Avarice",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage to an enemy equal to 25% of their current gold (up to 600 base damage).",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = min(int(0.25 * targets[0].get_inventory().get_coins()), 600)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage proportional to their current gold!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Sacrifice(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26B0\uFE0F",
            name="Sacrifice",
            class_key=ExpertiseClass.Merchant,
            description="Steal 40% of an enemy's max health.",
            flavor_text="",
            mana_cost=30,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        damage = int(0.4 * targets[0].get_expertise().max_hp)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        heal_results: List[str] = self._use_heal_ability(caster, [caster], range(damage, damage))

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        result_str += "\n"
        result_str += "\n".join([s.replace("{1}", "{0}") for s in heal_results])

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class ScratchesOnTheWall(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 46% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 9

        super().__init__("Scratches on the Wall" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(350, ExpertiseClass.Merchant)
        self._expertise.constitution = 100
        self._expertise.strength = 0
        self._expertise.dexterity = 50
        self._expertise.intelligence = 150
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.TerrifyingPresence))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [BloodToGold(), WhispersOfAvarice(), Sacrifice()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Scratches on the Wall"
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
