from bot import BenjaminBowtieBot
from discord import embeds, User
from discord.ext import commands, tasks
from enum import Enum
from math import ceil
from typing import List, Union

from games.knucklebones import Knucklebones

import dill
import discord
import os
import random
import shutil
import time

# -----------------------------------------------------------------------------
# INVENTORY AND ITEMS
# -----------------------------------------------------------------------------

class Item():
    def __init__(self, icon: str, name: str, value: int, count=1, is_unique=False):
        self._icon = icon
        self._name = name
        self._value = value
        self._count = count
        self._is_unique = is_unique

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(self._icon, self._name, self._value, amount, self._is_unique)
            self._count -= amount
            return result
        return None

    def add_amount(self, amount: int):
        self._count += amount

    def get_name(self):
        return self._name

    def get_full_name(self):
        return f"{self._icon} {self._name}"

    def get_full_name_and_count(self):
        return f"{self._icon} {self._name} ({self._count})"

    def get_value(self):
        return self._value

    def get_value_str(self):
        if self._value == 1:
            return "1 coin"
        return f"{self._value} coins"

    def get_count(self):
        return self._count

    def get_is_unique(self):
        return self._is_unique

    def get_icon(self):
        return self._icon

    def __eq__(self, obj):
        if not isinstance(obj, Item):
            return False
        
        if self._is_unique or obj.get_is_unique():
            return False
        
        if self._icon == obj.get_icon() and self._name == obj.get_name() and self._value == obj.get_value():
            return True

        return False


class Inventory():
    def __init__(self):
        self._inventory_slots: List[Item] = []
        self._coins: int = 0

    def _organize_inventory_slots(self):
        if len(self._inventory_slots) == 0:
            return
        
        item_set: List[Item] = []
        if len(self._inventory_slots) == 1:
            item = self._inventory_slots[0]
            item_set.append(Item(item.get_icon(), item.get_name(), item.get_value(), 0, item.get_is_unique()))
        if len(self._inventory_slots) >= 2:
            for item in self._inventory_slots:
                exists = False
                for item_in_set in item_set:
                    if item_in_set == item:
                        exists = True
                        break
                if not exists:
                    item_set.append(Item(item.get_icon(), item.get_name(), item.get_value(), 0, item.get_is_unique()))

        new_slots: List[Item] = []
        for item in item_set:
            for other_item in self._inventory_slots:
                if item == other_item:
                    item.add_amount(other_item.get_count())
            if item.get_count() != 0:
                new_slots.append(item)

        self._inventory_slots = sorted(new_slots, key=lambda item: item.get_name())

    def item_exists(self, item: Item):
        for i, inv_item in enumerate(self._inventory_slots):
            if inv_item == item:
                return i
        return -1

    def search_by_name(self, name: str):
        for i, item in enumerate(self._inventory_slots):
            if item.get_name() == name:
                return i
        return -1

    def add_item(self, item: Item):
        self._inventory_slots.append(item)
        self._organize_inventory_slots()

    def remove_item(self, slot_index: int, count=1):
        if slot_index < len(self._inventory_slots):
            result = self._inventory_slots[slot_index].remove_amount(count)
            if result is not None:
                self._organize_inventory_slots()
                return result
        return None

    def add_coins(self, amount: int):
        self._coins += amount
    
    def remove_coins(self, amount: int):
        if amount > self._coins:
            return None
        self._coins -= amount
        return self._coins

    def get_inventory_slots(self):
        return self._inventory_slots

    def get_coins(self):
        return self._coins


class InventoryButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=item_index)
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()


class InventorySellButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()} [{item.get_value_str()} each]", row=item_index)
        self._item = item
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view

        if view.get_user() == interaction.user:
            response = view.sell_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class InventoryMailButton(discord.ui.Button):
    def __init__(self, item_index: int, page: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=item_index)
        self._item = item
        self._item_index = item_index
        self._page = page

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
                self._item_index,
                self._item * self._page,
                view,
                interaction.message.id)
            )


