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
from features.shared.statuseffect import StatsHidden
from features.stats import Stats

from features.stories.underworld.combat.npcs.agaric_alchemist import PoppingPustules
from features.stories.underworld.combat.npcs.chanterspell import HummingRegeneration
from features.stories.underworld.combat.npcs.deathless_cap import MushroomSlam
from features.stories.underworld.combat.npcs.glowing_moss import Luminesce
from features.stories.underworld.combat.npcs.hen_of_the_caverns import CurseOfFrailty
from features.stories.underworld.combat.npcs.malevolent_morel import Counterattack
from features.stories.underworld.combat.npcs.mycelium_tree import ManaBurn

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class SporeHaze(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF44",
            name="Spore Haze",
            class_key=ExpertiseClass.Alchemist,
            description="Cause all enemies' health, mana, and armor to be hidden for 3 turns.",
            flavor_text="",
            mana_cost=25,
            cooldown=7,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = StatsHidden(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
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

class MushroomMaze(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 7% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 31

        super().__init__("Mushroom Maze" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.Chanterspell: 0.6,
            ItemKey.MalevolentMorel: 0.3,
            ItemKey.HenOfTheCaverns: 0.1,
            ItemKey.DeathlessCap: 0.4,
            ItemKey.DeepAgaric: 0.7,
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
        
        self._expertise.add_xp_to_class_until_level(600, ExpertiseClass.Alchemist)
        self._expertise.constitution = 300
        self._expertise.strength = 100
        self._expertise.dexterity = 50
        self._expertise.intelligence = 100
        self._expertise.luck = 44
        self._expertise.memory = 6

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SporeCloud))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [SporeHaze(), Counterattack(), Luminesce(), MushroomSlam(), CurseOfFrailty(), PoppingPustules(), HummingRegeneration(), ManaBurn()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Mushroom Maze"
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
