#! coding=utf-8

import sys
sys.dont_write_bytecode = True
from os import environ
import unittest
from types import NoneType

from doclient import DOClient, APIAuthError, Droplet
from doclient.droplet import Domain
from doclient.errors import InvalidArgumentError, APIAuthError, APIError


class DOClientTest(unittest.TestCase):

    token = environ.get("DO_KEY")
    invalid_token = ""
    client = None

    def setUp(self):
        self.client = DOClient(self.token)

    def test_valid_client(self):
        """Test valid DOClient instance initalization"""
        # self.client = DOClient(self.token)
        client = self.client
        self.assertTrue(hasattr(client, "filter_droplets") == True)
        self.assertNotIsInstance(client.droplets, NoneType)
        self.assertIsInstance(client.droplets, list)
        for droplet in client.droplets:
            self.assertIsInstance(droplet, Droplet)

    def test_invalid_client(self):
        """Test invalid DOClient instance initalization"""
        try:
            client = DOClient(self.invalid_token)
        except BaseException:
            self.assertRaises(APIAuthError)

    def test_domain_methods(self):
        name = environ.get("test_domain_name")
        ip_address = environ.get("test_domain_ip")
        try:
            create_response = self.client.create_domain(name, ip_address)
            self.assertIsInstance(create_response, dict)
            domain = self.client.get_domain(name)
            self.assertIsInstance(domain, Domain)
            domains = self.client.get_domains()
            self.assertIsInstance(domains, list)
            all_domains = all([isinstance(domain, Domain)
                               for domain in domains])
            self.assertTrue(all_domains)
            del_response = self.client.delete_domain(name)
            self.assertIsInstance(del_response, dict)
        except BaseException, error:
            self.assertIsInstance(error,
                (APIAuthError, APIError, InvalidArgumentError))


if __name__ == "__main__":
    unittest.main()
