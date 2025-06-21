import os


class FileLogger:
    """Simple logger that writes messages to a file and stdout."""

    def __init__(self):
        # Default to logging in the current working directory
        self.log_path = os.path.join(os.getcwd(), 'webnuke.log')

    def clear(self) -> None:
        """Remove any existing log contents."""
        open(self.log_path, 'w', encoding='utf-8').close()

    def _write(self, text: str) -> None:
        with open(self.log_path, 'a', encoding='utf-8') as logfile:
            logfile.write(f'{text}\n')

    def log(self, text: str) -> None:
        print(text)
        self._write(text)

    def debug(self, text: str) -> None:
        self.log(f'DEBUG: {text}')

    def error(self, text: str) -> None:
        self.log(f'ERROR: {text}')
        


