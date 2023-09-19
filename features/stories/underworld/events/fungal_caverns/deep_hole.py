from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.stories.underworld_room_selection import UnderworldRoomSelectionView
from features.player import Player
from features.shared.item import Rarity
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.shared.statuseffect import ConBuff, ConDebuff, DexBuff, DexDebuff, IntBuff, IntDebuff, LckBuff, LckDebuff, StatusEffect, StrBuff, StrDebuff
from features.stories.dungeon_run import DungeonRun
from enum import StrEnum

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.inventory import Inventory
    from features.shared.item import Item

# -----------------------------------------------------------------------------
# SACRIFICE VIEW
# -----------------------------------------------------------------------------

class SacrificeContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: SacrificeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class SacrificeView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun, item_rarity: Rarity):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        self._item_rarity = item_rarity

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        result_str: str = ""
        ses: List[StatusEffect] = []
        if self._item_rarity in [Rarity.Common, Rarity.Uncommon, Rarity.Cursed]:
            ses = [
                ConDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Deep Hole"
                ),
                StrDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Deep Hole"
                ),
                DexDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Deep Hole"
                ),
                IntDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Deep Hole"
                ),
                LckDebuff(
                    turns_remaining=30,
                    value=-15,
                    source_str="Deep Hole"
                )
            ]
            result_str = "You get a profound sense of displeasure at your offering and your entire party feels something branded onto their very beings."
        elif self._item_rarity == Rarity.Rare:
            ses = [
                ConBuff(
                    turns_remaining=30,
                    value=5,
                    source_str="Deep Hole"
                ),
                StrBuff(
                    turns_remaining=30,
                    value=5,
                    source_str="Deep Hole"
                ),
                DexBuff(
                    turns_remaining=30,
                    value=5,
                    source_str="Deep Hole"
                ),
                IntBuff(
                    turns_remaining=30,
                    value=5,
                    source_str="Deep Hole"
                ),
                LckBuff(
                    turns_remaining=30,
                    value=5,
                    source_str="Deep Hole"
                )
            ]
            result_str = "You feel something sated, for the moment. Some power comes to rest upon you, a minor gesture of gratitude."
        elif self._item_rarity == Rarity.Epic:
            ses = [
                ConBuff(
                    turns_remaining=30,
                    value=10,
                    source_str="Deep Hole"
                ),
                StrBuff(
                    turns_remaining=30,
                    value=10,
                    source_str="Deep Hole"
                ),
                DexBuff(
                    turns_remaining=30,
                    value=10,
                    source_str="Deep Hole"
                ),
                IntBuff(
                    turns_remaining=30,
                    value=10,
                    source_str="Deep Hole"
                ),
                LckBuff(
                    turns_remaining=30,
                    value=10,
                    source_str="Deep Hole"
                )
            ]
            result_str = "You feel something sated, for the moment. Some power comes to rest upon you, a gesture of gratitude."
        elif self._item_rarity == Rarity.Legendary:
            ses = [
                ConBuff(
                    turns_remaining=30,
                    value=15,
                    source_str="Deep Hole"
                ),
                StrBuff(
                    turns_remaining=30,
                    value=15,
                    source_str="Deep Hole"
                ),
                DexBuff(
                    turns_remaining=30,
                    value=15,
                    source_str="Deep Hole"
                ),
                IntBuff(
                    turns_remaining=30,
                    value=15,
                    source_str="Deep Hole"
                ),
                LckBuff(
                    turns_remaining=30,
                    value=15,
                    source_str="Deep Hole"
                )
            ]
            result_str = "You feel something sated, for the moment. Some power stirs within you, a powerful gesture of gratitude."
        elif self._item_rarity == Rarity.Artifact:
            ses = [
                ConBuff(
                    turns_remaining=30,
                    value=20,
                    source_str="Deep Hole"
                ),
                StrBuff(
                    turns_remaining=30,
                    value=20,
                    source_str="Deep Hole"
                ),
                DexBuff(
                    turns_remaining=30,
                    value=20,
                    source_str="Deep Hole"
                ),
                IntBuff(
                    turns_remaining=30,
                    value=20,
                    source_str="Deep Hole"
                ),
                LckBuff(
                    turns_remaining=30,
                    value=20,
                    source_str="Deep Hole"
                )
            ]
            result_str = "You feel something sated, for the moment. A great power stirs within you, a gesture of incredible gratitude."

        for user in self._users:
            player = self._get_player(user.id)
            player.get_dueling().status_effects += ses

        return Embed(title="Down, Down, Down", description=f"As you toss the item in and it sinks into the darkness below...\n\n{result_str}")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(SacrificeContinueButton())

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
# DEEP HOLE VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Sacrifice = "Sacrifice"


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeepHoleView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class EnterSacrificeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Sacrifice")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeepHoleView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return

        if view.get_group_leader().id == interaction.user.id:
            response = view.enter_sacrifice()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectInventoryItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeepHoleView = self.view
        if view.get_group_leader().id == interaction.user.id:
            response = view.select_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Feed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeepHoleView = self.view
        selected_item: Item | None = view._selected_item
        if view.get_group_leader().id == interaction.user.id and selected_item is not None:
            item_rarity: Rarity = selected_item.get_rarity()
            response = view.confirm_item()

            if response is not None:
                await interaction.response.edit_message(content=None, embed=response, view=view)
            else:
                post_view: SacrificeView = SacrificeView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run(), item_rarity)
                initial_info: Embed = post_view.get_initial_embed()

                await interaction.response.edit_message(embed=initial_info, view=post_view, content=None)


class ExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DeepHoleView = self.view
        if view.get_group_leader() == interaction.user:
            embed = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class DeepHoleView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self._intent: Intent | None = None
        self._selected_item: Item | None = None
        self._selected_item_index: int = -1

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="A Deep Hole", description="You begin to pass along a rocky bridge over a long abyss reaching further down than you can see -- or hear as one of you tosses a rock down to see if there's audible contact at the bottom. Almost as though you can hear a voice from below, some whispers call you to throw more in. To give more.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterSacrificeButton())
        self.add_item(ContinueButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def enter_sacrifice(self):
        self._intent = Intent.Sacrifice
        self._get_sacrifice_buttons()
        return self.get_embed_for_intent()

    def _get_sacrifice_buttons(self):
        self.clear_items()
        player: Player = self._get_player(self._group_leader.id)
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        page_slots = inventory_slots[self._page * self._NUM_PER_PAGE:min(len(inventory_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = i + (self._page * self._NUM_PER_PAGE)
            self.add_item(SelectInventoryItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def select_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_sacrifice_buttons()

        player: Player = self._get_player(self._group_leader.id)
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Choose an Item", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def confirm_item(self):
        player: Player = self._get_player(self._group_leader.id)
        inventory: Inventory = player.get_inventory()
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        # Indicates that the operation completed successfully, since there's no follow-up
        return None

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Sacrifice:
            return Embed(
                title="Choose an Item",
                description=(
                    "Choose an item from your inventory to feed it.\n\nNavigate through the items using the Prev and Next buttons."
                    f"{error}"
                )
            )
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Sacrifice:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_sacrifice_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Sacrifice:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_sacrifice_buttons()

        return self.get_embed_for_intent()

    def exit_to_main_menu(self):
        self._intent = None
        self._display_initial_buttons()
        return self.get_initial_embed()

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
    
    def get_players(self):
        return [self._get_player(user.id) for user in self._users]
