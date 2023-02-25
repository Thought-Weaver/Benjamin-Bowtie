import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.dueling import DuelView
from features.stories.forest.combat.npcs.wild_boar import WildBoar

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player

# -----------------------------------------------------------------------------
# WILD BOAR DUEL INTRO
# -----------------------------------------------------------------------------

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WildBoarDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [WildBoar(), WildBoar()])
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class WildBoarDuelView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="", description="")

    def _display_initial_buttons(self):
        self.clear_items()

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
