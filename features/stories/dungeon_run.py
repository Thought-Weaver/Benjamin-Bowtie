from __future__ import annotations

from features.shared.enums import ForestSection, OceanSection, UnderworldSection
from features.stories.story import Story

# -----------------------------------------------------------------------------
# DUNGEON RUN VARIABLES
# -----------------------------------------------------------------------------

class DungeonRun():
    def __init__(self, dungeon_type: Story, rooms_until_boss: int, section: ForestSection | OceanSection | UnderworldSection):
        self.dungeon_type = dungeon_type
        self.rooms_until_boss = rooms_until_boss
        self.section = section
        
        self.num_mystery_without_combat: int = 0
        self.num_mystery_without_treasure: int = 0
        self.num_mystery_without_shopkeep: int = 0

        self.previous_combat: int = -1
        self.previous_event: int = -1

        # Mostly for stats, tracked across the entire run
        self.rooms_explored: int = 0
        self.combat_encounters: int = 0
        self.treasure_rooms_encountered: int = 0
        self.shopkeeps_encountered: int = 0
        self.events_encountered: int = 0
        self.rests_taken: int = 0
        self.bosses_defeated: int = 0
