from __future__ import annotations

from features.shared.enums import ForestSection, OceanSection, UnderworldSection

# -----------------------------------------------------------------------------
# PLAYER DUNGEON RUN VARIABLES
# -----------------------------------------------------------------------------

class PlayerDungeonRun():
    def __init__(self):
        self.in_dungeon_run: bool = False
        self.in_rest_area: bool = False
        self.corruption: int = 0

        self.forest_best_act: ForestSection = ForestSection.QuietGrove
        self.ocean_best_act: OceanSection = OceanSection.TidewaterShallows
        self.underworld_best_act: UnderworldSection = UnderworldSection.MistyTunnels

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.in_dungeon_run = state.get("in_dungeon_run", False)
        self.in_rest_area = state.get("in_rest_area", False)
        self.corruption = state.get("corruption", 0)

        self.forest_best_act = state.get("forest_best_act", ForestSection.QuietGrove)
        self.ocean_best_act = state.get("ocean_best_act", OceanSection.TidewaterShallows)
        self.underworld_best_act = state.get("underworld_best_act", UnderworldSection.MistyTunnels)
