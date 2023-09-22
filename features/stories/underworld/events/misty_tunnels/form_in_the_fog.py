from __future__ import annotations
import random

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.ability import ALCHEMIST_ABILITIES, FISHER_ABILITIES, GUARDIAN_ABILITIES, MERCHANT_ABILITIES, VOID_ABILITIES, Ability
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: UnderworldRoomSelectionView = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class PowerButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Power")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.choose_power()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class KnowledgeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Knowledge")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.choose_knowledge()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WealthButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Wealth")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: FormInTheFogView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.choose_wealth()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class FormInTheFogView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def choose_power(self):
        self.clear_items()
        self.add_item(ContinueButton())

        rand_val: int = random.randint(0, 5)
        leader_player: Player = self._get_player(self._group_leader.id)
        attr_str: str = ""
        if rand_val == 0:
            leader_player.get_expertise().constitution += 1
            attr_str = "Constitution"
        elif rand_val == 1:
            leader_player.get_expertise().strength += 1
            attr_str = "Strength"
        elif rand_val == 2:
            leader_player.get_expertise().dexterity += 1
            attr_str = "Dexterity"
        elif rand_val == 3:
            leader_player.get_expertise().intelligence += 1
            attr_str = "Intelligence"
        elif rand_val == 4:
            leader_player.get_expertise().luck += 1
            attr_str = "Luck"
        else:
            leader_player.get_expertise().memory += 1
            attr_str = "Memory"

        damage: int = int(0.5 * leader_player.get_expertise().max_hp)
        leader_player.get_expertise().damage(damage, leader_player.get_dueling(), 0, True)

        return Embed(title="Power", description=f"\"A worthwhile deal, I'm sure you'll agree,\" it says as you suddenly look down and see blood pouring from where your heart is and towards the figure.\n\n{self._group_leader.display_name} took {damage} piercing damage and gained +1 {attr_str} permanently.")

    def get_available_abilities(self, player: Player, all_abilities: List[List[type]]):
        player_abilities: List[Ability] = player.get_dueling().available_abilities
        available_abilities: List[Ability] = []
        for ability_group in all_abilities:
            result: Ability | None = ability_group[0]()
            for ability_class in ability_group:
                if any(isinstance(ability, ability_class) for ability in player_abilities):
                    result = None
                    break
            if result is not None:
                available_abilities.append(result)
        return available_abilities

    def choose_knowledge(self):
        self.clear_items()
        self.add_item(ContinueButton())

        leader_player: Player = self._get_player(self._group_leader.id)

        available_abilities: List[Ability] = self.get_available_abilities(leader_player, FISHER_ABILITIES + GUARDIAN_ABILITIES + MERCHANT_ABILITIES + ALCHEMIST_ABILITIES + VOID_ABILITIES)
        
        result_str: str = "nothing"
        if len(available_abilities) > 0:
            random_ability = random.choice(available_abilities)
            leader_player.get_dueling().available_abilities.append(random_ability)
            result_str = random_ability.get_icon_and_name()

        damage: int = int(0.5 * leader_player.get_expertise().max_hp)
        leader_player.get_expertise().damage(damage, leader_player.get_dueling(), 0, True)

        return Embed(title="Knowledge", description=f"\"A worthwhile deal, I'm sure you'll agree,\" it says as you suddenly look down and see blood pouring from where your heart is and towards the figure.\n\n{self._group_leader.display_name} took {damage} piercing damage and learned {result_str}.")

    def choose_wealth(self):
        self.clear_items()
        self.add_item(ContinueButton())

        leader_player: Player = self._get_player(self._group_leader.id)

        leader_player.get_inventory().add_coins(300)

        damage: int = int(0.5 * leader_player.get_expertise().max_hp)
        leader_player.get_expertise().damage(damage, leader_player.get_dueling(), 0, True)

        return Embed(title="Wealth", description=f"\"A worthwhile deal, I'm sure you'll agree,\" it says as you suddenly look down and see blood pouring from where your heart is and towards the figure.\n\n{self._group_leader.display_name} took {damage} piercing damage and gained 300 coins.")

    def get_initial_embed(self):
        return Embed(title="The Form in the Fog", description="The mists in this area grow thick as fog and soon you find yourselves huddling close together for protection. Ahead of you, there's a spot darker than the rest: An outline of a figure like a person that begins to speak to you.\n\n\"What a journey you find yourselves on. Perhaps I can be of some assistance? If your group leader there wouldn't mind a little bargain, I would be happy to offer you a choice of power, knowledge, or wealth. Come closer.\"")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(PowerButton())
        self.add_item(KnowledgeButton())
        self.add_item(WealthButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_group_leader(self):
        return self._group_leader

    def get_dungeon_run(self):
        return self._dungeon_run