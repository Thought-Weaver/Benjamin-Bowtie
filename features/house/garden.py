from __future__ import annotations

import discord
import random

from discord.embeds import Embed
from strenum import StrEnum
from features.expertise import ExpertiseClass
from features.shared.enums import HouseRoom
from features.shared.constants import MAX_GARDEN_SIZE
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from math import sqrt
from types import MappingProxyType

from typing import TYPE_CHECKING, List, Literal, Tuple

if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House, HouseView
    from features.inventory import Inventory
    from features.shared.item import Item
    from features.player import Player
    from features.stats import Stats

# -----------------------------------------------------------------------------
# SEED DATA
# -----------------------------------------------------------------------------

class SeedData():
    def __init__(self, ticks_until_sprout: int, ticks_until_mature: int, ticks_until_death: int, result: ItemKey, chance_to_drop_seed: float, max_seeds_can_drop: int, sprout_icon: str, xp_to_gain: int):
        self.ticks_until_sprout: int = ticks_until_sprout
        self.ticks_until_mature: int = ticks_until_mature
        self.ticks_until_death: int = ticks_until_death

        self.result: ItemKey = result
        self.chance_to_drop_seed: float = chance_to_drop_seed
        self.max_seeds_can_drop: int = max_seeds_can_drop

        self.sprout_icon: str = sprout_icon
        self.mature_icon: str = LOADED_ITEMS.get_item_state(result)["icon"]

        self.xp_to_gain: int = xp_to_gain

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.ticks_until_sprout = state.get("ticks_until_sprout", 0)
        self.ticks_until_mature = state.get("ticks_until_mature", 0)
        self.ticks_until_death = state.get("ticks_until_death", 0)
        
        self.result = state.get("result", "")
        self.chance_to_drop_seed = state.get("chance_to_drop_seed", 0)
        self.max_seeds_can_drop = state.get("max_seeds_can_drop", 1)

        self.sprout_icon = state.get("sprout_icon", "")
        self.mature_icon = state.get("mature_icon", "")

        self.xp_to_gain = state.get("xp_to_gain", 0)


