class OceanStory():
    def __init__(self):
        self.first_to_find_maybe_fish_id: int = -1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.first_to_find_maybe_fish_id = state.get("first_to_find_maybe_fish_id", -1)
