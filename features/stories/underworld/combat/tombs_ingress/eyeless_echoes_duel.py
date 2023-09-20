from __future__ import annotations

import discord
from features.stories.underworld.combat.tombs_ingress.chthonic_emissary_duel import ChthonicEmissaryDuelView
import features.stories.underworld.underworld as underworld

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.stories.underworld.combat.npcs.echo_of_yenna import EchoOfYenna
from features.stories.underworld.combat.npcs.echo_of_asterius import EchoOfAsterius
from features.stories.underworld.combat.npcs.echo_of_passerhawk import EchoOfPasserhawk
from features.views.dueling_view import DuelView

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.player import Player
    from features.stories.dungeon_run import DungeonRun

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

        for player in view.get_players():
            player.get_dueling().status_effects = []
            player.get_expertise().heal(int(player.get_expertise().max_hp))
            player.get_expertise().restore_mana(int(player.get_expertise().max_mana))

        next_view: ChthonicEmissaryDuelView = ChthonicEmissaryDuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = next_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=next_view, content=None)


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
        return Embed(title="The Heroes Fade", description=f"With the echoes of the Fellowship of the Eyeless vanquished, the mists begin to fade back to their normal levels. The doors are before you, unguarded and waiting to be opened. The arcane barrier that holds them remains in place, but you can see points along the pattern at the base which look particularly important.\n\nAs you approach, another shockwave rocks the cavern and nudges the doors ever so slightly. The lines of mana spark and dissipate for a moment before reforming in their original configuration. The source, you realize, is behind those doors: Something is trying to get out.\n\nYou reach out to the sources of mana along the doors, feeling like the world is speeding up around you as you get closer and closer. Then, as you touch one of them, a burst of light erupts from it and wraps you in threads that extend up your arm, around your head, and all throughout your body. And as the light fades, you realize you're not where you were; you're on the other side of the gate.")

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

class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EyelessEchoesDuelView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: underworld.UnderworldDefeatView = underworld.UnderworldDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [EchoOfYenna(), EchoOfAsterius(), EchoOfPasserhawk()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class EyelessEchoesDuelView(discord.ui.View):
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
        return Embed(title="The Gate", description=(
            "The ruins of the city have only grown denser as you've progressed; more buildings carved in the stone, more sentinels at every turn, and more passageways to become lost in have done everything in their power to keep you from your goal. Up ahead, you can hear the occasional clink of something falling onto the ground from somewhere high above.\n\n"
            "You emerge now into a grand cavern, so large you might as well be above ground, and before you all stand two enormous doors -- towering hundreds of feet into the air -- infused with more arcane power than you could have ever imagined; sigils and lines intersect in a mechanical pattern that keeps the seal intact, focusing on a golden circle in the center.\n\n"
            "Looking closer at the seal, you can see something else etched -- not for the sake of the sorcery wrought here, but a depiction of three people fighting an entity shrouded in shredded cloak. One of the figures bears warrior's armor and a powerful sword, another a staff and wise robes, and the last weaves threads of mana in an intricate dance.\n\n"
            "What next catches your attention is that you're not alone: In front of these doors is an unfurling mist which has begun to expand outwards rapidly. Though most of the fog grasps the ground tightly, some of it begins to coalesce into a figure, then another, then another.\n\n"
            "\"Kasandra, where is Kasandra?\" shouts one of the mist-people in desperate alarm as their face begins to take form. \"We should never have come here, we should have just let it be,\" whispers one of the others, though you can't say which. \"Snap out of it you two! If we can't kill it, then we keep to our backup plan,\" says the last one, robe billowing into existence.\n\n"
            "The conversation stops as they turn to see your party standing there behind them. \"More cultists of avarice!\" shouts one of the echoes, leading the charge against your party."
        ))

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ContinueButton())

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
