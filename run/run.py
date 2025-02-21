from typing import Type
from unittest import main, TestCase
from types import TracebackType
from sys import exc_info
from typing import Self


class RunStatus:
    __excludes = ('self', 'e', '_', 'tb', 'args', 'kwargs')
    __slots__ = ('success', 'exception_type', 'exception_message', '_message')

    def __init__(self, status: bool = True, message: str = ''):
        self.success: bool = status
        self.exception_type: Type = type(None)
        self.exception_message: str = ''
        self._message: str = message

    def handle_exception(self, exception: Exception):
        self.success = False
        self.exception_type = type(exception)
        self.exception_message = str(exception)
        self._message = f'Exception {self.exception_type.__name__} raised: "{self.exception_message}"'
        _, _, tb = exc_info()
        if tb is not None:
            while tb := tb.tb_next:
                self._message += self.msg_line(tb)

    def __bool__(self):
        return self.success and self.exception_type() is None and self.exception_message == ''

    def __str__(self):
        return f'<Status: {self.success} ({self.exception_type} {self.exception_message})>'

    @property
    def message(self) -> str:
        return self._message

    @classmethod
    def msg_line(cls, tb: TracebackType, vars_str_length: int = 80):
        def _vars() -> str:
            return ', '.join([f'{k}={v}' for k, v in tb.tb_frame.f_locals.items() if k not in cls.__excludes])
        return (f'\n\t\t>>'
                f'file: {tb.tb_frame.f_code.co_filename}, line: {tb.tb_lineno}, function: {tb.tb_frame.f_code.co_name},'
                f'\n\t\t\tvariables: {_vars()[:vars_str_length]}')


class BaseRun:
    __slots__ = ('status',)

    def __init__(self):
        self.status: RunStatus = RunStatus()

    def __bool__(self):
        return bool(self.status)

    def run(self, *args, **kwargs) -> Self:
        try:
            self.status = self._run(*args, **kwargs)
        except Exception as e:
            self.status.handle_exception(e)
        finally:
            return self

    def _run(self, *args, **kwargs) -> RunStatus:
        raise NotImplementedError('Implement _run in class derived from BaseRun')


class RunStatusTest(TestCase):
    def test_init(self):
        rs = RunStatus()
        self.assertTrue(rs.success)
        self.assertIsNone(rs.exception_type())
        self.assertEqual(rs.exception_message, '')

    def test_handle_exception(self):
        rs = RunStatus()
        self.assertTrue(rs)
        rs.handle_exception(ValueError('value error example'))
        self.assertFalse(rs.success)
        self.assertEqual(rs.exception_type.__name__, 'ValueError')
        self.assertEqual(rs.exception_message, 'value error example')
        self.assertTrue(rs.message.startswith('Exception') and '"value error example"' in rs.message)


class BaseRunTest(TestCase):
    def test_init(self):
        br = BaseRun()
        self.assertTrue(br.status)

    def test_run(self):
        result = BaseRun().run()
        self.assertFalse(result.status)
        self.assertIs(result.status.exception_type, NotImplementedError)
        self.assertIn('function: _run', result.status.message)
        self.assertEqual(len(result.status.message.split('\n')), 3)


if __name__ == '__main__':
    main(verbosity=2)
