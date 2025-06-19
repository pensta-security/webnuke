class JSConsoleScript:
    def __init__(self, jsinjector):
        self.version = 2.0
        self.jsinjector = jsinjector
        self.jsinjector.add_help_topic('wn_help()', 'Shows WebNuke Help')

        
