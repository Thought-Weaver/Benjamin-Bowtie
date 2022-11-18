from __future__ import annotations

import discord
import time

from discord.embeds import Embed
from discord.ext import commands
from features.house.house import HouseView
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.inventory import Inventory, Item
    from features.player import Player
    from features.stats import Stats


class Mail():
    def __init__(self, sender_name: str, item: Item | None, coins: int, message: str, send_date: str, sender_id: int):
        self._sender_name = sender_name
        self._item = item
        self._message = message
        self._send_date = send_date
        self._coins = coins
        self._sender_id = sender_id

    def get_sender_name(self):
        return self._sender_name

    def get_item(self):
        return self._item

    def get_message(self):
        return self._message

    def get_send_date(self):
        return self._send_date

    def get_coins(self):
        return self._coins

    def get_sender_id(self):
        return self._sender_id

    def __eq__(self, obj):
        if not isinstance(obj, Mail):
            return False

        if (self._sender_name == obj.get_sender_name() and self._item == obj.get_item()
            and self._message == obj.get_message() and self._send_date == obj.get_send_date()
            and self._coins == obj.get_coins() and self._sender_id == obj.get_sender_id()):
            return True

        return False

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._sender_name = state.get("_sender_name", "")
        self._item = state.get("_item", None)
        self._message = state.get("_message", "")
        self._send_date = state.get("_send_date", "")
        self._coins = state.get("_coins", 0)
        self._sender_id = state.get("_sender_id", -1)


class InventoryMailButton(discord.ui.Button):
    def __init__(self, adjusted_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        self._item = item
        self._adjusted_item_index = adjusted_item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MailView = self.view

        if view.get_user() == interaction.user:
            await interaction.response.send_modal(MailModal(
                view.get_database(),
                view.get_guild_id(),
                view.get_user(),
                view.get_giftee(),
                self._adjusted_item_index,
                self._item,
                view,
                interaction.message.id)
            )


class MailView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, giftee: discord.User, context: commands.Context):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = context.guild.id
        self._user = context.author
        self._giftee = giftee
        self._context = context
        self._page = 0

        self._NUM_PER_PAGE = 4
        
        self._get_current_page_buttons()

    def get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player(self._user.id)
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryMailButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

    async def refresh(self, message_id):
        self._get_current_page_buttons()
        message: discord.Message = await self._context.fetch_message(message_id)
        await message.edit(view=self)

    def get_user(self):
        return self._user

    def get_giftee(self):
        return self._giftee

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id


class MailModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, giftee: discord.User, adjusted_item_index: int, item: Item, view: MailView, message_id: int):
        super().__init__(title=f"Mailing a gift to {giftee.display_name}!")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._giftee = giftee
        self._adjusted_item_index = adjusted_item_index
        self._item = item
        self._view = view
        self._message_id = message_id

        self._count_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Quantity",
            default="1",
        )
        self.add_item(self._count_input)

        self._coins_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Coins",
            default="0"
        )
        self.add_item(self._coins_input)

        self._message_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Message",
            required=False,
            style=discord.TextStyle.paragraph,
            placeholder="Anything you'd like to say?",
            max_length=1500
        )
        self.add_item(self._message_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        player: Player = self._get_player(self._user.id)
        giftee_player: Player = self._get_player(self._giftee.id)
        inventory = player.get_inventory()
        
        found_index = inventory.item_exists(self._item)
        if found_index != self._adjusted_item_index:
            await interaction.response.send_message(f"Error: Something about your inventory changed. Try using b!mail again.")
            return

        if not self._count_input.value.isnumeric() or int(self._count_input.value) < 0:
            await interaction.response.send_message(f"Error: You must send a non-negative number of that item.")
            return

        if int(self._count_input.value) > self._item.get_count():
            await interaction.response.send_message(f"Error: You can't send {int(self._count_input.value)} of that item, you only have {self._item.get_count()}.")
            return

        if not self._coins_input.value.isnumeric() or int(self._coins_input.value) < 0:
            await interaction.response.send_message(f"Error: You can't send a negative number of coins.")
            return

        if int(self._coins_input.value) > inventory.get_coins():
            await interaction.response.send_message(f"Error: You don't have that many coins to send.")
            return

        num_items_to_send = int(self._count_input.value)
        sent_item = inventory.remove_item(self._adjusted_item_index, num_items_to_send)
        sent_coins = int(self._coins_input.value)
        inventory.remove_coins(sent_coins)

        if sent_coins == 0 and sent_item is None and self._message_input.value == "":
            await interaction.response.send_message(f"Error: You can't send an empty message.")
            return

        mail = Mail(self._user.display_name, sent_item, sent_coins, self._message_input.value, str(time.time()).split(".")[0], self._user.id)
        giftee_player.get_mailbox().append(mail)
        
        if sent_coins > 0:
            coin_str = "coin" if sent_coins == 1 else "coins"
            if sent_item is not None:
                await interaction.response.send_message(f"You mailed {num_items_to_send} {sent_item.get_full_name()} and {sent_coins} {coin_str} to {self._giftee.display_name}!")
            else:
                await interaction.response.send_message(f"You mailed {sent_coins} {coin_str} to {self._giftee.display_name}!")
        else:
            if sent_item is not None:
                await interaction.response.send_message(f"You mailed {num_items_to_send} {sent_item.get_full_name()} to {self._giftee.display_name}!")
            else:
                await interaction.response.send_message(f"You mailed a letter to {self._giftee.display_name}!")
        
        player_stats: Stats = player.get_stats()
        if giftee_player == player:
            player_stats.mail.items_sent_to_self += num_items_to_send
            player_stats.mail.coins_sent_to_self += sent_coins

            if self._message_input.value != "":
                player_stats.mail.messages_sent_to_self += 1

            player_stats.mail.mail_sent_to_self += 1
        else:
            player_stats.mail.items_sent += num_items_to_send
            player_stats.mail.coins_sent += sent_coins

            if self._message_input.value != "":
                player_stats.mail.messages_sent += 1

            player_stats.mail.mail_sent += 1
        
        await self._view.refresh(self._message_id)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")


class MailboxButton(discord.ui.Button):
    def __init__(self, mail_index: int, mail: Mail):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"✉️ From: {mail.get_sender_name()}", row=mail_index)
        
        self._mail_index = mail_index
        self._mail = mail

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MailboxView = self.view
        if interaction.user == view.get_user():
            if view.open_mail(self._mail_index, self._mail):
                await interaction.response.edit_message(content=None, embed=view.get_current_page_info(), view=view)

                player: Player = view.get_player()
                player_stats: Stats = player.get_stats()

                coins_received = self._mail.get_coins()
                mail_message = f"From: {self._mail.get_sender_name()} (<t:{self._mail.get_send_date()}:R>)"
                if self._mail.get_item() is not None:
                    mail_message += f"\n\nItem: {self._mail.get_item().get_full_name_and_count()} each worth {self._mail.get_item().get_value_str()}"
                    if interaction.user.id != self._mail.get_sender_id():
                        player_stats.mail.items_received += 1
                if coins_received > 0:
                    mail_message += f"\n\nCoins: {coins_received}"
                    if interaction.user.id != self._mail.get_sender_id():
                        player_stats.mail.coins_received += coins_received
                if self._mail.get_message() != "":
                    mail_message += f"\n\nMessage:\n\n{self._mail.get_message()}"
                    if interaction.user.id != self._mail.get_sender_id():
                        player_stats.mail.messages_received += 1

                if interaction.user.id != self._mail.get_sender_id():
                    player_stats.mail.mail_opened += 1

                await interaction.user.send(mail_message)
            else:
                embed = view.get_current_page_info()
                embed.description += "\n\n*Error: That mail is no longer available.*"
                await interaction.response.edit_message(content=None, embed=embed, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MailboxView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView | None = view.get_house_view()
            if house_view is not None:
                embed = house_view.get_initial_embed()
                await interaction.response.edit_message(content=None, embed=embed, view=house_view)
            else:
                await interaction.response.defer()


class MailboxView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: discord.User, house_view: HouseView | None=None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view

        self._page = 0

        self._NUM_PER_PAGE = 4
        
        self._get_current_page_buttons()

    def get_player(self, user_id: int | None=None) -> Player:
        if user_id is None:
            return self._database[str(self._guild_id)]["members"][str(self._user.id)]
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player()
        mailbox: List[Mail] = player.get_mailbox()

        page_slots = mailbox[self._page * self._NUM_PER_PAGE:min(len(mailbox), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(MailboxButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(mailbox) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self.get_house_view() is not None:
            self.add_item(ExitToHouseButton(min(4, len(page_slots))))
        
    def get_current_page_info(self):
        return Embed(
            title=f"{self._user.display_name}'s Mailbox",
            description="Navigate through your mail using the Prev and Next buttons."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self.get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self.get_current_page_info()

    def _mail_exists(self, mailbox: List[Mail], mail: Mail):
        for i, mailbox_mail in enumerate(mailbox):
            if mailbox_mail == mail:
                return i
        return -1

    def open_mail(self, mail_index: int, mail: Mail):
        player: Player = self.get_player()
        inventory: Inventory = player.get_inventory()
        mailbox: List[Mail] = player.get_mailbox()

        if mail_index >= len(mailbox):
            self._get_current_page_buttons()
            return False
        
        adjusted_index = mail_index + (self._page * self._NUM_PER_PAGE)
        found_index = self._mail_exists(mailbox, mail)
        if found_index != adjusted_index:
            self._get_current_page_buttons()
            return False

        mailbox_mail = mailbox.pop(adjusted_index)
        inventory.add_item(mailbox_mail.get_item())
        inventory.add_coins(mailbox_mail.get_coins())

        self._get_current_page_buttons()
        return True

    def get_user(self):
        return self._user

    def get_house_view(self):
        return self._house_view
