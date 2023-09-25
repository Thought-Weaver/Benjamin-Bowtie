from __future__ import annotations

from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Attribute, Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability, NegativeAbilityResult
from features.shared.constants import BLEED_PERCENT_HP
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey
from features.shared.statuseffect import POSITIVE_STATUS_EFFECTS_ON_SELF, Bleeding, CannotAttack, CannotUseAbilities, ConBuff, DexBuff, StrBuff
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Rewind(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23EA",
            name="Rewind",
            class_key=ExpertiseClass.Fisher,
            description="Remove all positive status effects from an enemy.",
            flavor_text="",
            mana_cost=40,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            target.get_dueling().status_effects = [se for se in target.get_dueling().status_effects if se.key not in POSITIVE_STATUS_EFFECTS_ON_SELF]

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and removed all of " + "{1}'s positive status effects!\n\n"

        self.remove_mana_and_set_cd(caster)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ArcaneChains(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD17",
            name="Arcane Chains",
            class_key=ExpertiseClass.Fisher,
            description="Deal 120-130 damage to an enemy and cause them to be Atrophied and Enfeebled for 3 turns.",
            flavor_text="",
            mana_cost=60,
            cooldown=5,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        atrophied = CannotAttack(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        enfeebled = CannotUseAbilities(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(120, 130), [atrophied, enfeebled])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TemporalSeal(Ability):
    def __init__(self):
        super().__init__(
            icon="\u231B",
            name="Temporal Seal",
            class_key=ExpertiseClass.Fisher,
            description="Set all of an enemy's cooldowns to 6 turns remaining and restore 20% of your mana.",
            flavor_text="",
            mana_cost=50,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        for target in targets:
            for ability in target.get_dueling().abilities:
                ability._cur_cooldown = 6

        mana_to_restore: int = int(0.2 * caster.get_expertise().max_mana)
        caster.get_expertise().restore_mana(mana_to_restore)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}, setting all of " + "{1}'s cooldowns to 6 turns remaining.\n\n{0} restored " + f"{mana_to_restore} mana.\n\n"

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

class EchoOfPasserhawk(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # ?% chance of 4 player party (Lvl. 80-90) victory against 1 + Yenna + Asterius
        # Avg Number of Turns (per entity): ?

        super().__init__("Echo of Passerhawk" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Mage, {
            ItemKey.RelicOfTheEyelessWanderer: 0.01,
            ItemKey.CloakOfTheEyelessWanderer: 0.01
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
        
        self._expertise.add_xp_to_class_until_level(300, ExpertiseClass.Fisher)
        self._expertise.constitution = 100
        self._expertise.strength = 0
        self._expertise.dexterity = 60
        self._expertise.intelligence = 100
        self._expertise.luck = 37
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.RelicOfTheEyelessWanderer))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.CloakOfTheEyelessWanderer))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Rewind(), ArcaneChains(), TemporalSeal()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Echo of Passerhawk"
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
