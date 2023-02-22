from __future__ import annotations

from strenum import StrEnum
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise
from features.inventory import Inventory
from features.shared.item import ItemKey
from features.shared.statuseffect import NEGATIVE_STATUS_EFFECTS, POSITIVE_STATUS_EFFECTS_ON_SELF, StatusEffectKey, Taunted
from features.stats import Stats
from uuid import uuid4

from typing import Dict, List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player    

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class NPCRoles(StrEnum):
    Unknown = "Unknown"
    FortuneTeller = "FortuneTeller"
    Blacksmith = "Blacksmith"
    KnucklebonesPatron = "KnucklebonesPatron"
    Chef = "Chef"
    RandomItemMerchant = "RandomItemMerchant"
    DuelingTrainer = "DuelingTrainer"
    Companion = "Companion"
    CompanionMerchant = "CompanionMerchant"
    DungeonEnemy = "DungeonEnemy"


class NPCDuelingPersonas(StrEnum):
    Unknown = "Unknown"
    Bruiser = "Bruiser" # Str-based, aggressive, focused on healing and buffing self, focuses on tough targets
    Healer = "Healer" # Int-based, focused on keeping allies alive (unless alone, then becomes Mage)
    Mage = "Mage" # Int-based, aggressive, low con and dex, focuses on weak targets
    Rogue = "Rogue" # Dex-based, aggressive, low con, high lck, focuses on weak targets
    Specialist = "Specialist" # Utility focused, wants to debuff enemies and buff allies
    Tank = "Tank" # Con-based, focused on taunting and absorbing damage (unless alone, then becomes Brusier)

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class NPC():
    def __init__(self, name: str, role: NPCRoles, dueling_persona: NPCDuelingPersonas, dueling_rewards: Dict[ItemKey, float]):
        self._id = str(uuid4())

        self._name = name
        self._role = role
        self._dueling_persona = dueling_persona
        self._dueling_rewards = dueling_rewards

        self._inventory: Inventory = Inventory()
        self._stats: Stats = Stats()
        self._expertise: Expertise = Expertise()
        self._equipment: Equipment = Equipment()
        self._dueling: Dueling = Dueling()

    def _get_bruiser_fitness(self, org_self: NPC, enemies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Bruiser should heavily weight actions that heal itself at low health, but care less when at high health
        fitness_score += ((1 + (1 - org_self.get_expertise().hp / org_self.get_expertise().max_hp) + self_expertise.hp / self_expertise.max_hp - org_self.get_expertise().hp / org_self.get_expertise().max_hp) ** 10 - 1) / (15 ** 2 - 1)
        # The Bruiser should also focus on buffing its constitution, strength, and luck when possible
        fitness_score += (self.get_combined_attributes().constitution + self.get_combined_attributes().strength + self.get_combined_attributes().luck) / 10
        # The Bruiser should lastly consider the damage it dealt to enemies
        fitness_score += 2.5 * sum(
            (1 - 
                (enemy.get_expertise().hp + enemy.get_dueling().armor) / 
                (enemy.get_expertise().max_hp + enemy.get_equipment().get_total_reduced_armor(enemy.get_expertise().level, enemy.get_expertise().get_all_attributes() + enemy.get_equipment().get_total_attribute_mods())))
            for enemy in enemies
        ) / len(enemies)
        # The Bruiser should slightly consider the positive status effects it has active
        if len(self.get_dueling().status_effects) > 0:
            fitness_score += sum([1 if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF else 0 for se in self.get_dueling().status_effects]) / len(self.get_dueling().status_effects)
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)

        return fitness_score

    def _get_healer_fitness(self, org_self: NPC, allies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Healer should heavily weight actions that restore mana when low
        fitness_score += ((1 + (1 - org_self.get_expertise().mana / org_self.get_expertise().max_mana) + self_expertise.mana / self_expertise.max_mana - org_self.get_expertise().mana / org_self.get_expertise().max_mana) ** 10 - 1) / (18 ** 2 - 1)
        # The Healer should focus on buffing intelligence for more mana and healing power
        fitness_score += self.get_combined_attributes().intelligence / 10
        # The Healer should score the average of allies' health strongly since it wants to heal
        fitness_score += 4 * sum((ally.get_expertise().hp / ally.get_expertise().max_hp) for ally in allies) / len(allies)
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)

        return fitness_score

    def _get_mage_fitness(self, org_self: NPC, enemies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Mage should moderately weight actions that heal itself at low health, but care less when at high health
        fitness_score += ((1 + (1 - org_self.get_expertise().hp / org_self.get_expertise().max_hp) + self_expertise.hp / self_expertise.max_hp - org_self.get_expertise().hp / org_self.get_expertise().max_hp) ** 10 - 1) / (25 ** 2 - 1)
        # The Mage should heavily weight actions that restore mana when low
        fitness_score += ((1 + (1 - org_self.get_expertise().mana / org_self.get_expertise().max_mana) + self_expertise.mana / self_expertise.max_mana - org_self.get_expertise().mana / org_self.get_expertise().max_mana) ** 10 - 1) / (18 ** 2 - 1)
        # The Mage should focus on buffing intelligence for more mana and damage and luck for crit chance
        fitness_score += (self.get_combined_attributes().intelligence + self.get_combined_attributes().luck) / 10
        # The Mage should strongly consider the damage it dealt to enemies
        fitness_score += 2.5 * sum(
            (1 - 
                (enemy.get_expertise().hp + enemy.get_dueling().armor) / 
                (enemy.get_expertise().max_hp + enemy.get_equipment().get_total_reduced_armor(enemy.get_expertise().level, enemy.get_expertise().get_all_attributes() + enemy.get_equipment().get_total_attribute_mods())))
            for enemy in enemies
        ) / len(enemies)
        # The Mage should slightly consider the positive status effects it has active
        if len(self.get_dueling().status_effects) > 0:
            fitness_score += sum([1 if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF else 0 for se in self.get_dueling().status_effects]) / len(self.get_dueling().status_effects)
        # Consider the average negative status effects on enemies to account for any new ones that might have been applied
        fitness_score += sum(
            sum([1 if se.key in NEGATIVE_STATUS_EFFECTS else 0 for se in enemy.get_dueling().status_effects]) / len(enemy.get_dueling().status_effects) if len(enemy.get_dueling().status_effects) > 0 else 0
            for enemy in enemies
        ) / len(enemies)
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)

        return fitness_score

    def _get_rogue_fitness(self, org_self: NPC, enemies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Rogue should heavily weight actions that heal itself at low health, but care less when at high health
        fitness_score += 2.5 ** (1 + (1 - org_self.get_expertise().hp / org_self.get_expertise().max_hp) + self_expertise.hp / self_expertise.max_hp - org_self.get_expertise().hp / org_self.get_expertise().max_hp) - 2.5
        # The Rogue should focus on buffing luck for better crit chance and Dex for damage and dodge chance
        fitness_score += (self.get_combined_attributes().luck + self.get_combined_attributes().dexterity) / 10
        # The Rogue should strongly consider the damage it dealt to enemies
        fitness_score += 3 * sum(
            (1 - 
                (enemy.get_expertise().hp + enemy.get_dueling().armor) / 
                (enemy.get_expertise().max_hp + enemy.get_equipment().get_total_reduced_armor(enemy.get_expertise().level, enemy.get_expertise().get_all_attributes() + enemy.get_equipment().get_total_attribute_mods())))
            for enemy in enemies
        ) / len(enemies)
        # The Rogue should slightly consider the positive status effects it has active
        if len(self.get_dueling().status_effects) > 0:
            fitness_score += sum([1 if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF else 0 for se in self.get_dueling().status_effects]) / len(self.get_dueling().status_effects)
        # Consider the average negative status effects on enemies to account for any new ones that might have been applied
        fitness_score += sum(
            sum([1 if se.key in NEGATIVE_STATUS_EFFECTS else 0 for se in enemy.get_dueling().status_effects]) / len(enemy.get_dueling().status_effects) if len(enemy.get_dueling().status_effects) > 0 else 0
            for enemy in enemies
        ) / len(enemies)
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)

        return fitness_score

    def _get_specialist_fitness(self, org_self: NPC, allies: List[Player | NPC], enemies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Specialist should moderately weight actions that heal itself at low health, but care less when at high health
        fitness_score += ((1 + (1 - org_self.get_expertise().hp / org_self.get_expertise().max_hp) + self_expertise.hp / self_expertise.max_hp - org_self.get_expertise().hp / org_self.get_expertise().max_hp) ** 10 - 1) / (25 ** 2 - 1)
        # The Specialist should heavily weight actions that increase non-memory stats for allies
        fitness_score += sum([
            (ally.get_combined_attributes().constitution + ally.get_combined_attributes().dexterity +
            ally.get_combined_attributes().intelligence + ally.get_combined_attributes().luck +
            ally.get_combined_attributes().strength) / 50
            for ally in allies
        ])
        # The Specialist should also consider how effective the action was at decreasing stats for enemies
        averaged_enemy_attrs = sum([
            (enemy.get_combined_attributes().constitution + enemy.get_combined_attributes().dexterity +
            enemy.get_combined_attributes().intelligence + enemy.get_combined_attributes().luck +
            enemy.get_combined_attributes().strength) / 50
            for enemy in enemies
        ])
        fitness_score += 2 ** (2 - averaged_enemy_attrs) / (2 + averaged_enemy_attrs)
        # The Specialist should simply look at the average count of status effects
        fitness_score += sum([len(ally.get_dueling().status_effects) for ally in allies]) / len(allies)
        fitness_score += sum([len(enemy.get_dueling().status_effects) for enemy in enemies]) / len(enemies)
        # The Specialist should slightly consider the damage it dealt to enemies
        fitness_score += sum(
            (1 - 
                (enemy.get_expertise().hp + enemy.get_dueling().armor) / 
                (enemy.get_expertise().max_hp + enemy.get_equipment().get_total_reduced_armor(enemy.get_expertise().level, enemy.get_expertise().get_all_attributes() + enemy.get_equipment().get_total_attribute_mods())))
            for enemy in enemies
        ) / len(enemies)
        # The Specialist should heavily weight actions that restore mana when low
        fitness_score += ((1 + (1 - org_self.get_expertise().mana / org_self.get_expertise().max_mana) + self_expertise.mana / self_expertise.max_mana - org_self.get_expertise().mana / org_self.get_expertise().max_mana) ** 10 - 1) / (18 ** 2 - 1)
        # Consider the average negative status effects on enemies to account for any new ones that might have been applied
        fitness_score += sum(
            sum([1 if se.key in NEGATIVE_STATUS_EFFECTS else 0 for se in enemy.get_dueling().status_effects]) / len(enemy.get_dueling().status_effects) if len(enemy.get_dueling().status_effects) > 0 else 0
            for enemy in enemies
        ) / len(enemies)
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)

        return fitness_score

    def _get_tank_fitness(self, org_self: NPC, allies: List[Player | NPC], enemies: List[Player | NPC]):
        self_expertise = self.get_expertise()

        fitness_score: float = 0
        # The Tank should focus on buffing constitution for more health
        fitness_score += self.get_combined_attributes().constitution / 10
        # The Tank should score the average of allies' health strongly since it wants to protect, excluding its own
        fitness_score += (sum(
                (ally.get_expertise().hp + ally.get_dueling().armor) / (ally.get_expertise().max_hp + ally.get_equipment().get_total_reduced_armor(ally.get_expertise().level, ally.get_expertise().get_all_attributes() + ally.get_equipment().get_total_attribute_mods()))
            for ally in allies) - 
            (self_expertise.hp + self.get_dueling().armor) / (self_expertise.max_hp + self.get_equipment().get_total_reduced_armor(self_expertise.level, self_expertise.get_all_attributes() + self.get_equipment().get_total_attribute_mods()))) / (len(allies) - 1)
        # The Tank should add a fixed value for the number of Taunts it's causing
        for enemy in enemies:
            for se in enemy.get_dueling().status_effects:
                if se.key == StatusEffectKey.Taunted:
                    assert(isinstance(se, Taunted))
                    if se.forced_to_attack == self:
                        fitness_score += 1
        # Any action that gives an NPC additional actions should be weighted very heavily
        fitness_score += 4 * max(self.get_dueling().actions_remaining - org_self.get_dueling().actions_remaining, 0)
        
        return fitness_score

    def get_fitness_for_persona(self, org_self: NPC, allies: List[Player | NPC], enemies: List[Player | NPC]):
        num_allies_alive = sum([(1 if ally.get_expertise().hp > 0 else 0) for ally in allies])

        if self._dueling_persona == NPCDuelingPersonas.Bruiser or (self._dueling_persona == NPCDuelingPersonas.Tank and num_allies_alive <= 1):
            return self._get_bruiser_fitness(org_self, enemies)
        elif self._dueling_persona == NPCDuelingPersonas.Healer and len(allies) > 1:
            return self._get_healer_fitness(org_self, allies)
        elif self._dueling_persona == NPCDuelingPersonas.Mage or (self._dueling_persona == NPCDuelingPersonas.Healer and len(allies) <= 1):
            return self._get_mage_fitness(org_self, enemies)
        elif self._dueling_persona == NPCDuelingPersonas.Rogue:
            return self._get_rogue_fitness(org_self, enemies)
        elif self._dueling_persona == NPCDuelingPersonas.Specialist:
            return self._get_specialist_fitness(org_self, allies, enemies)
        elif self._dueling_persona == NPCDuelingPersonas.Tank:
            return self._get_tank_fitness(org_self, allies, enemies)
        return 0

    def get_id(self):
        return self._id

    def set_id(self, id: str):
        self._id = id

    def get_combined_attributes(self):
        return self._expertise.get_all_attributes() + self._equipment.get_total_attribute_mods() + self._dueling.get_combined_attribute_mods()

    def get_name(self):
        return self._name

    def get_inventory(self):
        return self._inventory

    def get_expertise(self):
        return self._expertise

    def get_equipment(self):
        return self._equipment

    def get_dueling(self):
        return self._dueling

    def get_stats(self):
        return self._stats

    def get_dueling_rewards(self):
        return self._dueling_rewards

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", "")
        self._name = state.get("_name", "")
        self._role = state.get("_role", NPCRoles.Unknown)
        self._inventory = state.get("_inventory", Inventory())
        self._expertise = state.get("_expertise", Expertise())
        self._equipment = state.get("_equipment", Equipment())
        self._dueling = state.get("_dueling", Dueling())
        self._stats = state.get("_stats", Stats())