# Could abstract into a generic button with some callback in the parent view?
class NextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        # TODO: Add type hint to this. Need to abstract view class with next/prev callbacks.
        view = self.view
        if interaction.user == view.get_user():
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        # TODO: Add type hint to this. Need to abstract view class with next/prev callbacks.
        view = self.view
        if interaction.user == view.get_user():
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class InventoryView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 4

        self._get_current_page_buttons()

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(5))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(5))
        
    def _get_current_page_info(self):
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        coins = player.get_inventory().get_coins()
        return embeds.Embed(
            title=f"{self._user.display_name}'s Inventory",
            description=f"You have {coins} coins.\n\nNavigate through your items using the Prev and Next buttons."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# MARKET SYSTEM
# -----------------------------------------------------------------------------

class MarketSellButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Sell")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            response = view.enter_sell_market()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 4
        
        self._display_initial_buttons()

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventorySellButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(5, len(page_slots))))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(min(5, len(page_slots))))
        self.add_item(MarketExitButton(min(5, len(page_slots))))
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

        return embeds.Embed(
            title="Selling at the Market",
            description="Choose an item from your inventory to sell!"
        )

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

        return embeds.Embed(
            title="Selling at the Market",
            description="Choose an item from your inventory to sell!"
        )

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(MarketSellButton())

    def enter_sell_market(self):
        self._get_current_page_buttons()
        
        return embeds.Embed(
            title="Selling at the Market",
            description="Choose an item from your inventory to sell!"
        )

    def sell_item(self, item_index: int, item: Item):
        # TODO: Rather than selling one at a time, create a modal that'll let you choose
        # how many to sell!
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        inventory = player.get_inventory()
        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        embed = embeds.Embed(
            title="Selling at the Market",
            description="Choose an item from your inventory to sell!\n\n*Error: That item couldn't be sold.*"
        )

        adjusted_index = item_index * (self._page + 1)
        found_index = inventory.item_exists(item)
        if found_index == adjusted_index:
            inventory.remove_item(item_index, 1)
            inventory.add_coins(item.get_value())
            embed = embeds.Embed(
                title="Selling at the Market",
                description=f"Choose an item from your inventory to sell!\n\n*Sold 1 {item.get_full_name()} for {item.get_value_str()}!*"
            )
        
        self._get_current_page_buttons()
        return embed
    
    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return embeds.Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# STATS
# -----------------------------------------------------------------------------

# Based on the command names; the user will do b!stats [name] or omit the name
# and get all of them at once.
class StatNames(Enum):
    Fish = "fish"
    Mail = "mail"
    Market = "market"
    Knucklebones = "knucklebones"
    Inventory = "inventory"

    @classmethod
    def values(self):
        return list(map(lambda stat_key: stat_key.value, self))

    @classmethod
    def search(self, name: str):
        try:
            return self.values().index(name.lower())
        except:
            return -1


class StatView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User, specific_stat: StatNames=None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._specific_stat = specific_stat
        self._page = 0

        self._STAT_ENUM_VALUES_LIST = StatNames.values()

        if specific_stat is None:
            self.add_item(PrevButton(0))
            self.add_item(NextButton(0))

    def get_current_page_info(self):
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        stat_enum_value: str = ""
        if self._specific_stat is not None:
            stat_enum_value = self._specific_stat
        else:
            stat_enum_value = self._STAT_ENUM_VALUES_LIST[self._page]
        stats_for_page: dict = player.get_stats()[stat_enum_value]

        title = stat_enum_value.capitalize()
        page_str = f"({self._page + 1}/{len(self._STAT_ENUM_VALUES_LIST)})"
        description = ""
        for name, value in enumerate(stats_for_page):
            description += f"**{name}**: {str(value)}\n"
        # Using "timestamp" as a way to communicate the current page to the user
        return embeds.Embed(title=title, description=description, timestamp=page_str)

    def next_page(self):
        self._page = (self._page + 1) % len(StatNames)
        return self.get_current_page_info()

    def prev_page(self):
        self._page = (self._page - 1) % len(StatNames)
        return self.get_current_page_info()

# -----------------------------------------------------------------------------
# EXPERTISE
# -----------------------------------------------------------------------------

# Expertise is similar to a class system in RPG games, such as being able to
# level Illusion magic in Skyrim or level cooking in WoW. While somewhat related
# to stats, it's going to be a separate system, since it's abstracted away from
# individual actions. I may rely on values in stats to contribute to leveling
# or I may pick and choose certain actions to level a class.

# If I need to change something, always change the enum key
# never the value, since I use the values to store data.
class ExpertiseCategoryNames(Enum):
    Fisher = "Fishing"
    Merchant = "Merchant"


class Expertise():
    def __init__(self):
        self._xp: int = 0
        self._level: int = 0

    # Could be positive or negative, regardless don't go below 0.
    def add_xp(self, value: int):
        self._xp = max(0, self._xp + value)

    def get_xp(self):
        return self._xp

    def get_level(self):
        return self._level

    def get_xp_remaining_to_next_level(self):
        # TODO: Figure out good function here based on XP awarded
        # for tasks. Probably something linear?
        return self._level * 25

