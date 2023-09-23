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

class TemporalTear(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0C",
            name="Temporal Tear",
            class_key=ExpertiseClass.Fisher,
            description="Deal damage to an enemy equal to 50x the time remaining on their CDs.",
            flavor_text="",
            mana_cost=50,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = 50 * sum(ability.get_cur_cooldown() for ability in targets[0].get_dueling().abilities)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, dealing damage proportional to the time remaining on " + "{1}'s cooldowns!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Impedance(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Impedance",
            class_key=ExpertiseClass.Fisher,
            description="Set all enemies' abilities on cooldown.",
            flavor_text="",
            mana_cost=30,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            for ability in target.get_dueling().abilities:
                ability._cur_cooldown = max(ability._cooldown, 0)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}! All of your abilities have been set on cooldown.\n\n"
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += mana_and_cd_str

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Hastening(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD52",
            name="Hastening",
            class_key=ExpertiseClass.Fisher,
            description="Reset all of your cooldowns and restore 100% of your mana.",
            flavor_text="",
            mana_cost=40,
            cooldown=3,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for ability in caster.get_dueling().abilities:
            if ability._cur_cooldown != -1:
                ability._cur_cooldown = 0

        caster.get_expertise().restore_mana(caster.get_expertise().max_mana)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, reset its cooldowns, and restored its mana!\n\n"

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class WarpingAnomaly(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 37% chance of 4 player party (Lvl. 80-90) victory against 1
        # Avg Number of Turns (per entity): 11

        super().__init__("Warping Anomaly" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(360, ExpertiseClass.Guardian)
        self._expertise.constitution = 120
        self._expertise.strength = 0
        self._expertise.dexterity = 80
        self._expertise.intelligence = 100
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.RendingDistortion))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [TemporalTear(), Impedance(), Hastening()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Warping Anomaly"
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
