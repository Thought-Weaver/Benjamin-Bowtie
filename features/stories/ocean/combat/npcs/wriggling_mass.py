from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.player import Player
from features.shared.ability import Ability
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import DmgVulnerability, StatusEffectKey
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class FlailingTentacles(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC19",
            name="Flailing Tentacles",
            class_key=ExpertiseClass.Fisher,
            description="Deal 65-70 damage to all enemies and remove their attribute buffs.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(65, 70))

        attr_buffs = [StatusEffectKey.ConBuff, StatusEffectKey.StrBuff, StatusEffectKey.DexBuff, StatusEffectKey.IntBuff, StatusEffectKey.LckBuff]
        for i, result in enumerate(results):
            if not result.dodged:
                targets[i].get_dueling().status_effects = list(filter(lambda se: se.key in attr_buffs, targets[i].get_dueling().status_effects))
                results[i].target_str += " and had their attribute buffs removed"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnceasingGaze(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC41\uFE0F",
            name="Unceasing Gaze",
            class_key=ExpertiseClass.Fisher,
            description="Cause an enemy to gain a stack of Corruption.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        
        for i, target in enumerate(targets):
            if isinstance(target, Player):
                target.get_dungeon_run().corruption += 1
                result_str += "{" + f"{i}" + "}" + " gained a stack of Corruption"

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PsychicScream(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDE0",
            name="Psychic Scream",
            class_key=ExpertiseClass.Fisher,
            description="Cause all enemies to take 75% more damage for 3 turns.",
            flavor_text="",
            mana_cost=20,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = DmgVulnerability(
            turns_remaining=3,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
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

class WrigglingMass(NPC):
    def __init__(self, name_suffix: str=""):
        super().__init__("Wriggling Mass" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Fisher)
        self._expertise.constitution = 160
        self._expertise.strength = 0
        self._expertise.dexterity = 20
        self._expertise.intelligence = 60
        self._expertise.luck = 57
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.WrigglingTentacles))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [FlailingTentacles(), UnceasingGaze(), PsychicScream()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Wriggling Mass"
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
