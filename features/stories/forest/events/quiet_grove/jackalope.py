from __future__ import annotations

import discord
import features.stories.forest.forest as forest

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.stories.forest_room_selection import ForestRoomSelectionView
from features.views.dueling_view import DuelView
from features.player import Player
from features.shared.enums import ClassTag
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from features.stories.dungeon_run import DungeonRun
from features.stories.forest.combat.npcs.jackalope import Jackalope
from enum import StrEnum

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.inventory import Inventory
    from features.shared.item import Item

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

        room_selection_view = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
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
        return Embed(title="Venture Onwards", description=f"With the jackalope vanquished, the rest of the woods await.")

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
# POST-FEED VIEW
# -----------------------------------------------------------------------------

class PostFeedView(discord.ui.View):
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
        return Embed(title="It Approaches", description=f"The jackalope approaches your hand warily, but with a hop, then another, reaches you and begins to nibble on your offering. After a moment, it leaps away into the forest and you have a sense of peace.")

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
# JACKALOPE VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Feed = "Feed"


class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Leave")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        room_selection_view = ForestRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class AttackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Attack")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(content="At least one person is already in a duel. This duel has been cancelled.")
            return

        victory_view: VictoryView = VictoryView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        defeat_view: forest.ForestDefeatView = forest.ForestDefeatView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())

        duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_players(), [Jackalope()], player_victory_post_view=victory_view, player_loss_post_view=defeat_view)
        initial_info: Embed = duel_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class EnterFeedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Feed")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the duel.")
            return

        if view.get_group_leader() == interaction.user:
            response = view.enter_feed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectInventoryItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view
        if view.get_group_leader() == interaction.user:
            response = view.select_food_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmFoodButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Feed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view
        if view.get_group_leader() == interaction.user:
            response = view.confirm_food_item()

            if response is not None:
                await interaction.response.edit_message(content=None, embed=response, view=view)
            else:
                post_feed_view: PostFeedView = PostFeedView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
                initial_info: Embed = post_feed_view.get_initial_embed()

                await interaction.response.edit_message(embed=initial_info, view=post_feed_view, content=None)


class ExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: JackalopeView = self.view
        if view.get_group_leader() == interaction.user:
            embed = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class JackalopeView(discord.ui.View):
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
        return Embed(title="A Rare Sight", description="In a small clearing beside the path, suddenly one of you spots something most unusual: A small brown rabbit with wings folded against its flank and two protruding elk-like horns.\n\nA few options occur to you:")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(AttackButton())
        self.add_item(EnterFeedButton())
        self.add_item(LeaveButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def enter_feed(self):
        self._intent = Intent.Feed
        self._get_food_buttons()
        return self.get_embed_for_intent()

    def _get_food_buttons(self):
        self.clear_items()
        player: Player = self._get_player(self._group_leader.id)
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Consumable.Food])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectInventoryItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmFoodButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def select_food_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_food_buttons()

        player: Player = self._get_player(self._group_leader.id)
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Feed the Creature", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def confirm_food_item(self):
        player: Player = self._get_player(self._group_leader.id)
        inventory: Inventory = player.get_inventory()
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        # As a reward for choosing the peaceful path, the combat probability in mystery rooms is reset
        self._dungeon_run.num_mystery_without_combat = 0

        # Indicates that the operation completed successfully, since there's no follow-up
        return None

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Feed:
            return Embed(
                title="Feed the Creature",
                description=(
                    "Choose an item from your inventory to feed it.\n\nNavigate through the items using the Prev and Next buttons."
                    f"{error}"
                )
            )
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Feed:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_food_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Feed:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_food_buttons()

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