SEED_DATA: MappingProxyType[ItemKey, SeedData] = MappingProxyType({
    ItemKey.AsptongueSeed: SeedData(2, 4, 20, ItemKey.Asptongue, 0.75, 1, "\uD83C\uDF31", 4),
    ItemKey.BlazeClusterSpores: SeedData(5, 5, 12, ItemKey.BlazeCluster, 0.2, 3, "\uD83C\uDF31", 6),
    ItemKey.BloodcrownSpores: SeedData(2, 2, 8, ItemKey.Bloodcrown, 0.85, 3, "\uD83C\uDF31", 1),
    ItemKey.BramblefrondSeed: SeedData(1, 2, 7, ItemKey.Bramblefrond, 0.8, 1, "\uD83C\uDF31", 1),
    ItemKey.DawnsGlorySeed: SeedData(2, 4, 8, ItemKey.DawnsGlory, 0.65, 1, "\uD83C\uDF31", 4),
    ItemKey.DragonsTeethSeed: SeedData(10, 25, 30, ItemKey.DragonsTeeth, 0.02, 1, "\uD83C\uDF31", 156),
    ItemKey.DreamMakerSeed: SeedData(3, 6, 16, ItemKey.DreamMaker, 0.4, 1, "\uD83C\uDF31", 9),
    ItemKey.FissureleafSeed: SeedData(1, 3, 12, ItemKey.Fissureleaf, 0.5, 1, "\uD83C\uDF31", 2),
    ItemKey.FoolsDelightSpores: SeedData(5, 5, 20, ItemKey.FoolsDelight, 0.4, 2, "\uD83C\uDF31", 6),
    ItemKey.ForgottenTearsSeed: SeedData(8, 15, 50, ItemKey.ForgottenTears, 0.05, 1, "\uD83C\uDF31", 56),
    ItemKey.FrostwortSeed: SeedData(2, 3, 10, ItemKey.Frostwort, 0.6, 3, "\uD83C\uDF31", 2),
    ItemKey.GoldenCloverSeed: SeedData(1, 3, 5, ItemKey.GoldenClover, 0.1, 1, "\uD83C\uDF31", 2),
    ItemKey.GraspleafSeed: SeedData(1, 3, 18, ItemKey.Graspleaf, 0.85, 2, "\uD83C\uDF31", 2),
    ItemKey.GraveMossSpores: SeedData(4, 4, 12, ItemKey.GraveMoss, 0.6, 3, "\uD83C\uDF31", 4),
    ItemKey.HushvineSeed: SeedData(5, 10, 20, ItemKey.Hushvine, 0.45, 1, "\uD83C\uDF31", 25),
    ItemKey.LichbloomSeed: SeedData(24, 64, 2400, ItemKey.Lichbloom, 0.01, 1, "\uD83C\uDF31", 256),
    ItemKey.MagesBaneSeed: SeedData(5, 12, 16, ItemKey.MagesBane, 0.3, 1, "\uD83C\uDF31", 36),
    ItemKey.ManabloomSeed: SeedData(3, 5, 15, ItemKey.Manabloom, 0.4, 2, "\uD83C\uDF31", 6),
    ItemKey.MeddlespreadSpores: SeedData(1, 1, 30, ItemKey.Meddlespread, 0.9, 6, "\uD83C\uDF31", 1),
    ItemKey.RazorgrassSeed: SeedData(1, 2, 14, ItemKey.Razorgrass, 0.6, 2, "\uD83C\uDF31", 1),
    ItemKey.RiverblossomSeed: SeedData(1, 3, 10, ItemKey.Riverblossom, 0.8, 1, "\uD83C\uDF31", 2),
    ItemKey.RotstalkSeed: SeedData(3, 10, 40, ItemKey.Rotstalk, 0.1, 1, "\uD83C\uDF31", 25),
    ItemKey.SeacloverSeed: SeedData(1, 2, 10, ItemKey.Seaclover, 0.75, 5, "\uD83C\uDF31", 1),
    ItemKey.ShellflowerSeed: SeedData(4, 6, 14, ItemKey.Shellflower, 0.5, 1, "\uD83C\uDF31", 9),
    ItemKey.ShelterfoilSeed: SeedData(3, 4, 20, ItemKey.Shelterfoil, 0.4, 2, "\uD83C\uDF31", 4),
    ItemKey.ShiverrootSeed: SeedData(2, 3, 15, ItemKey.Shiverroot, 0.6, 1, "\uD83C\uDF31", 2),
    ItemKey.SirensKissSeed: SeedData(5, 10, 15, ItemKey.SirensKiss, 0.1, 2, "\uD83C\uDF31", 25),
    ItemKey.SlumbershroomSpores: SeedData(4, 4, 14, ItemKey.Slumbershroom, 0.1, 2, "\uD83C\uDF31", 25),
    ItemKey.SnowdewSeed: SeedData(1, 2, 6, ItemKey.Snowdew, 0.9, 1, "\uD83C\uDF31", 1),
    ItemKey.SpeckledCapSpores: SeedData(2, 2, 6, ItemKey.SpeckledCap, 0.5, 3, "\uD83C\uDF31", 1),
    ItemKey.SpidersGroveSpores: SeedData(7, 7, 24, ItemKey.SpidersGrove, 0.1, 2, "\uD83C\uDF31", 12),
    ItemKey.SungrainSeed: SeedData(1, 2, 20, ItemKey.Sungrain, 0.7, 2, "\uD83C\uDF31", 1),
    ItemKey.WanderweedSeed: SeedData(2, 6, 9, ItemKey.Wanderweed, 0.15, 3, "\uD83C\uDF31", 9),
    ItemKey.WitherheartSeed: SeedData(12, 24, 26, ItemKey.Witherheart, 0.03, 1, "\uD83C\uDF31", 144),

    ItemKey.AllumCutting: SeedData(1, 3, 8, ItemKey.Allum, 0.75, 1, "\uD83C\uDF31", 1),
    ItemKey.AppleSeed: SeedData(2, 4, 18, ItemKey.Apple, 0.5, 4, "\uD83C\uDF31", 1),
    ItemKey.AshberrySeed: SeedData(1, 3, 25, ItemKey.Ashberries, 0.95, 1, "\uD83C\uDF31", 1),
    ItemKey.AzureberrySeed: SeedData(1, 3, 10, ItemKey.Azureberries, 0.45, 3, "\uD83C\uDF31", 1),
    ItemKey.CrownberrySeed: SeedData(1, 2, 14, ItemKey.Crownberry, 0.2, 4, "\uD83C\uDF31", 1),
    ItemKey.DragonPepperSeed: SeedData(1, 3, 20, ItemKey.DragonPepper, 0.6, 2, "\uD83C\uDF31", 1),
    ItemKey.ElsberrySeed: SeedData(1, 2, 12, ItemKey.Elsberries, 0.7, 3, "\uD83C\uDF31", 1),
    ItemKey.GoldenAppleSeed: SeedData(1, 2, 12, ItemKey.GoldenApple, 0.01, 3, "\uD83C\uDF31", 1),
    ItemKey.GrovemelonSeed: SeedData(2, 5, 25, ItemKey.Grovemelon, 0.5, 2, "\uD83C\uDF31", 1),
    ItemKey.HoneyfruitSeed: SeedData(1, 3, 15, ItemKey.Honeyfruit, 0.85, 1, "\uD83C\uDF31", 1),
    ItemKey.PlumpinSeed: SeedData(2, 4, 12, ItemKey.Plumpin, 0.4, 3, "\uD83C\uDF31", 1),
    ItemKey.PotatoCutting: SeedData(1, 2, 30, ItemKey.Potato, 0.95, 1, "\uD83C\uDF31", 1),
    ItemKey.SpearLeekCutting: SeedData(2, 3, 10, ItemKey.SpearLeek, 0.9, 1, "\uD83C\uDF31", 1),
    ItemKey.SunfruitSeed: SeedData(1, 3, 15, ItemKey.Sunfruit, 0.6, 2, "\uD83C\uDF31", 1),
    ItemKey.SweetrootCutting: SeedData(1, 2, 18, ItemKey.Sweetroot, 0.9, 1, "\uD83C\uDF31", 1)
})


