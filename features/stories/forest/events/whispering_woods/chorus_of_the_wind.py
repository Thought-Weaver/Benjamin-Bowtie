from __future__ import annotations

import discord
from features.shared.statuseffect import DmgBuff, DmgReduction
import features.stories.forest.forest as forest

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.views.dueling_view import DuelView
from features.player import Player
from features.stories.dungeon_run import DungeonRun, RoomSelectionView
from features.stories.forest.combat.npcs.song_of_the_woods import SongOfTheWoods

from typing import List

# -----------------------------------------------------------------------------
# DUEL VICTORY
# -----------------------------------------------------------------------------

class DuelVictoryContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: VictoryView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class VictoryView(discord.ui.View):
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

    def get_initial_embed(self):
        return Embed(title="Then, Silence", description=f"With the snapdragon vanquished, the rest of the woods await.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(DuelVictoryContinueButton())

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# DUEL INTRO
# -----------------------------------------------------------------------------

class DuelContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SnapdragonDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: forest.ForestDefeatView = forest.ForestDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [SongOfTheWoods()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class SnapdragonDuelView(discord.ui.View):
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

    def get_initial_embed(self):
        return Embed(title="A Haunting Voice", description="You follow the sound of the singing deeper into the woods, eventually coming to a grove of vines and bushes. Pushing them aside, you see a giant plant at its center -- and a hundred stalks begin to rise. Each has a grey-black flower that looks like a skull and each flower moves as though it had lips to sing. It draws you in, closer and closer!")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(DuelContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_players(self):
        return [self._get_player(user.id) for user in self._users]

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
    
    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# CHORUS OF THE WIND VIEW
# -----------------------------------------------------------------------------

class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Leave")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChorusOfTheWindView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class SingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Sing")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChorusOfTheWindView = self.view
        if interaction.user.id == view.get_group_leader().id:
            response = view.sing()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class FollowButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Follow")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ChorusOfTheWindView = self.view
        if interaction.user.id == view.get_group_leader().id:
            duel_room = SnapdragonDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
            initial_info: Embed = duel_room.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_room, content=None)


class ChorusOfTheWindView(discord.ui.View):
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

    def get_initial_embed(self):
        return Embed(title="Chorus of the Wind", description=f"You enter a section of these whispering woods where indeed the whispering seems to turn to soft singing on the winds. You find yourself compelled by three possibilities:")

    def sing(self):
        self.clear_items()
        self.add_item(LeaveButton())

        for user in self._users:
            player = self._get_player(user.id)
            
            dmg_buff = DmgBuff(
                turns_remaining=10,
                value=0.2,
                source_str="The Chorus of the Wind"
            )
            
            dmg_resist = DmgReduction(
                turns_remaining=10,
                value=0.2,
                source_str="The Chorus of the Wind"
            )

            player.get_dueling().status_effects += [dmg_buff, dmg_resist]
        
        return Embed(title="Chorus of the Wind", description=f"The song fills you and rather than follow the compulsion to follow it, instead you choose to harmonize and sing alongside it. The song on the wind begins to change as you do, and you find yourselves all filled with a warm, powerful feeling.")
    
    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(SingButton())
        self.add_item(FollowButton())
        self.add_item(LeaveButton())

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