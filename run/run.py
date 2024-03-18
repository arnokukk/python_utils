import sys
from typing import Callable, Any


class Run:
    exclude = ('self', 'e', '_', 'tb', 'args', 'kwargs')

    def __init__(self, *, func: Callable | None = None):
        self.success: bool = True
        self.exception: Exception | None = None
        self.message: str = ''
        self.value: Any = None

        self._func: Callable | None = func

    def run(self, *args, **kwargs):
        try:
            self.value = self._run(*args, **kwargs)
            self.success = True
            self.exception = None
            self.message = ''
        except Exception as e:
            self.handle_exception(e)
        finally:
            return self

    def __bool__(self):
        return self.success

    def handle_exception(self, e: Exception):
        self.success = False
        self.value = None
        self.exception = e
        self.message = f'Exception {type(e).__name__} raised: "{str(e).strip()}"'
        _, _, tb = sys.exc_info()
        self.message += f'\n\t\t> {self.file(tb)}, {self.line(tb)}, {self.function(tb)}, {self.variables(tb)}'
        while next_tb := tb.tb_next:
            tb = next_tb
            self.message += f'\n\t\t> {self.file(tb)}, {self.line(tb)}, {self.function(tb)}, {self.variables(tb)}'

    @staticmethod
    def file(tb) -> str:
        return f'file: {tb.tb_frame.f_code.co_filename}'

    @staticmethod
    def line(tb) -> str:
        return f'line: {tb.tb_lineno}'

    @staticmethod
    def function(tb) -> str:
        return f'function: {tb.tb_frame.f_code.co_name}'

    @staticmethod
    def variables(tb):
        return f"variables: {', '.join([f'{k}={v}' for k, v in tb.tb_frame.f_locals.items() if k not in Run.exclude])}"

    def _run(self, *args, **kwargs) -> Any:
        return self._func(*args, **kwargs) if self._func is not None else None
