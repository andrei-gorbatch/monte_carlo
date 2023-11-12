# Script to run all tests in the 'tests' folder

import unittest
import os
from config import tests_path

if __name__ == '__main__':
    # Discover all tests in the 'tests' folder
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(tests_path)

    # Run the test suite
    runner = unittest.TextTestRunner()
    runner.run(test_suite)