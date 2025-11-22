import unittest
from run.run import RunStatusTest, BaseRunTest
from run.run_example import RunExampleTest
from singleton import SingletonTest
from data_struct import DataStructTest
from thread import TestThread, TestArgument
from async_edu.corutines import TestAsyncCoroutines
from async_edu.async_execute import TestAsyncExecute


if __name__ == '__main__':
    unittest.main(verbosity=2)