# -----------------------------------------------------------------------------
# MAIL SYSTEM
# -----------------------------------------------------------------------------

class Mail():
    def __init__(self, sender_name: str, item: Item, coins: int, message: str, send_date: str):
        self._sender_name = sender_name
        self._item = item
        self._message = message
        self._send_date = send_date
        self._coins = coins

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

    def __eq__(self, obj):
        if not isinstance(obj, Mail):
            return False

        if self._sender_name == obj.get_sender_name() and self._item == obj.get_item() \
            and self._message == obj.get_message() and self._send_date == obj.get_send_date() \
            and self._coins == obj.get_coins():
            return True

        return False


class MailView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, giftee: User, context: commands.Context):
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

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryMailButton(i, self._page, item))
        if self._page != 0:
            self.add_item(PrevButton(5))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(5))
        
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
    def __init__(self, database: dict, guild_id: int, user: User, giftee: User, item_index: int, item: Item, view: MailView, message_id: int):
        super().__init__(title=f"Mailing a gift to {giftee.display_name}!")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._giftee = giftee
        self._item_index = item_index
        self._item = item
        self._view = view
        self._message_id = message_id

        self._count_input = discord.ui.TextInput(
            label="Quantity",
            default="1",
        )
        self.add_item(self._count_input)

        self._coins_input = discord.ui.TextInput(
            label="Coins",
            default="0"
        )
        self.add_item(self._coins_input)

        self._message_input = discord.ui.TextInput(
            label="Message",
            required=False,
            style=discord.TextStyle.paragraph,
            placeholder="Anything you'd like to say?"
        )
        self.add_item(self._message_input)

    async def on_submit(self, interaction: discord.Interaction):
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        giftee_player: Player = self._database[self._guild_id]["members"][self._giftee.id]
        inventory = player.get_inventory()
        
        found_index = inventory.item_exists(self._item)
        if found_index != self._item_index:
            await interaction.response.send_message(f"Error: Something about your inventory changed. Try using !mail again.")
            return

        if not self._count_input.value.isnumeric() or int(self._count_input.value) <= 0:
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

        sent_item = inventory.remove_item(self._item_index, int(self._count_input.value))
        sent_coins = inventory.remove_coins(int(self._coins_input.value))
        mail = Mail(self._user.display_name, sent_item, sent_coins, self._message_input.value, str(time.time()).split(".")[0]) 
        giftee_player.get_mailbox().append(mail)
        
        if sent_coins > 0:
            coin_str = "coin" if int(self._coins_input.value) == 1 else "coins"
            await interaction.response.send_message(f"You mailed {int(self._count_input.value)} {sent_item.get_full_name()} and {sent_coins} {coin_str} to {self._giftee.display_name}!")
        else:
            await interaction.response.send_message(f"You mailed {int(self._count_input.value)} {sent_item.get_full_name()} to {self._giftee.display_name}!")
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

                mail_message = f"From: {self._mail.get_sender_name()} (<t:{self._mail.get_send_date()}:R>)"
                mail_message += f"\n\nItem: {self._mail.get_item().get_full_name_and_count()} each worth {self._mail.get_item().get_value_str()}"
                if self._mail.get_coins() > 0:
                    mail_message += f"\n\nCoins: {self._mail.get_coins()}"
                if self._mail.get_message() != "":
                    mail_message += f"\n\nMessage:\n\n{self._mail.get_message()}"

                await interaction.followup.send(content=mail_message, ephemeral=True)
            else:
                embed = view.get_current_page_info()
                embed.description += "\n\n*Error: That mail is no longer available.*"
                await interaction.response.edit_message(content=None, embed=embed, view=view)


