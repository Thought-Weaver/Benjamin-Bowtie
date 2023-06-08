from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player


class Settings():
    def __init__(self):
        self.mature_plant_notifications: bool = False
        self.mail_notifications: bool = False

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.mature_plant_notifications = state.get("mature_plant_notifications", False)
        self.mail_notifications = state.get("mail_notifications", False)


class PlantNotificationsButton(discord.ui.Button):
    def __init__(self, player: Player, row: int):
        toggle_str: str = "Disable" if player.get_settings().mature_plant_notifications else "Enable"
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{toggle_str} Mature Plant Notifications", row=row)

        self._player = player

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SettingsView = self.view
        if interaction.user == view.get_user():
            self._player.get_settings().mature_plant_notifications = not self._player.get_settings().mature_plant_notifications
            view.get_buttons()


class MailNotificationsButton(discord.ui.Button):
    def __init__(self, player: Player, row: int):
        toggle_str: str = "Disable" if player.get_settings().mature_plant_notifications else "Enable"
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{toggle_str} Mail Notifications", row=row)

        self._player = player

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SettingsView = self.view
        if interaction.user == view.get_user():
            self._player.get_settings().mail_notifications = not self._player.get_settings().mail_notifications
            view.get_buttons()


class SettingsView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self.get_buttons()

    def get_player(self, user_id: int | None=None) -> Player:
        if user_id is None:
            return self._database[str(self._guild_id)]["members"][str(self._user.id)]
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_buttons(self):
        player = self.get_player(self._user.id)

        self.clear_items()
        self.add_item(PlantNotificationsButton(player, 0))
        self.add_item(MailNotificationsButton(player, 1))

    def get_initial_embed(self):
        return Embed(
            title="Settings",
            description="Enable and disable optional settings to adjust your experience."
        )

    def get_user(self):
        return self._user