# (First Plant, Second Plant): (Yields this Plant, With this Probability)
MUTATION_PROBS: MappingProxyType[Tuple[ItemKey | Literal[""], ItemKey | Literal[""]], Tuple[ItemKey, float]] = MappingProxyType({
    (ItemKey.Seaclover, ItemKey.Seaclover): (ItemKey.GraspleafSeed, 0.25),
    (ItemKey.Graspleaf, ItemKey.Seaclover): (ItemKey.BramblefrondSeed, 0.2),
    (ItemKey.Bramblefrond, ItemKey.Graspleaf): (ItemKey.FissureleafSeed, 0.15),
    (ItemKey.Fissureleaf, ItemKey.Seaclover): (ItemKey.RazorgrassSeed, 0.1),
    (ItemKey.Razorgrass, ItemKey.Graspleaf): (ItemKey.GraveMossSpores, 0.08),
    (ItemKey.GraveMoss, ItemKey.Asptongue): (ItemKey.HushvineSeed, 0.02),
    (ItemKey.Hushvine, ItemKey.FoolsDelight): (ItemKey.RotstalkSeed, 0.01),
    (ItemKey.Snowdew, ItemKey.Sungrain): (ItemKey.DawnsGlorySeed, 0.15),
    (ItemKey.DawnsGlory, ItemKey.Snowdew): (ItemKey.RiverblossomSeed, 0.1),
    (ItemKey.Riverblossom, ItemKey.Riverblossom): (ItemKey.ManabloomSeed, 0.03),
    (ItemKey.Manabloom, ItemKey.FoolsDelight): (ItemKey.DreamMakerSeed, 0.01),
    (ItemKey.DreamMaker, ItemKey.Rotstalk): (ItemKey.WitherheartSeed, 0.005),
    (ItemKey.Witherheart, ItemKey.DawnsGlory): (ItemKey.DragonsTeethSeed, 0.02),
    (ItemKey.Witherheart, ItemKey.Manabloom): (ItemKey.MagesBaneSeed, 0.1),
    (ItemKey.DreamMaker, ItemKey.Manabloom): (ItemKey.LichbloomSeed, 0.005),
    (ItemKey.Lichbloom, ItemKey.DragonsTeeth): (ItemKey.ForgottenTearsSeed, 0.001),
    (ItemKey.Snowdew, ItemKey.Seaclover): (ItemKey.FrostwortSeed, 0.25),
    (ItemKey.Frostwort, ItemKey.Snowdew): (ItemKey.ShiverrootSeed, 0.2),
    (ItemKey.Shiverroot, ItemKey.Seaclover): (ItemKey.ShelterfoilSeed, 0.15),
    (ItemKey.Shelterfoil, ItemKey.Shiverroot): (ItemKey.ShellflowerSeed, 0.05),
    (ItemKey.Meddlespread, ItemKey.Meddlespread): (ItemKey.SpeckledCapSpores, 0.25),
    (ItemKey.SpeckledCap, ItemKey.Meddlespread): (ItemKey.BloodcrownSpores, 0.2),
    (ItemKey.Bloodcrown, ItemKey.SpeckledCap): (ItemKey.FoolsDelightSpores, 0.15),
    (ItemKey.FoolsDelight, ItemKey.Bloodcrown): (ItemKey.SpidersGroveSpores, 0.01),
    (ItemKey.Bloodcrown, ItemKey.DawnsGlory): (ItemKey.BlazeClusterSpores, 0.1),
    (ItemKey.Seaclover, ItemKey.Sungrain): (ItemKey.GoldenCloverSeed, 0.005),
    (ItemKey.Meddlespread, ItemKey.Snowdew): (ItemKey.WanderweedSeed, 0.01),
    (ItemKey.GoldenClover, ItemKey.Apple): (ItemKey.GoldenCloverSeed, 0.01)
})

