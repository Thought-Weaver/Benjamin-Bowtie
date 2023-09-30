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
from features.shared.statuseffect import BonusDamageOnAttack, ConDebuff, Decaying, DexDebuff, DmgReduction, FixedDmgTick, IntDebuff, LckDebuff, StrDebuff, TurnSkipChance
from features.stats import Stats

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class PathsUpended(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDFDE",
            name="Paths Upended",
            class_key=ExpertiseClass.Fisher,
            description="Deal 60-65 damage to all enemies and cause Faltering for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        debuff = TurnSkipChance(
            turns_remaining=1,
            value=1,
            source_str=self.get_icon_and_name()
        )
        
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(60, 65), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class NoEscape(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26D3\uFE0F",
            name="No Escape",
            class_key=ExpertiseClass.Fisher,
            description="Decrease all enemies' stats by 5 for the rest of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        int_debuff = IntDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        lck_debuff = LckDebuff(
            turns_remaining=-1,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff, int_debuff, lck_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ConsumingTavern(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF7B",
            name="Consuming Tavern",
            class_key=ExpertiseClass.Fisher,
            description="Cause a 75 damage tick on an enemy for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        debuff = FixedDmgTick(
            turns_remaining=3,
            value=75,
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


class TentOfEyes(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26FA",
            name="Tent of Eyes",
            class_key=ExpertiseClass.Fisher,
            description="Deal 25 damage to an enemy for each stack of Corruption on them (min. 25 damage). Cause 50% Decaying on them for 3 turns.",
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
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        debuff = Decaying(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )
        
        damage = 25
        target = targets[0]
        if isinstance(target, Player):
            damage += 25 * target.get_dungeon_run().corruption
        
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(80, 90), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class MeltingSmithy(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2692\uFE0F",
            name="Melting Smithy",
            class_key=ExpertiseClass.Fisher,
            description="Your next attack deals 150 additional damage and gain 20% Protected for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = BonusDamageOnAttack(
            turns_remaining=-1,
            value=150,
            source_str=self.get_icon_and_name()
        )

        protect_buff = DmgReduction(
            turns_remaining=1,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff, protect_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class FalseVillage(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 1% chance of 4 player party (Lvl. 60-70) victory against 1
        # Avg Number of Turns (per entity): 10

        super().__init__("False Village" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {
            ItemKey.WavecallersConch: 0.01,
            ItemKey.TomeOfForbiddenKnowledge: 0.01,
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
        
        self._expertise.add_xp_to_class_until_level(800, ExpertiseClass.Guardian)
        self._expertise.constitution = 350
        self._expertise.strength = 150
        self._expertise.dexterity = 0
        self._expertise.intelligence = 200
        self._expertise.luck = 95
        self._expertise.memory = 5

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.VillageDebris))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.FalseVillageForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
            self._dueling.is_legendary = True
        
        self._dueling.abilities = [PathsUpended(), NoEscape(), ConsumingTavern(), TentOfEyes(), MeltingSmithy()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "False Village"
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