class MailboxView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        # These buttons are going to descend vertically. Thinking about changing the
        # inventory to be the same since it looks better on mobile too.
        self._NUM_PER_PAGE = 4
        
        self._get_current_page_buttons()

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        mailbox: List[Mail] = player.get_mailbox()

        page_slots = mailbox[self._page * self._NUM_PER_PAGE:min(len(mailbox), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(MailboxButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(5, len(page_slots))))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(min(5, len(page_slots))))
        
    def get_current_page_info(self):
        return embeds.Embed(
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
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        inventory: Inventory = player.get_inventory()
        mailbox: List[Mail] = player.get_mailbox()

        if mail_index >= len(mailbox):
            self._get_current_page_buttons()
            return False
        
        adjusted_index = mail_index * (self._page + 1)
        found_index = self._mail_exists(mailbox, mail)
        if found_index != adjusted_index:
            self._get_current_page_buttons()
            return False

        mailbox_mail = mailbox.pop(mail_index)
        inventory.add_item(mailbox_mail.get_item())
        inventory.add_coins(mailbox_mail.get_coins())

        self._get_current_page_buttons()
        return True

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# PLAYER
# -----------------------------------------------------------------------------

class Player():
    def __init__(self):
        self._inventory = Inventory()
        self._expertise: dict[str, Expertise] = {item.value: Expertise() for item in ExpertiseCategoryNames}
        self._mailbox: List[Mail] = []
        self._stats: dict[str, dict[str, Union[str, int, bool, float]]] = {}

    def get_inventory(self):
        return self._inventory

    def get_expertise(self):
        return self._expertise
    
    def get_mailbox(self):
        return self._mailbox

    def get_stat_category(self, category_name: StatNames, stat_name: str, init_value: Union[str, int, bool, float]):
        if self._stats.get(category_name) is None:
            self._stats[category_name] = {}
        if self._stats[category_name].get(stat_name) is None:
            self._stats[category_name][stat_name] = init_value
        return self._stats[category_name]

    def get_stats(self):
        return self._stats

# -----------------------------------------------------------------------------
# COMMAND HANDLERS
# -----------------------------------------------------------------------------

class Adventures(commands.Cog):
    def __init__(self, bot: BenjaminBowtieBot):
        self._bot = bot
        # Database is here due to a pickle issue with importing from this module at the bot level
        self._database: dict = dill.load(open("./adventuresdb", "rb")) if os.path.isfile("./adventuresdb") else {}
        
        self.save_database.start()

    def _check_member_and_guild_existence(self, guild_id: int, user_id: int):
        if self._database.get(guild_id) is None:
            self._database[guild_id] = {}
            self._database[guild_id]["members"] = {}
        
        if self._database[guild_id]["members"].get(user_id) is None:
            self._database[guild_id]["members"][user_id] = Player()

    @tasks.loop(hours=1)
    async def save_database(self):
        if os.path.isfile("./adventuresdb"):
            shutil.copy("adventuresdb", "adventuresdbbackup")
        
        dill.dump(self._database, open("adventuresdb", "wb"))

    @commands.command(name="fish", help="Begins a fishing minigame to catch fish and mysterious items")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fish_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()
        fishing_result:Item = None
        # tier_of_result:int = 4

        # 55% chance of getting a Tier 4 reward
        if 0.0 <= rand_val < 0.55:
            # tier_of_result = 4
            items = [Item("🥾", "Boot", 2), Item("🍂", "Clump of Leaves", 1), Item("🐚", "Conch", 1)]
            fishing_result = random.choice(items)
        # 20% chance of getting a Tier 3 reward
        if 0.55 < rand_val < 0.75:
            # tier_of_result = 3
            items = [Item("🐟", "Minnow", 3), Item("🐠", "Roughy", 4), Item("🦐", "Shrimp", 3)]
            fishing_result = random.choice(items)
        # 15% chance of getting a Tier 2 reward
        if 0.75 < rand_val < 0.9:
            # tier_of_result = 2
            items = [Item("🦪", "Oyster", 4), Item("🐡", "Pufferfish", 5)]
            fishing_result = random.choice(items)
        # 9% chance of getting a Tier 1 reward
        if 0.9 < rand_val < 0.99:
            # tier_of_result = 1
            items = [Item("🦑", "Squid", 10), Item("🦀", "Crab", 8), Item("🦞", "Lobster", 8), Item("🦈", "Shark", 10)]
            fishing_result = random.choice(items)
        # 1% chance of getting a Tier 0 reward
        if 0.99 < rand_val <= 1.0:
            # tier_of_result = 0
            items = [Item("🏺", "Ancient Vase", 40), Item("💎", "Diamond", 50), Item("📜", "Mysterious Scroll", 30)]
            fishing_result = random.choice(items)
        
        # E(X) = 
        # 0.55 * (2 + 1 + 1) / 3 + 
        # 0.2 * (3 + 4 + 3) / 3 + 
        # 0.15 * (4 + 5) / 2 + 
        # 0.09 * (10 + 8 + 8) / 3 + 
        # 0.01 * (25 + 50) / 2 = 
        # 3.23 every 30 seconds -> 387.6 an hour
        
        author_player: Player = self._database[context.guild.id]["members"][context.author.id]
        author_player.get_inventory().add_item(fishing_result)

        # author_player.get_stat_category(StatNames.Fish, f"Tier {str(tier_of_result)} Caught", 0)[f"Tier {str(tier_of_result)} Caught"] += 1

        embed = embeds.Embed(
            title=f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}!",
            description="It's been added to your b!inventory"
        )
        await context.send(embed=embed)

    @commands.command(name="knucklebones", help="Face another player in a game of knucklebones")
    async def knucklebones_handler(self, context: commands.Context, user: User=None, amount: int=0):
        if user is None:
            await context.send("You need to @ a member to use b!knucklebones")
            return

        if user == context.author:
            await context.send("You can't challenge yourself to a game of knucklebones")
            return
            
        if user.bot:
            await context.send("You can't challenge a bot to knucklebones (but Benjamin Bowtie might learn how to play one day!)")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        self._check_member_and_guild_existence(context.guild.id, user.id)

        if amount < 0:
            await context.send(f"You have to bet a non-negative number of coins!")
            return

        # I don't think I need to keep track of the games in the database, since each message
        # will update itself as buttons are pressed becoming a self-contained game. So long as (1)
        # we check that the players pressing the buttons are valid which should happen naturally
        # based on turn checks; (2) when paying out we check that the player has the money to do
        # so, else the winner gets whatever's left that the other can pay.
        author_player: Player = self._database[context.guild.id]["members"][context.author.id] 
        challenged_player: Player = self._database[context.guild.id]["members"][user.id]
        if author_player.get_inventory().get_coins() < amount:
            await context.send(f"You don't have enough coins ({author_player.get_inventory().get_coins()}) to bet that much!")
            return
        if challenged_player.get_inventory().get_coins() < amount:
            await context.send(f"That person doesn't have enough coins ({challenged_player.get_inventory().get_coins()}) to bet that much!")
            return

        embed = embeds.Embed(
            title="Welcome to Knucklebones!",
            description="Players will take alternating turns rolling dice. They will then choose a column in which to place the die result.\n\n\
                        If the opponent has dice of the same value in that same column, those dice are removed from their board.\n\n\
                        Two of the same die in a single column double their value. Three of the same die triple their value.\n\n\
                        When one player fills their board with dice, the game is over. The player with the most points wins.\n\n\
                        The game will begin when the other player accepts the invitation to play."
        )

        await context.send(embed=embed, view=Knucklebones(self._bot, self._database, context.guild.id, context.author, user, amount))

    @commands.command(name="mail", help="Send another player a gift")
    async def mail_handler(self, context: commands.Context, giftee: User=None):
        if giftee is None:
            await context.send("You need to @ a member to use !mail")
            return
        
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        self._check_member_and_guild_existence(context.guild.id, giftee.id)
        # The process will be:
        # (1) The user gets to select an item (as a button) from their inventory
        #     There will be 5 items in a row (4 rows of that), along with a 
        #     prev and next button to navigate on the final row
        # (2) Upon clicking a button, a modal will pop up asking how many to send and
        #     an optional message to send
        player: Player = self._database[context.guild.id]["members"][context.author.id]
        coins = player.get_inventory().get_coins()
        embed = embeds.Embed(
            title=f"{context.author.display_name}'s Inventory",
            description=f"You have {coins} coins.\n\nChoose an item to mail to {giftee.display_name}!"
        )
        await context.send(embed=embed, view=MailView(self._bot, self._database, giftee, context))

    @commands.command(name="inventory", help="Check your inventory", aliases=["inv"])
    async def inventory_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        player: Player = self._database[context.guild.id]["members"][context.author.id]
        coins = player.get_inventory().get_coins()
        embed = embeds.Embed(
            title=f"{context.author.display_name}'s Inventory",
            description=f"You have {coins} coins.\n\nNavigate through your items using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=InventoryView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="market", help="Sell and buy items at the marketplace", aliases=["marketplace"])
    async def market_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = embeds.Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )
        await context.send(embed=embed, view=MarketView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="mailbox", help="Open mail you've received from others", aliases=["inbox"])
    async def mailbox_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = embeds.Embed(
            title=f"{context.author.display_name}'s Mailbox",
            description=f"Navigate through your mail using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=MailboxView(self._bot, self._database, context.guild.id, context.author))

    @commands.is_owner()
    @commands.command(name="saveadventures", help="Saves the adventures database")
    async def save_adventures_handler(self, context: commands.Context):
        await self.save_database()
        await context.send("The adventures database has been saved!")


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
