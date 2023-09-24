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
from features.shared.statuseffect import AttackingChanceToApplyStatus, Poisoned, StatusEffectKey
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult
    from features.shared.statuseffect import StatusEffect

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class BlackBile(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDA4",
            name="Black Bile",
            class_key=ExpertiseClass.Alchemist,
            description="Spew a corrosive bile on everyone, causing 10 stacks of Poisoned for 8 turns.",
            flavor_text="",
            mana_cost=25,
            cooldown=0,
            num_targets=-2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuffs: List[StatusEffect] = [Poisoned(
            turns_remaining=8,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        ) for _ in range(10)]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, debuffs)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ToxinBurst(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Toxin Burst",
            class_key=ExpertiseClass.Alchemist,
            description="Consume all Poisoned stacks on an enemy, dealing 50x the amount of time remaining as damage.",
            flavor_text="",
            mana_cost=20,
            cooldown=0,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = 50 * sum(se.turns_remaining for se in targets[0].get_dueling().status_effects if se.key == StatusEffectKey.Poisoned)
        targets[0].get_dueling().status_effects = [se for se in targets[0].get_dueling().status_effects if se.key != StatusEffectKey.Poisoned]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, exploding all stacks of Poisoned on " + "{1}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VenomousClaws(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8E",
            name="Venomous Claws",
            class_key=ExpertiseClass.Alchemist,
            description="Envenom your claws, allowing them to cause Poisoned 6 times for 10 turns each when attacking. Lasts 5 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buffs: List[StatusEffect] = [AttackingChanceToApplyStatus(
            turns_remaining=5,
            value=1,
            status_effect=Poisoned(
                turns_remaining=10,
                value=POISONED_PERCENT_HP,
                source_str=self.get_icon_and_name()
            ),
            source_str=self.get_icon_and_name()
        ) for _ in range(6)]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, buffs)
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class BlindSalamander(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 42% chance of 4 player party (Lvl. 70-80) victory against 1
        # Avg Number of Turns (per entity): 15

        super().__init__("Blind Salamander" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.SalamanderVenom: 0.4,
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
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Alchemist)
        self._expertise.constitution = 150
        self._expertise.strength = 0
        self._expertise.dexterity = 67
        self._expertise.intelligence = 80
        self._expertise.luck = 0
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.SalamanderClaws))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.SalamanderForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [BlackBile(), ToxinBurst(), VenomousClaws()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Blind Salamander"
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
