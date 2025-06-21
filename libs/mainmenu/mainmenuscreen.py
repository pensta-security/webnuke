class MainMenuScreen:
    def __init__(self, screen, curses):
        self.screen = screen
        self.curses = curses
        
    def drawscreen(self):
        self.screen.addstr(2, 2,  "Please enter a command")
        self.screen.addstr(3, 4,  " 1) goto <url>   - opens url")
        self.screen.addstr(4, 4,  " 2) quickdetect  - detect technologies in use on url...")
        self.screen.addstr(5, 4,  " 3) jsconsole    - opens a console bound to a browser javascript console...")
        self.screen.addstr(6 , 4, " 4) html         - HTML tools menu...")
        self.screen.addstr(7 , 4, " 5) javascript   - Javascript tools menu...")
        self.screen.addstr(8 , 4, " 6) angularjs    - AngularJS tools menu...")
        self.screen.addstr(9 , 4, " 7) spider       - Spider tools menu...")
        self.screen.addstr(10, 4, " 8) followme     - Activates followme mode...")
        self.screen.addstr(11, 4, " 9) brute        - Brute force login screen...")
        self.screen.addstr(12, 4, "10) aws          - Amazon AWS...")
        self.screen.addstr(13, 4, "11) cms          - CMS info menu...")
        self.screen.addstr(14, 4, "12) xss          - XSS...")
        self.screen.addstr(15, 4, "13) csrf         - CSRF tools...")
        self.screen.addstr(16, 4, "14) debug        - toggle debug on/off")
        self.screen.addstr(17, 4, "15) proxy        - set proxy settings...")
        self.screen.addstr(18, 4, "16) !sh          - escape to unix land...")
        self.screen.addstr(19, 4, "17) update       - git pull and restart")
        self.screen.addstr(20, 4, "18) quit         - Exit webnuke")
        self.screen.addstr(21, 4, "19) dns          - DNS tools...")
        # pointy rocket ascii art with background stars
        greencolour = self.curses.color_pair(2)
        self.screen.addstr(7, 45, "        *        .     *", greencolour)
        self.screen.addstr(8, 45, "          /\\", greencolour)
        self.screen.addstr(9, 45, "   *     /  \\       *", greencolour)
        self.screen.addstr(10,45, "        /++++\\   .", greencolour)
        self.screen.addstr(11,45, "       /  ()  \\     *", greencolour)
        self.screen.addstr(12,45, "       |      |", greencolour)
        self.screen.addstr(13,45, "  *    |      |   .", greencolour)
        self.screen.addstr(14,45, "       |      |    *", greencolour)
        self.screen.addstr(15,45, "      /|______|\\", greencolour)
        self.screen.addstr(16,45, " .    /_        _\\   *", greencolour)
        self.screen.addstr(17,45, "       /_/\\/\\_\\    .", greencolour)
