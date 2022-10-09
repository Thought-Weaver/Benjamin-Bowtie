from __future__ import annotations
from random import choice

import discord

from discord import Embed
from discord.ext import tasks
from features.expertise import ExpertiseClass
from features.npcs.npc import NPC, NPCRoles
from features.shared.ability import BoundToGetLuckyIII, ContractManaToBloodIII, ContractWealthForPowerIII, EmpowermentI, IncenseIII, ParalyzingFumesI, PreparePotionsIII, QuickAccessI, RegenerationIII, SecondWindI, SilkspeakingI, VitalityTransferIII
from features.shared.item import LOADED_ITEMS, ClassTag, Item, ItemKey
from strenum import StrEnum

from typing import TYPE_CHECKING, List
from features.shared.nextbutton import NextButton

from features.shared.prevbutton import PrevButton
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# MODALS
# -----------------------------------------------------------------------------

class PurchaseModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, item: Item, view: YennaView, message_id: int):
        super().__init__(title=f"Purchase {item.get_full_name()}")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._item = item
        self._view = view
        self._message_id = message_id

        # TODO: Small problem: I don't have a way of displaying the total cost to the user
        # since there's no callback on the text input value changing.
        self._count_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Quantity",
            default="1",
            required=True
        )
        self.add_item(self._count_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        pass

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Identify = "Identify"
    Tarot = "Tarot"


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterIdentifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Identify Items", row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_identify()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterTarotButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Tarot Reading", row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_tarot()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view

        if view.get_user() == interaction.user:
            response = view.return_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WaresDisplayButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class IdentifyDisplayButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.select_identify_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: YennaView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class YennaView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._yenna: Yenna = database[str(guild_id)]["npcs"][NPCRoles.FortuneTeller]
        self._wares: List[Item] = []
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items
        self._IDENTIFY_COST = 50 # Fixed at 50 coins for right now
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(
            title="Madame Yenna's Tent",
            description=(
                "In the bustling village market stands an unusual tent, covered in a patterned red, gold, and purple fabric. "
                "Stepping inside, the daylight suddenly disperses and shadow engulfs you. Your eyes adjust to the dim interior, oddly larger than it appeared from the outside. "
                "A flickering light passes across the shadows cast by the setup in front of you: Dark wooden chairs, one near you and another on the opposite side of a rectangular table hewn of the same wood. "
                "The table has white wax candles on either side, illuminating tarot cards, potions, herbs, and various occult implements that belong to the figure hidden in the shadows beyond the table's edge.\n\n"
                "\"Matters of fate and destiny are often complex,\" she says, moving closer to the light, though you remain unable to see the upper half of her face. \"What can I do to aid your journey?\""
            )
        )

    def show_initial_buttons(self):
        self.clear_items()

        self.add_item(EnterWaresButton())
        self.add_item(EnterIdentifyButton())
        self.add_item(EnterTarotButton())

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Looking to procure something for what lies ahead? I have herbs, potions, and scrolls -- all of which I'm willing to part with for a reasonable fee.\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Identify:
            return Embed(
                title="Identify Item",
                description=(
                    "\"The mysteries of this world can often be a challenge to unravel. Let's see the truth hidden within.\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Tarot:
            pass
        return self.get_initial_embed()

    def display_item_info(self):
        player: Player = self._get_player()
        if self._selected_item is None or not (0 <= self._selected_item_index < len(self._wares) and self._wares[self._selected_item_index] == self._selected_item):
            self._get_wares_page_buttons()
            return Embed(
                title="Browse Wares",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available wares using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_item.get_value() * self._COST_ADJUST)
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"──────────\n{self._selected_item}\nPrice: {actual_cost_str}\n──────────\n\n"
                "Navigate through available wares using the Prev and Next buttons."
            )
        )

    def select_wares_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index
        return self.display_item_info()

    def _get_wares_page_buttons(self):
        self.clear_items()
        all_slots = self._wares

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(WaresDisplayButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item is not None:
            self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        if self._selected_item is not None and self._wares[self._selected_item_index] == self._selected_item:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST)
            if inventory.get_coins() < actual_value:
                inventory.remove_coins(actual_value)
                inventory.add_item(LOADED_ITEMS.get_new_item(self._selected_item.get_key()))
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*You purchased 1 {self._selected_item.get_full_name()}!*"
                    )
                )

        self._get_wares_page_buttons()
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available wares using the Prev and Next buttons.\n\n"
                "*Error: Something about that item changed or it's no longer available.*"
            )
        )

    def enter_wares(self):
        self._intent = Intent.Wares
        self._get_wares_page_buttons()
        return self.get_embed_for_intent()

    def display_identify_info(self):
        player: Player = self._get_player()
        all_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or not (0 <= self._selected_item_index < len(all_slots) and all_slots[self._selected_item_index] == self._selected_item):
            self._get_wares_page_buttons()
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        return Embed(
            title="Identify Item",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"──────────\n**{self._selected_item.get_full_name()}**\n*{self._selected_item.get_rarity()} Item*\n\nIdentification Cost: {self._IDENTIFY_COST}\n──────────\n\n"
                "Navigate through your items using the Prev and Next buttons."
            )
        )

    def select_identify_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index
        return self.display_item_info()

    def _get_identify_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Misc.NeedsIdentification])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(WaresDisplayButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item is not None:
            self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _identify_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        if self._selected_item is None or self._wares[self._selected_item_index] != self._selected_item:
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {inventory.get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        if inventory.get_coins() < self._IDENTIFY_COST:
            return Embed(
                title="Identify Item",
                description=(
                    f"You have {inventory.get_coins_str()}.\n\n"
                    "Navigate through your items using the Prev and Next buttons.\n\n"
                    f"*You don't have the coins needed ({self._IDENTIFY_COST}) to identify this item.*" 
                )
            )

        if ClassTag.Equipment.Equipment in self._selected_item.get_class_tags():
            # TODO: Implement this when random items based on rarity happens
            # inventory.remove_coins(self._IDENTIFY_COST)
            # inventory.remove_item(self._selected_item_index)
            # Then add a new item randomly generated based on the selected item's rarity
            pass
        
        if self._selected_item.get_key() == ItemKey.MysteriousScroll:
            return self._yenna.identify_scroll(player, self._selected_item_index, self._user.display_name, self._IDENTIFY_COST)

        if self._selected_item.get_key() == ItemKey.FishMaybe:
            return self._yenna.identify_fish_maybe(player, self._selected_item_index, self._IDENTIFY_COST)

        return Embed(
            title="Identify Item",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through your items using the Prev and Next buttons.\n\n"
                "\"Strange... I can't make sense of this item at all. Perhaps let's try a different one.\""
            )
        )

    def enter_identify(self):
        self._intent = Intent.Identify
        self._get_identify_page_buttons()
        return self.get_embed_for_intent()

    def _tarot_reading(self):
        # TODO: Implement this based on player's expertise and suggest an alternative, then reset points.
        pass

    def enter_tarot(self):
        self.clear_items()
        self._intent = Intent.Tarot
        self.add_item(ConfirmButton(0))
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            return self._purchase_item()
        if self._intent == Intent.Identify:
            return self._identify_item()
        if self._intent == Intent.Tarot:
            return self._tarot_reading()
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        self._selected_item = None
        self._selected_item_index = -1

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        self._selected_item = None
        self._selected_item_index = -1

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Yenna(NPC):
    def __init__(self):
        super().__init__("Yenna", NPCRoles.FortuneTeller)

        # Inventory Setup
        self._restock_items = []
        self._restock_coins = 5000

        self._inventory.add_coins(self._restock_coins)
        for item in self._restock_items:
            self._inventory.add_item(item)
        
        # Expertise Setup
        # TODO: When Alchemy is implemented, add XP to that class to get to Level 50
        self._expertise.add_xp_to_class(96600, ExpertiseClass.Merchant) # Level 20
        self._expertise.add_xp_to_class(1600, ExpertiseClass.Guardian) # Level 5
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 10
        self._expertise.intelligence = 30
        self._expertise.dexterity = 10
        self._expertise.strength = 3
        self._expertise.luck = 10
        self._expertise.memory = 12

        # Equipment Setup
        # TODO: Add items when they've been created
        # self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, None)

        self._expertise.update_stats(self._equipment.get_total_buffs())

        # Dueling Setup
        # TODO: Also add fate-bending abilities
        self._dueling.abilities = [
            BoundToGetLuckyIII(), SecondWindI(), SilkspeakingI(),
            ParalyzingFumesI(), RegenerationIII(), QuickAccessI(),
            PreparePotionsIII(), VitalityTransferIII(), EmpowermentI(),
            IncenseIII(), ContractManaToBloodIII(), ContractWealthForPowerIII()
        ]

        # Story Variables
        self._scroll_text: str = ""
        self._words_identified: List[str] = []
        self._last_to_identify_scroll: str = ""
        self._num_fish_maybe_identified: int = 0
        self._NUM_FISH_PER_RESULT: int = 3

    @tasks.loop(hours=24)
    async def restock(self):
        # At the moment, just restock coins in anticipation of being involved in duels or potentially for
        # using for a more realistic economy. Sold items are being managed by the view rather than the NPC
        # entity -- the items in her inventory are basically just for duels.
        coins_to_restock: int = max(0, self._restock_coins - self._inventory.get_coins())
        self._inventory.add_coins(coins_to_restock)

    def identify_scroll(self, player: Player, selected_item_index: int, display_name: str, identify_cost: int):
        inventory = player.get_inventory()

        word_set = set(self._scroll_text.replace(".", "").replace(",", "").replace("!", "").split(" "))
        found_words = set(self._words_identified)
        words_remaining = word_set - found_words
        
        if len(words_remaining) == 0:
            inventory.add_coins(60)
            inventory.remove_item(selected_item_index)
            return Embed(
                title="A Mysterious Scroll",
                description=(
                    "\"Ah, another one of these scrolls. It looks like there's nothing more I can glean from the text. The final message is:\"\n\n"
                    f"{self._scroll_text}\n\n"
                    "However, allow me to offer compensation at least for trusting the scroll to me.\"\n\n"
                    "*You received 60 coins.*"
                )
            )
        
        random_word: str = choice(list(words_remaining))
        self._words_identified.append(random_word)
        found_words.add(random_word)
        words_remaining = word_set - found_words
        
        result_text = self._scroll_text
        for word in words_remaining:
            result_text.replace(word, "▮" * len(word))

        last_to_identify_str = ""
        if display_name == self._last_to_identify_scroll:
            last_to_identify_str = f"\"Another one, {display_name}? You have a propensity for acquiring unusual items it seems. With time and effort, I anticipate we'll decipher all there is to know here.\""
        else:
            last_to_identify_str = f"\"Another one? {self._last_to_identify_scroll} also brought me one before... With time and effort, I anticipate we'll decipher all there is to know here.\"" if self._last_to_identify_scroll != "" else ""
        
        inventory.remove_coins(identify_cost)
        inventory.remove_item(selected_item_index)
        return Embed(
            title="A Mysterious Scroll",
            description=(
                f"{last_to_identify_str}\n\n"
                "*Reaching out past the firelight, Yenna takes the scroll from your hands and unrolls it onto the table.*\n\n"
                "\"This scroll is degrading -- not from being previously submerged in water, but perhaps due to its exposure to air? The parchment is some kind of pulped kelp, dyed made to look like the off-white coloration I'd typically expect in a scroll of this design. "
                "There are words written here, but they're more like a failed attempt to write the Common tongue with some borrowed elements from other languages and more still I don't recognize. I might be able to make some sense of them...\"\n\n"
                "*Yenna pours over the scroll for hours, comparing to her books and other texts in an effort to understand it. Eventually, the parchment begins to fully fall apart in the warm light.*\n\n"
                "Here's what I have for you:\n\n"
                f"{result_text}"
            )
        )

    def identify_fish_maybe(self, player: Player, selected_item_index: int, identify_cost: int):
        inventory = player.get_inventory()

        inventory.remove_coins(identify_cost)
        inventory.remove_item(selected_item_index)

        if self._num_fish_maybe_identified % self._NUM_FISH_PER_RESULT == 0:
            self._num_fish_maybe_identified += 1

            result_num: int = int(self._num_fish_maybe_identified / self._NUM_FISH_PER_RESULT)
            if result_num == 0:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
            if result_num == 1:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
            if result_num == 2:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
            if result_num == 3:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
            if result_num == 4:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
            if result_num == 5:
                return Embed(title="A Fish?",
                    description=(
                        ""
                    )
                )
        else:
            self._num_fish_maybe_identified += 1
            
            return Embed(title="A Fish?",
                description=(
                    ""
                )
            )
