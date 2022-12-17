from __future__ import annotations
import random
from uuid import uuid4

import discord

from discord import Embed
from strenum import StrEnum
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import BoundToGetLuckyIII, ContractWealthForPowerIII, PreparePotionsII, SilkspeakingI
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, Item, ItemKey, Rarity
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.stats import Stats

from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

MAX_PURCHASABLE_THIS_TICK = 10

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RandomItemMerchantView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RandomItemMerchantView = self.view

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
        
        view: RandomItemMerchantView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RandomItemMerchantView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RandomItemMerchantView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._random_item_merchant: RandomItemMerchant = database[str(guild_id)]["npcs"][NPCRoles.RandomItemMerchant]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        random_word = random.choice(["windmill", "horse", "dagger", "seaclover", "shoe", "tankard", "squid", "crab", "fish cake", "miniature version of the village", "snowdew flower", "ball of yarn", "coin", "crystal vial"])
        return Embed(
            title="Viktor's Hovel",
            description=(
                "A bit outside town, in what some may describe as a modest living space and others a hole in a hillside, lives a rather eccentric character known for somehow procuring all manner of strange goods.\n\n"
                f"Viktor opens the makeshift wooden door as you approach, beckoning you inside with hasty gestures and a candle shaped like a {random_word}.\n\n"
                "There seems to be no organization to anything in the hovel, with items piled high on top of each other in a mountain of chaos. Viktor walks back behind a wooden plank which you can only assume is intended as a checkout counter."
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton())

    def get_embed_for_intent(self):
        player: Player = self._get_player()

        items_remaining: int = MAX_PURCHASABLE_THIS_TICK - self._random_item_merchant.get_purchased_this_tick(str(self._user.id))
        item_str = "items" if items_remaining != 1 else "item"

        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"I have MANY THINGS!\" he says pointing to all the various things.\n\n"
                    f"You have {player.get_inventory().get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour."
                )
            )
        return self.get_initial_embed()

    def display_item_info(self):
        player: Player = self._get_player()
        wares: List[Item] = self._random_item_merchant.get_current_wares()

        items_remaining: int = MAX_PURCHASABLE_THIS_TICK - self._random_item_merchant.get_purchased_this_tick(str(self._user.id))
        item_str = "items" if items_remaining != 1 else "item"

        if self._selected_item is None or not (0 <= self._selected_item_index < len(wares) and wares[self._selected_item_index] == self._selected_item):
            self._get_wares_page_buttons()
            
            return Embed(
                title="Browse Wares",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour.\n\n"
                    "Navigate through available wares using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        # Add 1 to account for low-cost items and avoid free XP/coin exploits
        actual_cost: int = int(self._selected_item.get_value() * self._random_item_merchant.get_cost_adjust()) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {player.get_inventory().get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through available wares using the Prev and Next buttons."
            )
        )

    def select_wares_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_wares_page_buttons()
        return self.display_item_info()

    def _get_wares_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        all_slots = self._random_item_merchant.get_current_wares()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(WaresDisplayButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            actual_value: int = int(self._selected_item.get_value() * self._random_item_merchant.get_cost_adjust()) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        wares: List[Item] = self._random_item_merchant.get_current_wares()

        if self._random_item_merchant.get_purchased_this_tick(str(self._user.id)) >= MAX_PURCHASABLE_THIS_TICK:
            return Embed(
                title="Browse Wares",
                description=(
                    f"You have {inventory.get_coins_str()}.\n\n"
                    "Navigate through available wares using the Prev and Next buttons.\n\n"
                    "*You can't purchase any more items from Viktor this hour!*"
                )
            )

        items_remaining: int = MAX_PURCHASABLE_THIS_TICK - self._random_item_merchant.get_purchased_this_tick(str(self._user.id))
        item_str = "items" if items_remaining != 1 else "item"

        if self._selected_item is not None and wares[self._selected_item_index] == self._selected_item:
            actual_value: int = int(self._selected_item.get_value() * self._random_item_merchant.get_cost_adjust()) + 1
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                inventory.add_item(LOADED_ITEMS.get_new_item(self._selected_item.get_key()))
                self._get_wares_page_buttons()

                self._random_item_merchant.add_purchased_this_tick(str(self._user.id))
                items_remaining: int = MAX_PURCHASABLE_THIS_TICK - self._random_item_merchant.get_purchased_this_tick(str(self._user.id))
                item_str = "items" if items_remaining != 1 else "item"

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*You purchased 1 {self._selected_item.get_full_name()}!*"
                    )
                )
            else:
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to buy that!*"
                    )
                )

        self._get_wares_page_buttons()
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {inventory.get_coins_str()}. You can purchase {items_remaining} more {item_str} this hour.\n\n"
                "Navigate through available wares using the Prev and Next buttons.\n\n"
                "*Error: Something about that item changed or it's no longer available.*"
            )
        )

    def enter_wares(self):
        self._intent = Intent.Wares
        self._get_wares_page_buttons()
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._get_wares_page_buttons()

            return result
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

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

