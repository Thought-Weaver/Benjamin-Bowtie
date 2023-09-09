from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import BLEED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import Bleeding, DmgReduction, StackingDamage
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class RazorCharge(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Razor Charge",
            class_key=ExpertiseClass.Guardian,
            description="Charge with your claws ahead of you, dealing 125-135 damage and causing Bleeding for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = Bleeding(
            turns_remaining=4,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(125, 135), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RepeatedStrikes(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Repeated Strikes",
            class_key=ExpertiseClass.Guardian,
            description="An enemy quakes with the strength of your blows, duplicating the first Reverberating status caused by your weapon.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for se in targets[0].get_dueling().status_effects:
            main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
            source_str = main_hand_item.get_full_name() if main_hand_item is not None else "None Equipped"
            if isinstance(se, StackingDamage) and se.source_str == source_str and se.caster == caster:
                new_se = StackingDamage(
                    turns_remaining=se.turns_remaining,
                    value=se.value,
                    caster=caster,
                    source_str=se.source_str
                )
                targets[0].get_dueling().status_effects.append(new_se)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and duplicated the first Reverberating status caused by its claws on " + "{1}!"

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ArmoredHide(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Armored Hide",
            class_key=ExpertiseClass.Guardian,
            description="Gain 100% Protected for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=7,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReduction(
            turns_remaining=3,
            value=1,
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

class Tunneldigger(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 13% chance of 4 player party (Lvl. 70-80) victory against 1
        # Avg Number of Turns (per entity): 22

        super().__init__("Tunneldigger" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(600, ExpertiseClass.Guardian)
        self._expertise.constitution = 200
        self._expertise.strength = 300
        self._expertise.dexterity = 50
        self._expertise.intelligence = 0
        self._expertise.luck = 47
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.TunneldiggerClaws))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.TunneldiggerForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [RazorCharge(), ArmoredHide(), RepeatedStrikes()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Tunneldigger"
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
