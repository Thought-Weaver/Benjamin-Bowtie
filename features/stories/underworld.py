from __future__ import annotations

from discord import Embed

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.stats import Stats


class UnderworldStory():
    def __init__(self):
        self._something_stirs: int = 0
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
                description="It plummets into the darkness below." \
                    "Down, down it goes -- past the bottom of the well, through rock and flowing fire into deeper darkness still, down into a place the living believe only superstition.\n\n" \
                    "Somewhere deep in the sunless underworld... something stirs."
            )
        elif player_stats.wishingwell.something_stirs == 0:
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below." \
                    "The coin of someone else, yes, but it too slips beyond the material into the shadows. There is no sound to you above; it is simply gone in a haunting silence.\n\n" \
                    "Somewhere deep in the sunless underworld... something stirs."
            )
        else:
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below." \
                    "You've come again. And your coin, like the other before it, descends descends descends. The darkness grabs it close, pulling the coin quickly towards its inevitable destination.\n\n" \
                    "Somewhere deep in the sunless underworld... something stirs."
            )

        self._something_stirs += 1
        return embed

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._something_stirs = state.get("_something_stirs", 0)
        self.first_to_stir_id = state.get("first_to_stir_id", -1)
