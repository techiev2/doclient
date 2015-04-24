#! coding=utf-8

import sys
sys.dont_write_bytecode = True
from os import environ
import unittest

from doclient import DOClient, APIAuthError


class DOClientTest(unittest.TestCase):

    token = environ.get("DO_KEY")
    invalid_token = ""

    def test_valid_client(self):
        """Test valid DOClient instance initalization"""
        client = DOClient(self.token)
        self.assertTrue(hasattr(client, "filter_droplets") == True)

    def test_invalid_client(self):
        """Test invalid DOClient instance initalization"""
        try:
            client = DOClient(self.invalid_token)
        except BaseException:
            self.assertRaises(APIAuthError)


if __name__ == "__main__":
    unittest.main()