# -----------------------------------------------------------------------------
# GARDEN PLOT
# -----------------------------------------------------------------------------

class GardenPlot():
    def __init__(self):
        self.seed: Item | None = None
        # Should be None until the growth ticks match those needed by the seed
        self.plant: Item | None = None
        self.soil: Item | None = None
        self.seed_data: SeedData | None = None
        self.growth_ticks: int = 0
        self.may_mutate: bool = False

    def harvest(self):
        if self.seed is None:
            return None

        # If self.growth_ticks < self.ticks_until_mature, this uproots it 
        # and returns None!
        harvested_plant = self.plant

        if self.soil is not None and self.soil.get_key() == ItemKey.Compost:
            if harvested_plant is not None and random.random() < 0.05:
                harvested_plant.add_amount(1)

        self.reset(keep_soil=True)

        return harvested_plant

    def tick(self):
        if self.seed_data is None:
            return

        self.growth_ticks += 1

        if self.growth_ticks == self.seed_data.ticks_until_mature:
            self.plant = LOADED_ITEMS.get_new_item(self.seed_data.result)
        
        if self.growth_ticks >= self.seed_data.ticks_until_death:
            self.reset(keep_soil=True)

    def reset(self, keep_soil=False):
        self.seed = None
        self.plant = None
        self.soil = None if not keep_soil else self.soil
        self.seed_data = None
        self.growth_ticks = 0
        self.may_mutate = False

    def is_mature(self):
        if self.seed_data is None:
            return False

        return self.growth_ticks >= self.seed_data.ticks_until_mature and self.growth_ticks < self.seed_data.ticks_until_death

    def plant_seed(self, seed: Item):
        seed_data = SEED_DATA.get(seed.get_key())

        if seed_data is None:
            return "*That seed can't be planted*"

        self.seed = seed
        self.seed_data = seed_data
        self.may_mutate = False

        return f"*Planted {seed.get_full_name()}!*"

    def use_item(self, item: Item):
        if ClassTag.Gardening.Soil in item.get_class_tags():
            self.soil = item
            return f"*Soil changed to {item.get_full_name()}!*"
        return "*That item can't be used on this plot!*"

    def get_icon(self):
        if self.seed_data is None:
            return None

        if self.growth_ticks < self.seed_data.ticks_until_sprout:
            # Default sprout icon until then, maybe replaced with a different icon during the actual
            # sprouting phase
            return "\uD83D\uDFEB"

        if self.growth_ticks >= self.seed_data.ticks_until_sprout and self.growth_ticks < self.seed_data.ticks_until_mature:
            return self.seed_data.sprout_icon

        if self.growth_ticks >= self.seed_data.ticks_until_mature and self.growth_ticks < self.seed_data.ticks_until_death:
            return self.seed_data.mature_icon

        # Return a question mark
        return "\u2753"

    def __str__(self):
        if self.seed is None or self.seed_data is None:
            soil_str = f"\n**{self.soil.get_full_name()}:** {self.soil.get_description()}" if self.soil is not None else ""

            may_mutate_string = ""
            if self.seed is None and self.seed_data is None and self.may_mutate:
                may_mutate_string = ("" if soil_str == "" else "\n") + "*This plot might mutate into a new plant next tick!*\n"
            
            result_str = f"\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆{soil_str}\n{may_mutate_string}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆" if (soil_str != "" or may_mutate_string != "") else ""
            return result_str
        
        growth_tick_str = "tick" if self.growth_ticks == 1 else "ticks"

        ticks_until_mature = self.seed_data.ticks_until_mature - self.growth_ticks
        mature_tick_str = "tick" if ticks_until_mature == 1 else "ticks"
        
        ticks_until_death = self.seed_data.ticks_until_death - self.growth_ticks
        death_tick_str = "tick" if ticks_until_death == 1 else "ticks"
        
        mature_string = f"Mature in {ticks_until_mature} {mature_tick_str}" if ticks_until_mature > 0 else f"Will perish in {ticks_until_death} {death_tick_str}"

        num_mutations = 0
        for plant_key_1, plant_key_2 in MUTATION_PROBS.keys():
            if self.seed_data.result == plant_key_1 or self.seed_data.result == plant_key_2:
                num_mutations += 1
        mutate_string = f"{num_mutations} possible mutation{'s' if num_mutations != 1 else ''}\n" if num_mutations > 0 else ""

        soil_str = f"{self.soil.get_full_name()}: {self.soil.get_description()}\n\n" if self.soil is not None else ""

        display_string = f"\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self.seed.get_full_name()}\n\n{soil_str}{self.growth_ticks} {growth_tick_str} old\n{mature_string}\n{mutate_string}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.seed = state.get("seed", None)
        self.plant = state.get("plant", None)
        self.soil = state.get("soil", None)
        self.growth_ticks = state.get("growth_ticks", 0)
        self.may_mutate = state.get("may_mutate", False)

        self.seed_data = None
        if self.seed is not None:
            self.seed_data = SEED_DATA.get(self.seed.get_key())

