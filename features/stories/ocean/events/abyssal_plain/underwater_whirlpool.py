from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.shared.statuseffect import DexDebuff, StrDebuff
from features.stories.dungeon_run import DungeonRun
from features.stories.ocean_room_selection import OceanRoomSelectionView

from typing import Dict, List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderwaterWhirlpoolView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view: OceanRoomSelectionView = OceanRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class GoAroundButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Go Around")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderwaterWhirlpoolView = self.view
        view.users_swimming[interaction.user.id] = False

        if len(view.users_swimming) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class SwimThroughButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Swim Through")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: UnderwaterWhirlpoolView = self.view
        view.users_swimming[interaction.user.id] = True

        if len(view.users_swimming) == len(view.get_users()):
            response = view.resolve()
            await interaction.response.edit_message(content=None, embed=response, view=view)
        else:
            await interaction.response.edit_message(content=None, embed=view.get_initial_embed(), view=view)


class UnderwaterWhirlpoolView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.users_swimming: Dict[int, bool] = {}
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Underwater Whirlpool", description=f"As you continue through the stygian depths, you come across an enormous, collapsed region of stone. The entire area looks as though it's been shattered and sunk into itself. In place of the endless field of sand that occupies the rest of the abyss, this has become a terrifying underwater whirlpool.\n\nIf you stay at the edge, you might be able to power through to the other side and avoid being dragged in, but it'll be quite a feat of strength. The only alternative would be to take a long, safe route around. In any case, you'll all have to go to together and need to vote what approach is best.\n\n{len(self.users_swimming)}/{len(self._users)} have decided on their course of action.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(GoAroundButton())
        self.add_item(SwimThroughButton())

    def resolve(self):
        self.clear_items()
        self.add_item(ContinueButton())

        num_swim_through = sum(choice == True for choice in self.users_swimming.values())
        results: List[str] = []

        if num_swim_through > len(self._users) // 2:
            for user in self._users:
                player = self._get_player(user.id)
                if player.get_expertise().strength > 20:
                    results.append(f"{user.display_name} successfully pushed through the raging whirlpool and made it to the other side.")
                else:
                    debuffs = [DexDebuff(-1, -20, "Underwater Whirlpool"), StrDebuff(-1, -20, "Underwater Whirlpool")]
                    player.get_dueling().status_effects += debuffs

                    results.append(f"{user.display_name} tried to gather their strength to make it to the other side, but got dragged in the whirlpool and was greatly weakened.")
        else:
            self._dungeon_run.rooms_until_boss += 3
            results.append("You all decide to take the long way around, which will increase the length of the journey, but was definitely the safer route.")

        final_str: str = "\n\n".join(results)
        return Embed(title="Through the Whirlpool", description=f"{final_str}")

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