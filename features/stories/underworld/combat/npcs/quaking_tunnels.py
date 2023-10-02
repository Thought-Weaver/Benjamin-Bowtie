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
from features.shared.statuseffect import ConDebuff, DmgVulnerability, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Shockwave(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Shockwave",
            class_key=ExpertiseClass.Guardian,
            description="Deal 95-100 damage to all enemies and cause Faltering for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = TurnSkipChance(
            turns_remaining=2,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(95, 100), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class FallingDebris(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEA8",
            name="Falling Debris",
            class_key=ExpertiseClass.Guardian,
            description="Deal 70-75 damage to all enemies and decrease their Con by 10 for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = ConDebuff(
            turns_remaining=2,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(70, 75), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EmergingFissure(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD73",
            name="Emerging Fissure",
            class_key=ExpertiseClass.Guardian,
            description="Cause 50% damage vulnerability on all enemies for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgVulnerability(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class QuakingTunnels(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 19% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 11

        super().__init__("Quaking Tunnels" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.AFewCoins: 0.6,
            ItemKey.PileOfCoins: 0.05,
            ItemKey.CopperOre: 1,
            ItemKey.SilverOre: 0.6,
            ItemKey.GoldOre: 0.6,
            ItemKey.AmberiteOre: 0.5,
            ItemKey.OrichalcumOre: 0.3,
            ItemKey.MythrilOre: 0.1,
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
        
        self._expertise.add_xp_to_class_until_level(350, ExpertiseClass.Guardian)
        self._expertise.constitution = 180
        self._expertise.strength = 100
        self._expertise.dexterity = 0
        self._expertise.intelligence = 0
        self._expertise.luck = 67
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.Tremors))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Shockwave(), FallingDebris(), EmergingFissure()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Quaking Tunnels"
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
