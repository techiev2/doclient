#! coding=utf-8

import sys
sys.dont_write_bytecode = True
from json import dumps as json_dumps
from re import compile as re_compile, match as re_match
from ast import literal_eval

import requests

from .droplet import Droplet
from .errors import APIAuthError, InvalidArgumentError


class DOClient(object):

    """DigitalOcean APIv2 client"""

    droplet_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets?page=1&per_page=100"
    ])

    power_onoff_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets/%s/actions"
    ])

    poweroff_data = json_dumps({
        "type": "power_off"
    })

    poweron_data = json_dumps({
        "type": "power_on"
    })

    powercycle_data = json_dumps({
        "type": "power_cycle"
    })

    def __init__(self, token):
        """DigitalOcean APIv2 client init"""
        self._token = token
        self.droplets = []
        self.get_droplets()

    def __repr__(self):
        return "DigitalOcean API Client %s" % self.id

    def __str__(self):
        return "DigitalOcean API Client %s" % self.id

    @property
    def token(self):
        """
        DigitalOcean API client token property.
        Used with request headers as Authorization Bearer
        """
        return self._token

    # [TODO] Add a setter for request_headers to allow for additional
    # headers' addition to DOClient.
    @property
    def request_headers(self):
        """
        DigitalOcean API client base request headers property.
        Used with all of the DOClient's HTTP requests.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % self.token
        }

    def get_droplets(self):
        """
        Get list of droplets for the requested account.
        :raises: APIAuthError
        """
        response = requests.get(url=self.droplet_url,
                                headers=self.request_headers)

        if response.status_code != 200:
            raise APIAuthError(
                "Unable to fetch data from DigitalOcean API.")

        droplets = response.json().get("droplets", [])

        for droplet in droplets:
            droplet = Droplet(**{
                "name": droplet.get("name"),
                "_id": droplet.get("id"),
                "client": self
            })
            self.droplets.append(droplet) 

    def poweroff_instance(self, instance_id):
        """
        Instance power off helper method.
        :param instance_id: ID of the instance to turn off.
        :type  instance_id: int, basestring<int>
        :rtype: NoneType
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweroff_data)

    def poweron_instance(self, instance_id):
        """
        Instance power on helper method.
        :param instance_id: ID of the instance to turn on.
        :type  instance_id: int, basestring<int>
        :rtype: NoneType
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweron_data)

    def powercycle_instance(self, instance_id):
        """
        Instance power cycle helper method.
        :param instance_id: ID of the instance to powercycle.
        :type  instance_id: int, basestring<int>
        :rtype: NoneType
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweron_data)

    def get_droplet(self, droplet_id):
        """
        Basic droplet find helper.
        Filters out droplets which match the provided droplet id.
        [Essentially one droplet].
        :param droplet_id: ID to match droplets against.
        :type  matcher: int, basestring
        :rtype: list<Droplet>
        """

        if not isinstance(droplet_id, int):
            droplet_id = droplet_id or ""
            try:
                droplet_id = literal_eval(str(droplet_id))
            except (TypeError, ValueError):
                droplet_id = None

        if not isinstance(droplet_id, int):
            raise InvalidArgumentError(
                "Method requires a valid integer droplet id")

        droplet = filter(lambda x: x._id==droplet_id,
                         self.droplets)
        return droplet[0] if droplet else None

    def filter_droplets(self, matcher=None):
        """
        Basic droplet filter helper.
        Filters out droplets which pass a substring match on the name
        for the provided matcher.
        Matcher defaults to empty string and returns all instances
        :param matcher: Token to match droplet names against.
        :type  matcher: basestring
        :rtype: list<Droplet>
        """
        if matcher is None:
            return self.droplets

        if not isinstance(matcher, basestring):
            raise InvalidArgumentError(
                "Method requires a string filter token")

        matcher = re_compile(".*?%s.*?" % matcher)
        return filter(
            lambda x: re_match(matcher, x.name) is not None,
            self.droplets)


if __name__ == "__main__":
    pass
