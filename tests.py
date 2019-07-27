#! coding=utf-8

import sys
sys.dont_write_bytecode = True
from os import environ
import unittest

from doclient import DOClient, Droplet
from doclient.errors import InvalidArgumentError, APIAuthError, APIError
from doclient.meta import Domain, Snapshot


NoneType = type(None)


class DOClientTest(unittest.TestCase):

    """Tests for DigitalOcean client class"""

    token = environ.get("DO_KEY")
    invalid_token = ""
    client = None

    def setUp(self):
        try:
            self.client = DOClient(self.token)
        except BaseException:
            self.assertRaises(APIAuthError)

    def test_valid_client(self):
        """Test valid DOClient instance initalization"""
        if self.client:
            self.assertTrue(hasattr(self.client, "filter_droplets") == True)
            self.assertNotIsInstance(self.client.droplets, NoneType)
            self.assertIsInstance(self.client.droplets, list)
            for droplet in self.client.droplets:
                self.assertIsInstance(droplet, Droplet)

    def test_invalid_client(self):
        """Test invalid DOClient instance initalization"""
        try:
            client = DOClient(self.invalid_token)
        except BaseException:
            self.assertRaises(APIAuthError)

    def test_domain_methods(self):
        """Tests for domain create, list, get, and delete methods"""
        if self.client:
            name = environ.get("test_domain_name")
            ip_address = environ.get("test_domain_ip")
            try:
                create_response = self.client.create_domain(
                    name, ip_address)
                self.assertIsInstance(create_response, dict)
                domain = self.client.get_domain(name)
                self.assertIsInstance(domain, Domain)
                domains = self.client.get_domains()
                self.assertIsInstance(domains, list)
                all_domains = all((isinstance(domain, Domain)
                                   for domain in domains))
                self.assertTrue(all_domains)
                del_response = self.client.delete_domain(name)
                self.assertIsInstance(del_response, dict)
            except BaseException as error:
                self.assertIsInstance(error,
                    (APIAuthError, APIError, InvalidArgumentError))

    def test_droplet_methods(self):
        """Test droplet functions"""
        if self.client:
            droplet = self.client.filter_droplets("f")[0]
            self.assertIsInstance(droplet, Droplet)
            snapshots = droplet.get_snapshots()
            self.assertIsInstance(snapshots, list)
            for snapshot in snapshots:
                self.assertIsInstance(snapshot, Snapshot)
            neighbours = droplet.get_neighbours()
            self.assertIsInstance(neighbours, list)
            for neighbour in neighbours:
                self.assertIsInstance(neighbour, Droplet)

if __name__ == "__main__":
    unittest.main()
