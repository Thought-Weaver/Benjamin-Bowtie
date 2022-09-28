from __future__ import annotations

from math import ceil
from random import choice, random

import discord

from dataclasses import dataclass
from discord.embeds import Embed
from discord.ext import commands
from features.expertise import DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, STR_DMG_SCALE, Attributes, Expertise, ExpertiseClass
from features.shared.item import Buffs, ClassTag, WeaponStats
from features.shared.statuseffect import StatusEffectKey
from strenum import StrEnum

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import Ability
    from features.shared.item import Item
    from features.shared.statuseffect import StatusEffect

# -----------------------------------------------------------------------------
# DUELING CLASS
# -----------------------------------------------------------------------------

class Dueling():
    def __init__(self):
        # All abilities unlocked and purchased
        self.available_abilities: List[Ability] = []
        # Abilities that the player has equipped and can be used
        self.abilities: List[Ability] = []

        # Temporary variables maintained for duels
        # They're stored here to make it easier to check if a Player/NPC
        # is currently in a duel
        self.is_in_combat: bool = False
        self.status_effects: List[StatusEffect] = []
        # Some enemies might start with more than 1 by default
        self.init_actions_remaining: int = 1
        # Storing here because abilities will affect them and access is
        # easier this way
        self.actions_remaining: int = 1

    # TODO: Implement an abstract method for automatically taking a turn
    # which NPCs will implement.

    @staticmethod
    def format_armor_dmg_reduct_str(damage: int, actual_damage_dealt: int):
        # Could deal more damage due to weaknesses or less due to armor and resistances
        # This is here since it's only really used during Dueling
        if damage == actual_damage_dealt:
            return ""
        
        damage_reduction_str = "+" if actual_damage_dealt > damage else ""
        damage_reduction_str = f" ({damage_reduction_str}{-(damage - actual_damage_dealt)})" if damage != actual_damage_dealt else ""
        return damage_reduction_str

    def get_total_percent_dmg_reduct(self):
        total_percent_reduction = 0
        for status_effect in self.status_effects:
            if status_effect.key == StatusEffectKey.DmgReduction:
                total_percent_reduction = min(0.75, total_percent_reduction + status_effect.value)
            if status_effect.key == StatusEffectKey.DmgVulnerability:
                total_percent_reduction = max(-0.25, total_percent_reduction + status_effect.value)
        return total_percent_reduction

    def reset_ability_cds(self):
        for ability in self.abilities:
            ability.reset_cd()

    def decrement_all_ability_cds(self):
        for ability in self.abilities:
            ability.decrement_cd()

    def decrement_statuses_time_remaining(self):
        remaining_effects = []
        for status_effect in self.status_effects:
            status_effect.decrement_turns_remaining()
            if status_effect.turns_remaining > 0 or status_effect.turns_remaining == -1:
                remaining_effects.append(status_effect)
        self.status_effects = remaining_effects

    def ability_exists(self, ability: Ability):
        for i, dueling_ability in enumerate(self.abilities):
            if dueling_ability == ability:
                return i
        return -1

    def get_combined_attribute_mods(self) -> Buffs:
        result = Buffs()
        for status_effect in self.status_effects:
            if status_effect.key == StatusEffectKey.ConBuff or status_effect.key == StatusEffectKey.ConDebuff:
                result.con_buff += status_effect.value
            if status_effect.key == StatusEffectKey.StrBuff or status_effect.key == StatusEffectKey.StrDebuff:
                result.str_buff += status_effect.value
            if status_effect.key == StatusEffectKey.DexBuff or status_effect.key == StatusEffectKey.DexDebuff:
                result.dex_buff += status_effect.value
            if status_effect.key == StatusEffectKey.IntBuff or status_effect.key == StatusEffectKey.IntDebuff:
                result.int_buff += status_effect.value
            if status_effect.key == StatusEffectKey.LckBuff or status_effect.key == StatusEffectKey.LckDebuff:
                result.lck_buff += status_effect.value
        return result

    def get_statuses_string(self) -> str:
        return "*Status Effects:*\n\n" + "\n".join([str(se) for se in self.status_effects])

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.available_abilities = state.get("available_abilities", [])
        self.abilities = state.get("abilities", [])

        self.is_in_combat = False
        self.status_effects = []
        self.init_actions_remaining = 1
        self.actions_remaining = 1

