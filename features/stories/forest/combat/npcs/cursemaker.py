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
from features.shared.statuseffect import CannotAttack, CannotUseAbilities, ConDebuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class CurseOfTheForest(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF32",
            name="Curse of the Forest",
            class_key=ExpertiseClass.Fisher,
            description="Decrease all enemies' Constitution by 3 for the rest of the duel.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=-1,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Entangle(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF3F",
            name="Entangle",
            class_key=ExpertiseClass.Fisher,
            description="Cause up to 2 enemies to become Atrophied for 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = CannotAttack(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HollowStare(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC41\uFE0F",
            name="Hollow Stare",
            class_key=ExpertiseClass.Fisher,
            description="Cause up to 2 enemies to become Enfeebled for 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=2,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = CannotUseAbilities(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
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

class Cursemaker(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Cursemaker" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.Wrathbark: 0.9,
            ItemKey.MagesBaneSeed: 0.9,
            ItemKey.DoomCharm: 0.1
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
        
        self._expertise.add_xp_to_class_until_level(160, ExpertiseClass.Fisher)
        self._expertise.constitution = 60
        self._expertise.strength = 0
        self._expertise.dexterity = 20
        self._expertise.intelligence = 50
        self._expertise.luck = 27
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

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [CurseOfTheForest(), Entangle(), HollowStare()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Lithe Treant"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Mage
        self._dueling_rewards = {
            ItemKey.Wrathbark: 0.9,
            ItemKey.Wrathbark: 0.6,
            ItemKey.Lithewood: 0.9,
            ItemKey.Lithewood: 0.6,
            ItemKey.MagesBaneSeed: 0.9,
            ItemKey.MagesBaneSeed: 0.7,
            ItemKey.MagesBaneSeed: 0.5,
            ItemKey.TreantCuttings: 0.5,
            ItemKey.DoomCharm: 0.1
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
