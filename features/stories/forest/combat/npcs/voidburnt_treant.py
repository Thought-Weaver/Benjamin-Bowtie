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
from features.shared.statuseffect import FixedDmgTick
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class BurningGrasp(Ability):
    def __init__(self):
        super().__init__(
            icon="\u270A",
            name="Burning Grasp",
            class_key=ExpertiseClass.Guardian,
            description="Deal 30-35 damage and cause 10 damage to tick every turn for 4 turns on an enemy.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        fixed_dmg_tick = FixedDmgTick(
            turns_remaining=4,
            value=10,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(30, 35), [fixed_dmg_tick])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BellowVoidflame(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD25",
            name="Bellow Voidflame",
            class_key=ExpertiseClass.Guardian,
            description="Deal 20-25 damage and cause 5 damage to tick every turn for 2 turns on all enemies.",
            flavor_text="",
            mana_cost=35,
            cooldown=5,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        fixed_dmg_tick = FixedDmgTick(
            turns_remaining=2,
            value=5,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(20, 25), [fixed_dmg_tick])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Combust(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Combust",
            class_key=ExpertiseClass.Guardian,
            description="Deal 40-50 damage to everyone, including yourself.",
            flavor_text="",
            mana_cost=10,
            cooldown=8,
            num_targets=-2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(40, 50))
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

class VoidburntTreant(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 28% chance of 4 player party (Lvl. 20-30) victory against 1

        super().__init__("Voidburnt Treant" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.Wrathbark: 0.9,
            ItemKey.Wrathbark: 0.8,
            ItemKey.Wrathbark: 0.7,
            ItemKey.TreantCuttings: 0.5,
            ItemKey.CharredUndeadWood: 0.75
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
        
        self._expertise.add_xp_to_class_until_level(160, ExpertiseClass.Guardian)
        self._expertise.constitution = 60
        self._expertise.strength = 27
        self._expertise.dexterity = 0
        self._expertise.intelligence = 60
        self._expertise.luck = 10
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.TreantClaws))

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.WrathbarkHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.WrathbarkGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.WrathbarkCuirass))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.WrathbarkLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.WrathbarkGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [BurningGrasp(), BellowVoidflame(), Combust()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Voidburnt Treant"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.Wrathbark: 0.9,
            ItemKey.Wrathbark: 0.8,
            ItemKey.Wrathbark: 0.7,
            ItemKey.TreantCuttings: 0.5,
            ItemKey.CharredUndeadWood: 0.75
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