# -----------------------------------------------------------------------------
# GARDEN VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    PlantSeed = "PlantSeed"
    UseItem = "UseItem"


class HarvestButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Harvest", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.harvest()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PlantSeedButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Plant Seed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_plant_seed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UseItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Use Item", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_use_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExpandButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Expand ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.expand_garden()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSeedButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.select_seed(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.select_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GardenPlotButton(discord.ui.Button):
    def __init__(self, plot: GardenPlot, row: int, is_selected: bool):
        icon = plot.get_icon()
        super().__init__(
            style=discord.ButtonStyle.secondary if not is_selected else discord.ButtonStyle.blurple, 
            row=row, label="‍" if icon is None else None,
            emoji=icon
        )
        
        self._plot = plot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.select_plot(self._plot)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseGardenButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_garden()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmPlantSeedButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_plant_seed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmUseItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_use_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView | None = view.get_house_view()
            if house_view is not None:
                embed = house_view.get_initial_embed()
                await interaction.response.edit_message(content=None, embed=embed, view=house_view)


class ExitToGardenButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GardenView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView | None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view
        
        self._selected_item_index = -1
        self._selected_item: Item | None = None
        self._selected_plot: GardenPlot | None = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._intent: Intent | None = None
        
        self._PLOT_COST = 500
        self._PURCHASE_COST = 2000

        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, additional: str=""):
        if self._intent == Intent.PlantSeed:
            return Embed(title="Plant Seed", description="Choose a seed to plant in this plot.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        if self._intent == Intent.UseItem:
            return Embed(title="Use Item", description="Choose an item to use on this plot.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        return Embed(title="Garden", description="You enter the garden, where you can plant seeds and harvest crops. The garden plots tick every hour." + additional)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Garden in self._get_player().get_house().house_rooms:
            self._get_garden_buttons()
        else:
            self.add_item(PurchaseGardenButton(self._PURCHASE_COST, 0))
            if self._house_view is not None:
                self.add_item(ExitToHouseButton(0))

        self._intent = None

    def _get_garden_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        house: House = player.get_house()
        
        num_per_row = int(sqrt(len(house.garden_plots)))
        for i, plot in enumerate(house.garden_plots):
            self.add_item(GardenPlotButton(plot, int(i / num_per_row), plot == self._selected_plot))

        if self._selected_plot is not None:
            self.add_item(HarvestButton(min(4, num_per_row)))
            if self._selected_plot.seed is None:
                self.add_item(PlantSeedButton(min(4, num_per_row)))
            self.add_item(UseItemButton(min(4, num_per_row)))
        if int(sqrt(len(player.get_house().garden_plots))) < MAX_GARDEN_SIZE:
            self.add_item(ExpandButton(self._PLOT_COST, min(4, num_per_row)))
        if self._house_view is not None:
            self.add_item(ExitToHouseButton(min(4, num_per_row)))

        self._intent = None

    def purchase_garden(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(additional="\n\n*Error: You don't have enough coins to purchase the garden.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Garden)
        # You get one for free!
        house.garden_plots = [GardenPlot()]
        self._get_garden_buttons()

        return self.get_embed_for_intent(additional=f"\n\n*Garden purchased! You can further expand it for {self._PLOT_COST} coins.*")
    
    def _get_plant_seed_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Gardening.Seed])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectSeedButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmPlantSeedButton(min(4, len(page_slots))))
        self.add_item(ExitToGardenButton(min(4, len(page_slots))))

    def _get_use_item_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Gardening.Soil, ClassTag.Gardening.GrowthAssist])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmUseItemButton(min(4, len(page_slots))))
        self.add_item(ExitToGardenButton(min(4, len(page_slots))))

    def enter_plant_seed(self):
        self._intent = Intent.PlantSeed

        self._get_plant_seed_buttons()
        return self.get_embed_for_intent()

    def enter_use_item(self):
        self._intent = Intent.UseItem

        self._get_use_item_buttons()
        return self.get_embed_for_intent()

    def harvest(self):
        if self._selected_plot is None or self._selected_plot.seed is None or self._selected_plot.seed_data is None:
            self._get_garden_buttons()
            return self.get_embed_for_intent(additional="\n\n*A plot either isn't selected or lacks a seed!*")

        seed_key = self._selected_plot.seed.get_key()
        seed_data = self._selected_plot.seed_data
        harvest_result = self._selected_plot.harvest()

        self._get_garden_buttons()

        if harvest_result is None:
            return self.get_embed_for_intent(additional="\n\n*The harvest yielded nothing!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory.add_item(harvest_result)

        stats: Stats = player.get_stats()
        if harvest_result.get_rarity() == Rarity.Common:
            stats.garden.common_plants_harvested += 1
        if harvest_result.get_rarity() == Rarity.Uncommon:
            stats.garden.uncommon_plants_harvested += 1
        if harvest_result.get_rarity() == Rarity.Rare:
            stats.garden.rare_plants_harvested += 1
        if harvest_result.get_rarity() == Rarity.Epic:
            stats.garden.epic_plants_harvested += 1
        if harvest_result.get_rarity() == Rarity.Legendary:
            stats.garden.legendary_plants_harvested += 1

        max_seed_adjustment = 1 if self._selected_plot.soil is not None and self._selected_plot.soil.get_key() == ItemKey.Loam else 0
        seed_drop_adjustment = 0.15 if self._selected_plot.soil is not None and self._selected_plot.soil.get_key() == ItemKey.Clay else 0
        num_seeds_to_add = 0
        for _ in range(seed_data.max_seeds_can_drop + max_seed_adjustment):
            if random.random() < seed_data.chance_to_drop_seed + seed_drop_adjustment:
                num_seeds_to_add += 1
                inventory.add_item(LOADED_ITEMS.get_new_item(seed_key))
        seeds_added_str = f" and {num_seeds_to_add} seeds" if num_seeds_to_add > 0 else ""

        if harvest_result.get_rarity() == Rarity.Common:
            stats.garden.common_seeds_dropped += num_seeds_to_add
        if harvest_result.get_rarity() == Rarity.Uncommon:
            stats.garden.uncommon_seeds_dropped += num_seeds_to_add
        if harvest_result.get_rarity() == Rarity.Rare:
            stats.garden.rare_seeds_dropped += num_seeds_to_add
        if harvest_result.get_rarity() == Rarity.Epic:
            stats.garden.epic_seeds_dropped += num_seeds_to_add
        if harvest_result.get_rarity() == Rarity.Legendary:
            stats.garden.legendary_seeds_dropped += num_seeds_to_add

        final_xp = player.get_expertise().add_xp_to_class(seed_data.xp_to_gain, ExpertiseClass.Alchemist, player.get_equipment())

        player.get_house().tick_garden(only_update_display=True)

        return self.get_embed_for_intent(additional=f"\n\n*You received {harvest_result.get_full_name_and_count()}{seeds_added_str} and gained {final_xp} Alchemist xp*")

    def expand_garden(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()

        if int(sqrt(len(house.garden_plots))) == MAX_GARDEN_SIZE:
            self._get_garden_buttons()
            return self.get_embed_for_intent(additional="\n\n*You've reached the max size for the garden!*")

        if inventory.get_coins() < self._PLOT_COST:
            return self.get_embed_for_intent(additional=f"\n\n*You don't have enough coins ({self._PLOT_COST}) to expand the garden.*")

        inventory.remove_coins(self._PLOT_COST)

        cur_size = int(sqrt(len(house.garden_plots)))
        for _ in range(cur_size * cur_size, (cur_size + 1) * (cur_size + 1)):
            house.garden_plots.append(GardenPlot())

        player.get_house().tick_garden(only_update_display=True)

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*You increased the size of the garden from {cur_size * cur_size} plots to {(cur_size + 1) * (cur_size + 1)} plots!*")

    def select_plot(self, plot: GardenPlot):
        self._selected_plot = plot
        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=str(plot))

    def select_seed(self, index: int, seed: Item):
        self._selected_item = seed
        self._selected_item_index = index

        self._get_plant_seed_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Plant Seed", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def confirm_plant_seed(self):
        if self._selected_plot is None:
            return self.get_embed_for_intent(additional="\n\n*That plot doesn't exist!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        seed = inventory.remove_item(self._selected_item_index, 1)
        if seed is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        response = self._selected_plot.plant_seed(seed)

        player.get_house().tick_garden(only_update_display=True)

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*{response}*")

    def select_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_use_item_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Use Item", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def confirm_use_item(self):
        if self._selected_plot is None:
            return self.get_embed_for_intent(additional="\n\n*That plot doesn't exist!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        item = inventory.remove_item(self._selected_item_index, 1)
        if item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        response = self._selected_plot.use_item(self._selected_item)

        player.get_house().tick_garden(only_update_display=True)

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*{response}*")

    def next_page(self):
        self._page += 1
        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.PlantSeed:
            self._get_plant_seed_buttons()
        if self._intent == Intent.UseItem:
            self._get_use_item_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._selected_item = None
        self._selected_item_index = -1

        if self._intent == Intent.PlantSeed:
            self._get_plant_seed_buttons()
        if self._intent == Intent.UseItem:
            self._get_use_item_buttons()

        return self.get_embed_for_intent()
    
    def exit_to_main_menu(self):
        self._get_garden_buttons()
        return self.get_embed_for_intent()

    def get_bot(self):
        return self._bot

    def get_user(self):
        return self._user

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_house_view(self):
        return self._house_view
