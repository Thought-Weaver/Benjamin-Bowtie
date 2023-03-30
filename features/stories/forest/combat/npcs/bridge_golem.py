from __future__ import annotations

import random

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import RegenerateArmor, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class StoneSwarm(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA8",
            name="Stone Swarm",
            class_key=ExpertiseClass.Guardian,
            description="Summon a barrage of stones, dealing 30-40 to up to 3 enemies.",
            flavor_text="",
            mana_cost=20,
            cooldown=3,
            num_targets=3,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(30, 40))
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EruptingEarth(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0B",
            name="Erupting Earth",
            class_key=ExpertiseClass.Guardian,
            description="Deal 15-20 damage and cause Faltering with a 30% chance for 3 turns.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=-1,
            level_requirement=0,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength, Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=3,
            value=0.3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(15, 20), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Reform(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Reform",
            class_key=ExpertiseClass.Guardian,
            description="Regenerate 5% of your max armor every turn for 5 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=10,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = RegenerateArmor(
            turns_remaining=5,
            value=0.05,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
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

# Idea: Since the reward system doesn't support "a random rare item" well, perhaps
# I could link to a post-boss treasure room before moving to the next section?
class BridgeGolem(NPC):
    def __init__(self, name_suffix: str=""):
        artifact_reward = random.choice([ItemKey.GolemsEye, ItemKey.GolemicAssembly])
        super().__init__("Bridge Golem" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {    
            ItemKey.BagOfCoins: 0.9,
            ItemKey.BagOfCoins: 0.6,
            artifact_reward: 0.3,
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
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Guardian)
        self._expertise.constitution = 80
        self._expertise.strength = 30
        self._expertise.dexterity = 0
        self._expertise.intelligence = 70
        self._expertise.luck = 16
        self._expertise.memory = 4

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.GolemicFists))

        self._equipment.equip_item_to_slot(ClassTag.Equipment.Helmet, LOADED_ITEMS.get_new_item(ItemKey.OrichalcumPlateHelmet))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Gloves, LOADED_ITEMS.get_new_item(ItemKey.OrichalcumPlateGauntlets))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.GolemicHeart))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Leggings, LOADED_ITEMS.get_new_item(ItemKey.OrichalcumPlateLeggings))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.Boots, LOADED_ITEMS.get_new_item(ItemKey.OrichalcumPlateGreaves))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
            self._dueling.is_legendary = True

        self._dueling.abilities = [StoneSwarm(), EruptingEarth(), Reform()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Bridge Golem"
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
