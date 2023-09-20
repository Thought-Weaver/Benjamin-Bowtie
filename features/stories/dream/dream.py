from __future__ import annotations

# -----------------------------------------------------------------------------
# DREAM STORY CLASS
# -----------------------------------------------------------------------------

class DreamStory():
    def __init__(self):
        self.gateway_open: bool = False

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.gateway_open = state.get("gateway_open", False)
