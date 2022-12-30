from __future__ import annotations
import random

from discord import Embed

from features.shared.item import LOADED_ITEMS, ItemKey

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.stats import Stats


class UnderworldStory():
    def __init__(self):
        self._something_stirs: int = 0
        self.remaining_sunless_keys: List[ItemKey] = [
            ItemKey.SunlessStride,
            ItemKey.SunlessChains,
            ItemKey.SunlessGrip,
            ItemKey.SunlessSteps,
            ItemKey.SunlessMind,
            ItemKey.SunlessHeart,
            ItemKey.SunlessWill
        ]
        self.first_to_stir_id: int = -1

    def get_wishing_well_response(self, user_id: int, player_stats: Stats):
        embed = Embed(
            title="You toss the coin in...",
            description="It plummets into the darkness below and hits the bottom with a resounding clink."
        )
        if self._something_stirs == 0:
            self.first_to_stir_id = user_id
            embed = Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "Down, down it goes -- past the bottom of the well, through rock and flowing fire into deeper darkness still, down into a place the living believe only superstition.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )
        elif player_stats.wishingwell.something_stirs == 0:
            embed = Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "The coin of someone else, yes, but it too slips beyond the material into the shadows. There is no sound to you above; it is simply gone in a haunting silence.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )
        else:
            embed = Embed(
                title="You toss the coin in...",
                description=(
                    "It plummets into the darkness below. "
                    "You've come again. And your coin, like the other before it, descends descends descends. The darkness grabs it close, pulling the coin quickly towards its inevitable destination.\n\n"
                    "Somewhere deep in the sunless underworld... something stirs."
                )
            )

        self._something_stirs += 1
        return embed

    def get_wishing_well_item(self):
        if len(self.remaining_sunless_keys) > 0:
            rand_index: int = random.randint(0, max(0, len(self.remaining_sunless_keys) - 1))
            item_key: ItemKey = self.remaining_sunless_keys.pop(rand_index)

            return LOADED_ITEMS.get_new_item(item_key)
        else:
            rand_key = random.choices(
                [
                    ItemKey.CrackedAgate, ItemKey.CrackedAmethyst, ItemKey.CrackedBloodstone, ItemKey.CrackedDiamond,
                    ItemKey.CrackedEmerald, ItemKey.CrackedJade, ItemKey.CrackedLapis, ItemKey.CrackedMalachite,
                    ItemKey.CrackedMoonstone, ItemKey.CrackedOpal, ItemKey.CrackedOnyx, ItemKey.CrackedPeridot,
                    ItemKey.CrackedQuartz, ItemKey.CrackedRuby, ItemKey.CrackedSapphire, ItemKey.CrackedTanzanite,
                    ItemKey.CrackedTopaz, ItemKey.CrackedTurquoise, ItemKey.CrackedZircon,

                    ItemKey.Agate, ItemKey.Amethyst, ItemKey.Bloodstone, ItemKey.Diamond,
                    ItemKey.Emerald, ItemKey.Jade, ItemKey.Lapis, ItemKey.Malachite,
                    ItemKey.Moonstone, ItemKey.Opal, ItemKey.Onyx, ItemKey.Peridot,
                    ItemKey.Quartz, ItemKey.Ruby, ItemKey.Sapphire, ItemKey.Tanzanite,
                    ItemKey.Topaz, ItemKey.Turquoise, ItemKey.Zircon,
                    
                    ItemKey.FlawlessAgate, ItemKey.FlawlessAmethyst, ItemKey.FlawlessBloodstone, ItemKey.FlawlessDiamond,
                    ItemKey.FlawlessEmerald, ItemKey.FlawlessJade, ItemKey.FlawlessLapis, ItemKey.FlawlessMalachite,
                    ItemKey.FlawlessMoonstone, ItemKey.FlawlessOpal, ItemKey.FlawlessOnyx, ItemKey.FlawlessPeridot,
                    ItemKey.FlawlessQuartz, ItemKey.FlawlessRuby, ItemKey.FlawlessSapphire, ItemKey.FlawlessTanzanite,
                    ItemKey.FlawlessTopaz, ItemKey.FlawlessTurquoise, ItemKey.FlawlessZircon
                ], 
                k=1,
                weights=[
                    0.035 * 2/76, 0.035 * 5/76, 0.035 * 6/76, 0.035 * 3/76,
                    0.035 * 7/76, 0.035 * 6/76, 0.035 * 1/76, 0.035 * 4/76,
                    0.035 * 2/76, 0.035 * 2/76, 0.035 * 2/76, 0.035 * 8/76,
                    0.035 * 10/76, 0.035 * 1/76, 0.035 * 1/76, 0.035 * 2/76,
                    0.035 * 1/76, 0.035 * 6/76, 0.035 * 5/76,

                    0.01 * 2/76, 0.01 * 5/76, 0.01 * 6/76, 0.01 * 3/76,
                    0.01 * 7/76, 0.01 * 6/76, 0.01 * 1/76, 0.01 * 4/76,
                    0.01 * 2/76, 0.01 * 2/76, 0.01 * 2/76, 0.01 * 8/76,
                    0.01 * 10/76, 0.01 * 1/76, 0.01 * 1/76, 0.01 * 2/76,
                    0.01 * 1/76, 0.01 * 6/76, 0.01 * 5/76,

                    0.005 * 2/76, 0.005 * 5/76, 0.005 * 6/76, 0.005 * 3/76,
                    0.005 * 7/76, 0.005 * 6/76, 0.005 * 1/76, 0.005 * 4/76,
                    0.005 * 2/76, 0.005 * 2/76, 0.005 * 2/76, 0.005 * 8/76,
                    0.005 * 10/76, 0.005 * 1/76, 0.005 * 1/76, 0.005 * 2/76,
                    0.005 * 1/76, 0.005 * 6/76, 0.005 * 5/76,
                ]
            )[0]
            return LOADED_ITEMS.get_new_item(rand_key)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._something_stirs = state.get("_something_stirs", 0)
        self.first_to_stir_id = state.get("first_to_stir_id", -1)
        self.remaining_sunless_keys = state.get("remaining_sunless_keys",
            [
                ItemKey.SunlessStride,
                ItemKey.SunlessChains,
                ItemKey.SunlessGrip,
                ItemKey.SunlessSteps,
                ItemKey.SunlessMind,
                ItemKey.SunlessHeart,
                ItemKey.SunlessWill
            ]
        )