# -----------------------------------------------------------------------------
# DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

from features.npcs.npc import NPC
from features.player import Player

class Intent(StrEnum):
    Attack = "Attack"
    Ability = "Ability"
    Item = "Item"


class AttackActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Attack")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Attack)
            response = view.show_targets()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AbilityActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Ability")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Ability)
            response = view.show_abilities()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ItemActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Item")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Item)
            response = view.show_items()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class TargetButton(discord.ui.Button):
    def __init__(self, label: str, target: Player | NPC, index: int, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        self._target = target
        self._index = index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_target(self._target, self._index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseItemButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._exact_item_index = exact_item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_item(self._exact_item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseAbilityButton(discord.ui.Button):
    def __init__(self, ability_index: int, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{ability.get_name()}", row=row, emoji=ability.get_icon())
        
        self._ability_index = ability_index
        self._ability = ability

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_ability(self._ability_index, self._ability)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BackToActionSelectButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.exit_to_action_select()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmAbilityButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_ability()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ContinueToNextActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Continue")
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.continue_turn()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BackUsingIntentButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label=f"Back", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.go_back_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DoActionOnTargetsButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Finish", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.do_action_on_selected_targets(is_finished=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmTargetButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_target()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingNextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingPrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SkipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Skip")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.continue_turn(skip_turn=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelView(discord.ui.View):
    # Using a data class instead of a tuple to make the code more readable
    @dataclass
    class DuelResult():
        game_won: bool
        winners: List[Player | NPC] | None

    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User], allies: List[Player], enemies: List[Player | NPC]):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._allies = allies
        self._enemies = enemies
        self._turn_order = sorted(allies + enemies, key=lambda x: x.get_expertise().dexterity)
        self._turn_index = 0

        self._intent: (Intent | None) = None
        self._selected_targets: List[Player | NPC] = []
        self._targets_remaining = 1
        self._selected_ability: (Ability | None) = None
        self._selected_ability_index: int = -1
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1
        self._target_own_group: bool = False
        self._current_target: Player | NPC = None # For passing along to the confirmation
        self._current_target_index: int = -1
        self._selecting_targets = False # For next/prev buttons

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._additional_info_string_data = ""

        for entity in allies + enemies:
            entity.get_dueling().is_in_combat = True
            # Make sure stats are correct.
            entity.get_expertise().update_stats(entity.get_equipment().get_total_buffs())

        cur_entity: (Player | NPC) = self._turn_order[self._turn_index]
        if isinstance(cur_entity, Player):
            self.show_actions()
        # TODO: Handle NPCs doing their own turns

    def get_user_from_player(self, player: Player):
        for user in self._users:
            if self._database[str(self._guild_id)]["members"][str(user.id)] == player:
                return user
        return None

    def get_user_for_current_turn(self):
        if isinstance(self._turn_order[self._turn_index], Player):
            return self.get_user_from_player(self._turn_order[self._turn_index])
        return None

    def get_name(self, entity: Player | NPC):
        if isinstance(entity, NPC):
            return entity.get_name()
        return self.get_user_from_player(entity).display_name

    def get_turn_index(self, entity: Player | NPC):
        for i, other_entity in enumerate(self._turn_order):
            if other_entity == entity:
                return i
        return -1

    def check_for_win(self) -> DuelResult:
        allies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._allies))
        enemies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._enemies))
        
        if len(allies_alive) == 0 and len(enemies_alive) == 0: # Tie, which may happen due to reflected damage
            return self.DuelResult(True, None)
        if len(enemies_alive) == 0:
            return self.DuelResult(True, self._allies)
        if len(allies_alive) == 0:
            return self.DuelResult(True, self._enemies)
        
        return self.DuelResult(False, None)

    def _reset_turn_variables(self, reset_actions=False):
        self._intent = None
        self._selected_targets = []
        self._targets_remaining = 1
        self._selected_ability = None
        self._selected_ability_index = -1
        self._selected_item = None
        self._selected_item_index = -1
        self._target_own_group = False
        self._current_target = None
        self._current_target_index = -1
        self._selecting_targets = False
        self._page = 0

        if reset_actions:
            self._actions_remaining = self._turn_order[self._turn_index].get_dueling().init_actions_remaining

    def set_next_turn(self):
        self._turn_index = (self._turn_index + 1) % len(self._turn_order)
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        entity: Player | NPC = self._turn_order[self._turn_index]
        start_damage: int = 0
        max_should_skip_chance: float = 0
        for se in entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.FixedDmgTick:
                start_damage += se.value
            if se.key == StatusEffectKey.Bleeding or se.key == StatusEffectKey.Poisoned:
                start_damage += entity.get_expertise().max_hp * se.value
            # Only take the largest chance to skip the turn
            if se.key == StatusEffectKey.TurnSkipChance:
                max_should_skip_chance = max(se.value, max_should_skip_chance)
        # Fixed damage is taken directly, no reduction
        entity.get_expertise().damage(start_damage, 0, 0)
        if start_damage > 0:
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_damage} damage! "

        if random() < max_should_skip_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            self._additional_info_string_data += f"{self.get_name(entity)}'s turn was skipped!"

        duel_result = self.check_for_win()
        if duel_result.game_won:
            return duel_result

        # Continue to iterate if the fixed damage killed the current entity
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        self._reset_turn_variables(True)

        return duel_result

    def get_duel_info_str(self):
        info_str = "──────────\n"
        for i, entity in enumerate(self._turn_order):
            info_str += f"({i + 1}) **{self.get_name(entity)}**\n\n{entity.get_expertise().get_health_and_mana_string()}"
            if len(entity.get_dueling().status_effects) > 0:
                info_str += f"\n\n{entity.get_dueling().get_statuses_string()}"
            info_str += "\n──────────\n"

        player_name = self.get_user_for_current_turn().display_name

        return info_str + f"\n*It's {player_name}'s turn!*"

    def get_selected_entity_full_duel_info_str(self):
        name = self.get_name(self._current_target)
        expertise = self._current_target.get_expertise()
        dueling = self._current_target.get_dueling()

        duel_string = f"──────────\n({self._current_target_index + 1}) **{name}**\n\n{expertise.get_health_and_mana_string()}"
        if len(dueling.status_effects) > 0:
            duel_string += f"{dueling.get_statuses_string()}"

        return f"{duel_string}\n──────────"

    def get_victory_screen(self, duel_result: DuelResult):
        self.clear_items()

        if duel_result.winners is None:
            for entity in self._turn_order:
                entity.get_dueling().status_effects = []
                entity.get_dueling().is_in_combat = False
                entity.get_dueling().reset_ability_cds()

                entity.get_expertise().update_stats(entity.get_equipment().get_total_buffs())
                entity.get_expertise().hp = entity.get_expertise().max_hp
                entity.get_expertise().mana = entity.get_expertise().max_mana
                
                entity.get_stats().dueling.duels_fought += 1
                entity.get_stats().dueling.duels_tied += 1

            return Embed(
                title="Victory for Both and Neither",
                description="A hard-fought battle resulting in a tie. Neither side emerges truly victorious and yet both have defeated their enemies."
            )
        
        # TODO: Implement what happens when an NPC group wins/loses.
        losers = self._allies if duel_result.winners == self._enemies else self._enemies

        for winner in duel_result.winners:
            winner.get_stats().dueling.duels_fought += 1
            winner.get_stats().dueling.duels_won += 1
        for loser in losers:
            loser.get_stats().dueling.duels_fought += 1

        if all(isinstance(entity, Player) for entity in self._turn_order):
            # This should only happen in a PvP duel
            winner_str = ""
            winner_xp = ceil(2 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                winner_expertise = winner.get_expertise()
                winner_dueling = winner.get_dueling()
                
                winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian)
                
                winner_dueling.reset_ability_cds()
                winner_dueling.status_effects = []
                winner_dueling.is_in_combat = False

                winner_expertise.update_stats(winner.get_equipment().get_total_buffs())
                winner_expertise.hp = winner_expertise.max_hp
                winner_expertise.mana = winner_expertise.max_mana

                winner_str += f"{self.get_name(winner)} *(+{winner_xp} Guardian xp)*\n"

            loser_str = ""
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (2 * len(losers)))
            for loser in losers:
                loser_expertise = loser.get_expertise()
                loser_dueling = loser.get_dueling()
                
                loser_expertise.add_xp_to_class(loser_xp, ExpertiseClass.Guardian)

                loser_dueling.reset_ability_cds()
                loser_dueling.status_effects = []
                loser_dueling.is_in_combat = False

                loser_expertise.update_stats(loser.get_equipment().get_total_buffs())
                loser_expertise.hp = loser_expertise.max_hp
                loser_expertise.mana = loser_expertise.max_mana

                loser_str += f"{self.get_name(loser)} *(+{loser_xp} Guardian xp)*\n"

            return Embed(title="Duel Finished", description=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}\nPractice for the journeys yet to come.")

        return Embed(title="Beyond the Veil", description="Hello, wayward adventurer. You've reached the in-between -- how strange.")

    def show_actions(self):
        self.clear_items()

        self.add_item(AttackActionButton())
        self.add_item(AbilityActionButton())
        self.add_item(ItemActionButton())
        self.add_item(SkipButton())

        self._reset_turn_variables()

        return Embed(title="Choose an Action", description=self.get_duel_info_str())

    def set_intent(self, intent: Intent):
        self._intent = intent

    def show_targets(self, target_own_group: bool=False):
        self.clear_items()

        self._selecting_targets = True

        cur_turn_entity: Player = self._turn_order[self._turn_index]
        taunt_target: Player | NPC = None
        for se in cur_turn_entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.Taunted:
                taunt_target = se.value
                break
        if taunt_target is not None:
            self._selected_targets = [taunt_target]
            return self.do_action_on_selected_targets()

        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Selected Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""
        
        self._target_own_group = target_own_group and self._intent != Intent.Attack

        # This should only be called for a Player
        targets: List[Player | NPC] = []
        description = ""

        if self._current_target is not None:
            description += self.get_selected_entity_full_duel_info_str() + "\n\n"

        if (cur_turn_entity in self._enemies and target_own_group) or (cur_turn_entity in self._allies and not target_own_group):
            targets = self._enemies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        elif (cur_turn_entity in self._enemies and not target_own_group) or (cur_turn_entity in self._allies and target_own_group):
            targets = self._allies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        
        page_slots = targets[self._page * self._NUM_PER_PAGE:min(len(targets), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, target in enumerate(page_slots):
            turn_number: int = self.get_turn_index(target)
            if isinstance(target, NPC):
                self.add_item(TargetButton(f"({turn_number + 1}) {target.get_name()}", target, turn_number, i))
            if isinstance(target, Player):
                user = self.get_user_from_player(target)
                self.add_item(TargetButton(f"({turn_number + 1}) {user.display_name}", target, turn_number, i))

        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(targets) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        if self._current_target is not None and self._current_target_index != -1:
            self.add_item(ConfirmTargetButton(min(4, len(page_slots))))
        if len(self._selected_targets) > 0:
            # This handles the cases where you might not want/need to select the max number
            # of possible targets.
            self.add_item(DoActionOnTargetsButton(min(4, len(page_slots))))
        self.add_item(BackUsingIntentButton(min(4, len(page_slots))))

        return Embed(title="Choose a Target", description=description)

    def attack_selected_targets(self):
        attacker = self._turn_order[self._turn_index]
        attacker_name = self.get_name(attacker)
        attacker_attrs = attacker.get_combined_attributes()
        attacker_equipment = attacker.get_equipment()

        generating_value = 0
        tarnished_value = 0
        for se in attacker.get_dueling().status_effects:
            if se.key == StatusEffectKey.Generating:
                generating_value = se.value
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        cursed_coins_damage = 0

        main_hand_item = attacker_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        # Base possible damage is [1, 2], basically fist fighting
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        result_strs = []
        for target in self._selected_targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()
            target_attrs = target.get_combined_attributes()

            target_name = self.get_name(target)
            target_dodged = random() < target_attrs.dexterity * DEX_DODGE_SCALE
            
            if target_dodged:
                target.get_stats().dueling.attacks_dodged += 1
                result_strs.append(f"{target_name} dodged the attack")
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < attacker_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                attacker.get_stats().dueling.critical_hit_successes += 1

            damage = int(weapon_stats.get_random_damage() * critical_hit_boost)
            damage += int(damage * STR_DMG_SCALE * max(attacker_attrs.strength, 0))
 
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()

            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)

            attacker.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != attacker), se.on_being_hit_buffs))
                    result_strs.append(f"{target_name} gained {se.get_buffs_str()}")
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)
            target.get_expertise().update_stats(target.get_dueling().get_combined_attribute_mods() + target.get_equipment().get_total_buffs())

            generating_string = ""
            if generating_value != 0:
                attacker.get_inventory().add_coins(generating_value)
                generating_string = f" and gained {generating_value} coins"

                if tarnished_value != 0:
                    cursed_coins_damage += int(tarnished_value * generating_value)
            
            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}{generating_string}")
        
            attacker.get_stats().dueling.attacks_done += 1
        
        if cursed_coins_damage != 0:
            if attacker in self._enemies:
                for other in self._allies:
                    other.get_expertise().damage(cursed_coins_damage, 0, 0)
                    attacker.get_stats().dueling.damage_dealt += cursed_coins_damage
                
                names_str = ", ".join([self.get_name(other) in self._allies])
                result_strs.append(f"{attacker_name} dealt {cursed_coins_damage} damage to {names_str}")
            elif attacker in self._allies:
                for other in self._enemies:
                    other.get_expertise().damage(cursed_coins_damage, 0, 0)
                    attacker.get_stats().dueling.damage_dealt += cursed_coins_damage
                
                names_str = ", ".join([self.get_name(other) in self._enemies])
                result_strs.append(f"{attacker_name} dealt {cursed_coins_damage} damage to {names_str} using Cursed Coins")

        return "\n".join(result_strs)

    def use_ability_on_selected_targets(self):
        caster = self._turn_order[self._turn_index]
        names = [self.get_name(caster), *[self.get_name(target) for target in self._selected_targets]]
        result_str = self._selected_ability.use_ability(caster, self._selected_targets)

        caster.get_stats().dueling.abilities_used += 1

        return result_str.format(*names)

    def use_item_on_selected_targets(self):
        # TODO: Implement item usage when said items exist.
        # TODO: And implement the stat increment.
        return "How did you get here?"

    def confirm_target(self):
        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Current Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""

        if self._current_target != self._turn_order[self._current_target_index]:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}*Error: That target changed position in the turn order or something else terrible happened.*\n\n{self._targets_remaining} targets remaining.")
        
        if self._current_target in self._selected_targets:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You already selected that target. {self._targets_remaining} targets remaining.")
        
        entity = self._turn_order[self._turn_index]
        if any(se.key == StatusEffectKey.CannotTarget and se.cant_target == entity for se in entity.get_dueling().status_effects):
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You can't select that target due to being Convinced. {self._targets_remaining} targets remaining.")

        self._selected_targets.append(self._current_target)
        self._targets_remaining -= 1
        self._current_target = None

        return self.do_action_on_selected_targets()

    def do_action_on_selected_targets(self, is_finished=False):
        # TODO: Better handle case where, for example, you might need to select 3 targets, but only 2 targets exist.
        # I'm using a boolean for that case at the moment rather than setting self._targets_remaining to 0, just to
        # make a clear distinction about this case in the code.
        if self._targets_remaining == 0 or self._targets_remaining == -1 or is_finished:
            self._page = 0
            self.clear_items()
            self.add_item(ContinueToNextActionButton())

            catch_phrases = []
            result_str = ""
            if self._intent == Intent.Attack:
                catch_phrases = [
                    "Now, strike!",
                    "Yield to none!",
                    "Glory is yours!"
                ]
                result_str = self.attack_selected_targets()
            if self._intent == Intent.Ability:
                catch_phrases = [
                    "Behold true power!",
                    "Surge as they crumble!",
                    "Calamity unleashed!"
                ]
                result_str = self.use_ability_on_selected_targets()
            if self._intent == Intent.Item:
                catch_phrases = [
                    "A useful trinket!",
                    "The time is now!",
                    "A perfect purpose!"
                ]
                result_str = self.use_item_on_selected_targets()
            
            return Embed(title=choice(catch_phrases), description=result_str)
        self._page = 0
        self._selecting_targets = True
        return self.show_targets(self._target_own_group)

    def show_items(self, error_str: str | None=None):
        self._page = 0
        self._get_current_items_page_buttons()
        return self._get_current_page_info(error_str)

    def show_abilities(self, error_str: str | None=None):
        self._page = 0
        self._get_current_abilities_page_buttons()
        return self._get_current_page_info(error_str)

    def _get_current_items_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index]
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Consumable.Consumable])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(ChooseItemButton(exact_item_index, item, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            self.add_item(ConfirmItemButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def _get_current_abilities_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index]
        expertise: Expertise = player.get_expertise()
        dueling: Dueling = player.get_dueling()

        page_slots = dueling.abilities[self._page * self._NUM_PER_PAGE:min(len(dueling.abilities), (self._page + 1) * self._NUM_PER_PAGE)][:expertise.memory]
        for i, ability in enumerate(page_slots):
            self.add_item(ChooseAbilityButton(i + (self._page * self._NUM_PER_PAGE), ability, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(dueling.abilities) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))

        sanguinated_active = any(se.key == StatusEffectKey.ManaToHP for se in dueling.status_effects)

        if self._selected_ability is not None:
            if self._selected_ability.get_cur_cooldown() == 0:
                if expertise.mana >= self._selected_ability.get_mana_cost() or sanguinated_active:
                    self.add_item(ConfirmAbilityButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def exit_to_action_select(self):
        self._reset_turn_variables()
        return self.show_actions()

    def _get_current_page_info(self, error_str: str | None=None):
        player: Player = self._turn_order[self._turn_index]
        description = ""
        if self._intent == Intent.Item:
            description = "Selected item info will be displayed here."
            if self._selected_item is not None:
                description = f"──────────\n{self._selected_item}\n──────────"
        if self._intent == Intent.Ability:
            description = f"{player.get_expertise().get_health_and_mana_string()}\nCoins: {player.get_inventory().get_coins_str()}\n\n"
            if self._selected_ability is not None:
                description += f"──────────\n{self._selected_ability}\n──────────"
            else:
                description += "Selected ability info will be displayed here."
        if error_str is not None:
            description += f"\n\n{error_str}"
        return Embed(title=f"Choose an {self._intent}", description=description)

    def next_page(self):
        self._page += 1
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def select_item(self, exact_item_index: int, item: Item):
        self._selected_item_index = exact_item_index
        self._selected_item = item

        self._get_current_abilities_page_buttons()
        return self._get_current_page_info()
        
    def select_ability(self, ability_index: int, ability: Ability):
        self._selected_ability_index = ability_index
        self._selected_ability = ability

        self._get_current_abilities_page_buttons()
        return self._get_current_page_info()

    def confirm_item(self):
        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_inventory().item_exists(self._selected_item)
        if found_index == self._selected_item_index:
            self._page = 0
            self._selecting_targets = True
            return self.show_targets()
        return self.show_items("*Error: That item couldn't be selected.*")

    def confirm_ability(self):
        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_dueling().ability_exists(self._selected_ability)
        if found_index == self._selected_ability_index:
            self._targets_remaining = self._selected_ability.get_num_targets()
            target_own_group = self._selected_ability.get_target_own_group()

            if self._targets_remaining == 0:
                self._selected_targets = [entity]
                return self.do_action_on_selected_targets()
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    self._selected_targets = self._enemies
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    self._selected_targets = self._allies
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_abilities("*Error: That ability couldn't be selected.*")

    def select_target(self, target: Player | NPC, index: int):
        self._current_target_index = index
        self._current_target = target

        return self.show_targets(self._target_own_group)
 
    def continue_turn(self, skip_turn=False):
        self._page = 0
        cur_entity: (Player | NPC) = self._turn_order[self._turn_index]

        # Check here before setting next turn, just in case
        duel_result = self.check_for_win()
        if duel_result.game_won:
            return self.get_victory_screen()

        dueling: Dueling = cur_entity.get_dueling()
        dueling.actions_remaining = max(0, dueling.actions_remaining - 1)
        if dueling.actions_remaining == 0 or skip_turn:
            # CDs and status effect time remaining decrement at the end of the turn,
            # so they actually last a turn
            dueling.decrement_all_ability_cds()
            dueling.decrement_statuses_time_remaining()
            duel_result = self.set_next_turn()
            if duel_result.game_won:
                return self.get_victory_screen()
        
        next_entity: (Player | NPC) = self._turn_order[self._turn_index]
        next_entity_dueling: Dueling = next_entity.get_dueling()
        if isinstance(next_entity, Player):
            next_entity_dueling.actions_remaining = next_entity_dueling.init_actions_remaining
            return self.show_actions()
        # TODO: Handle NPC AI doing their own turns

    def go_back_using_intent(self):
        self._page = 0
        self._selecting_targets = False
        if self._intent == Intent.Attack:
            return self.show_actions()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            return self.show_abilities()
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            return self.show_items()

# -----------------------------------------------------------------------------
# PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.accept_request(interaction.user)
        if not view.all_accepted():
            await interaction.response.edit_message(embed=response, view=view, content=None)
        else:
            users: List[discord.User] = [view.get_challenger(), *view.get_opponents()]
            challenger_player: Player = view.get_challenger_player()
            opponents_players: List[Player] = view.get_opponents_players()
            
            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), users, [challenger_player], opponents_players)
            initial_info: Embed = duel_view.show_actions()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't decline this request!", view=view)
            return

        view.clear_items()
        await interaction.response.edit_message(content="The duel was declined.", view=view, embed=None)


class PlayerVsPlayerDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, challenger: discord.User, opponents: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._challenger = challenger
        self._opponents = opponents

        self._acceptances: List[discord.User] = []

        self.add_item(AcceptButton())
        self.add_item(DeclineButton())

    def get_info_embed(self):
        not_accepted = list(filter(lambda x: x not in self._acceptances, self._opponents))
        not_accepted_names = "\n".join(list(map(lambda x: x.display_name, not_accepted)))
        return Embed(title="PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The game will begin when all challenged players accept the invitation to play.\n\n**Waiting on acceptances from:**\n\n{not_accepted_names}"
        ))

    def accept_request(self, user: discord.User):
        if user not in self._acceptances:
            self._acceptances.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._acceptances for user in self._opponents)

    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_challenger(self):
        return self._challenger

    def get_opponents(self):
        return self._opponents

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_challenger_player(self):
        return self._get_player(self._challenger.id)

    def get_opponents_players(self):
        return [self._get_player(opponent.id) for opponent in self._opponents]