class RandomItemMerchant(NPC):
    def __init__(self):
        super().__init__("Viktor", NPCRoles.RandomItemMerchant, NPCDuelingPersonas.Rogue, {})

        self._setup_npc_params()

    def tick(self):
        possible_items = list(filter(lambda x: x.get_rarity() < Rarity.Artifact, [LOADED_ITEMS.get_new_item(key) for key in ItemKey]))
        prob_map: Dict[Rarity, float] = {
            Rarity.Common: 0.7,
            Rarity.Uncommon: 0.22,
            Rarity.Rare: 0.055,
            Rarity.Epic: 0.02,
            Rarity.Legendary: 0.005,
            Rarity.Artifact: 0,
            Rarity.Unknown: 0
        }
        weights = [prob_map[item.get_rarity()] for item in possible_items]
        new_items = random.choices(possible_items, k=8, weights=weights)
        
        self._current_wares = new_items
        self._cost_adjust = random.randint(125, 225) / 100.0
        self._purchased_this_tick: Dict[str, int] = {}

    def _setup_inventory(self):
        self.tick()

        if self._inventory is None:
            self._inventory = Inventory()

        health_potions = LOADED_ITEMS.get_new_item(ItemKey.HealthPotion)
        health_potions.add_amount(2)
        sapping_potions = LOADED_ITEMS.get_new_item(ItemKey.SappingPotion)
        sapping_potions.add_amount(1)
        greater_dex_potion = LOADED_ITEMS.get_new_item(ItemKey.GreaterDexterityPotion)
        luck_potion = LOADED_ITEMS.get_new_item(ItemKey.LuckPotion)

        self._inventory.add_item(health_potions)
        self._inventory.add_item(sapping_potions)
        self._inventory.add_item(greater_dex_potion)
        self._inventory.add_item(luck_potion)

    def get_current_wares(self):
        return self._current_wares
    
    def get_cost_adjust(self):
        return self._cost_adjust

    def add_purchased_this_tick(self, id_str: str):
        self._purchased_this_tick[id_str] = self._purchased_this_tick.get(id_str, 0) + 1

    def get_purchased_this_tick(self, id_str: str):
        return self._purchased_this_tick.get(id_str, 0)

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise.add_xp_to_class(1750, ExpertiseClass.Merchant, self._equipment) # Level 10
        self._expertise.add_xp_to_class(600, ExpertiseClass.Alchemist, self._equipment) # Level 5
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 2
        self._expertise.intelligence = 2
        self._expertise.dexterity = 6
        self._expertise.strength = 0
        self._expertise.luck = 0
        self._expertise.memory = 4

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.IronDagger))

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()

        self._dueling.abilities = [
            ContractWealthForPowerIII(), PreparePotionsII(),
            BoundToGetLuckyIII(), SilkspeakingI()
        ]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Viktor"
        self._role = NPCRoles.RandomItemMerchant
        self._dueling_persona = NPCDuelingPersonas.Rogue
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()
            self._setup_inventory()

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()
            self._setup_equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()
            self._setup_xp()

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()
            self._setup_abilities()

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()

        self._current_wares = state.get("_current_wares", [])
        self._cost_adjust = state.get("_cost_adjust", 1.5)
        self._purchased_this_tick = state.get("_purchased_this_tick", {})
