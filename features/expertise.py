from enum import Enum

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
