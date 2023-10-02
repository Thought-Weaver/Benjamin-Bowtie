from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import POISONED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Charmed, DexDebuff, Poisoned
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SporeSpread(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Spore Spread",
            class_key=ExpertiseClass.Alchemist,
            description="Release spores into the air that have a 100% chance to Poison all enemies for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [poisoned])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class FungalControl(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC9E",
            name="Fungal Control",
            class_key=ExpertiseClass.Alchemist,
            description="Charm an enemy for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        charm = Charmed(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [charm])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MushroomsEmbrace(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF44",
            name="Mushroom's Embrace",
            class_key=ExpertiseClass.Alchemist,
            description="Grasp an enemy in your fungal tendrils, dealing 10-18 damage and decreasing their Dexterity by 5 for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:        
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        debuff = DexDebuff(
            turns_remaining=5,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(15, 18), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class FuriousMushroom(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Furious Mushroom" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.BlazeCluster: 0.8,
            ItemKey.FoolsDelight: 1,
            ItemKey.Bloodcrown: 0.9,
            ItemKey.SpeckledCap: 1,
            ItemKey.Slumbershroom: 0.8,
            ItemKey.SlumbershroomSpores: 1,
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
        
        self._expertise.add_xp_to_class_until_level(60, ExpertiseClass.Alchemist)
        self._expertise.constitution = 30
        self._expertise.strength = 7
        self._expertise.dexterity = 0
        self._expertise.intelligence = 20
        self._expertise.luck = 0
        self._expertise.memory = 3

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
        
        self._dueling.abilities = [SporeSpread(), MushroomsEmbrace(), FungalControl()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Furious Mushroom"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.BlazeCluster: 0.8,
            ItemKey.BlazeCluster: 0.5,
            ItemKey.FoolsDelight: 1,
            ItemKey.FoolsDelight: 0.6,
            ItemKey.Bloodcrown: 1,
            ItemKey.Bloodcrown: 0.9,
            ItemKey.Bloodcrown: 0.7,
            ItemKey.Bloodcrown: 0.5,
            ItemKey.SpeckledCap: 1,
            ItemKey.SpeckledCap: 0.9,
            ItemKey.SpeckledCap: 0.8,
            ItemKey.SpeckledCap: 0.7,
            ItemKey.Slumbershroom: 0.8,
            ItemKey.Slumbershroom: 0.5,
            ItemKey.Slumbershroom: 0.2,
            ItemKey.SlumbershroomSpores: 1,
            ItemKey.SlumbershroomSpores: 0.8,
            ItemKey.SlumbershroomSpores: 0.6
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
