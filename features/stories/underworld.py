class UnderworldStory():
    def __init__(self):
        self.something_stirs = 0

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.something_stirs = state.get("something_stirs", 0)
