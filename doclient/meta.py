#! coding=utf-8
"""
DigitalOcean APIv2 metadata module
Exposes meta classes for meta informtaion.
"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("Domain",)

import sys
sys.dont_write_bytecode = True

from .base import BaseObject


class Domain(BaseObject):

    """DigitalOcean droplet domain object"""

    name, ttl, zone_file = (None,) * 3
    base_url = "https://api.digitalocean.com/v2/domains/"

    def __repr__(self):
        return "Domain %s" % self.name

    def __str__(self):
        return "Domain %s" % self.name

    @classmethod
    @set_caller
    def create(cls, name, ip_address):
        """Domain creation helper method"""
        payload = {
            "url": cls.base_url,
            "method": "post",
            "data": {
                "name": name,
                "ip_address": ip_address
            },
            "return_json": False
        }
        response = cls.client.api_request(**payload)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 201:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return Domain(**response.json().get("domain"))

    @classmethod
    @set_caller
    def get(cls, name):
        """Domain information fetch helper method"""
        url = "%s%s" % (cls.base_url, name)
        response = cls.client.api_request(url=url, return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 200:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return Domain(**response.json().get("domain"))

    @classmethod
    @set_caller
    def get_all(cls):
        """
        Get all domain maps generated through DigitalOcean's DNS.
        :rtype: list<Domain>
        """
        response = cls.client.api_request(url=cls.base_url,
                                         return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 200:
            message = response.json().get("message")
            raise InvalidArgumentError(message)
        domains = response.json().get("domains", [])
        return [Domain(**domain) for domain in domains]

    @classmethod
    @set_caller
    def delete(cls, name):
        """
        Domain mapping delete helper method
        :param name: Domain name
        :type  name: basestring
        :rtype: dict
        """
        url = "%s%s" % (cls.base_url, name)
        response = cls.client.api_request(url=url,
                                          method="delete",
                                          return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 204:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return {
            "message": "Successfully initiated domain mapping delete"
        }
