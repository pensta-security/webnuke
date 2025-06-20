class MenuHelper:
    @staticmethod
    def run(curses_util, title, items, extra_draw=None):
        """Display a simple curses menu.

        Parameters
        ----------
        curses_util: CursesUtil instance used to manage the screen.
        title: str title displayed at the top of the screen.
        items: list or callable returning list of (key, description, callback).
        extra_draw: optional function(screen) to draw additional content each
            loop before the items are rendered. It should return the next line
            number to use for rendering items or None to start at line 4.
        """
        showscreen = True
        while showscreen:
            screen = curses_util.get_screen()
            screen.addstr(2, 2, title)
            line = 4
            if extra_draw:
                res = extra_draw(screen)
                if isinstance(res, int):
                    line = res
            current_items = items() if callable(items) else items
            for key, desc, _ in current_items:
                screen.addstr(line, 4, f"{key}) {desc}")
                line += 1
            screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            screen.refresh()
            c = screen.getch()
            if c in (ord('M'), ord('m')):
                showscreen = False
                continue
            for key, _, callback in current_items:
                key_code = key if isinstance(key, int) else ord(str(key))
                if c == key_code:
                    curses_util.close_screen()
                    callback()
                    break

