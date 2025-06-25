from .menuhelper import MenuHelper
from .networklogger import NetworkLogger
from .domain import get_root_domain


def wait_for_enter(prompt: str = "Press ENTER to return to menu.") -> None:
    """Pause execution until the user presses ENTER.

    This helper centralizes all the little pauses sprinkled throughout
    the command modules.  It simply calls ``input`` with the provided
    prompt and ignores ``EOFError`` so tests can mock ``input`` without
    blowing up.
    """
    try:
        input(prompt)
    except EOFError:
        # When stdin is closed or in automated tests, just continue.
        pass

