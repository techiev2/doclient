#! coding=utf-8

import sys
sys.dont_write_bytecode = True
from json import dumps as json_dumps
from re import compile as re_compile, match as re_match
from ast import literal_eval

import requests

from .droplet import Droplet, Kernel, Snapshot
from .errors import APIAuthError, InvalidArgumentError
from .user import DOUser


class DOClient(object):

    """DigitalOcean APIv2 client"""

    _id = None

    droplet_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets?page=1&per_page=100"
    ])

    power_onoff_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets/%s/actions"
    ])

    userinfo_url = "https://api.digitalocean.com/v2/account"

    droplet_base_url = "https://api.digitalocean.com/v2/droplets/"
    droplet_snapshot_url = "".join([
        droplet_base_url,
        "%s/snapshots?page=1&per_page=100"
    ])
    droplet_kernels_url = "".join([
        droplet_base_url,
        "%s/kernels?page=1&per_page=100"
    ])

    # Metadata

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
        self.droplets = None
        self.get_droplets()

    @property
    def id(self):
        return self._id

    @property
    def user_information(self):
        response = requests.get(url=self.userinfo_url,
                            headers=self.request_headers)
        if not response.status_code == 200:
            raise APIAuthError("Unable to authenticate session")
        return DOUser(**response.json().get("account"))

    def __repr__(self):
        return "DigitalOcean API Client %s" % self._id

    def __str__(self):
        return "DigitalOcean API Client %s" % self._id

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
        _droplets = []

        for droplet in droplets:
            droplet = Droplet(**{
                "name": droplet.get("name"),
                "_id": droplet.get("id"),
                "client": self
            })
            _droplets.append(droplet)

        self.droplets = _droplets

    def poweroff_droplet(self, instance_id):
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

    def poweron_droplet(self, instance_id):
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

    def powercycle_droplet(self, instance_id):
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

    def get_droplet_snapshots(self, droplet_id):
        """
        DigitalOcean APIv2 droplet snapshots helper method.
        Returns a list of snapshots created for the requested droplet.
        :param droplet_id: ID of droplet to get snapshots for.
        :type  droplet_id: int
        :rtype: list<dict>
        """
        url = self.droplet_snapshot_url % droplet_id
        response = requests.get(url=url,
                                headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        snapshots = response.json().get("snapshots")
        return [Snapshot(**snapshot) for snapshot in snapshots]

    def get_droplet_kernels(self, droplet_id):
        """
        DigitalOcean APIv2 droplet kernels helper method.
        Returns a list of kernels available for the requested droplet.
        :param droplet_id: ID of droplet to get available kernels for.
        :type  droplet_id: int
        :rtype: list<dict>
        """
        url = self.droplet_kernels_url % droplet_id
        response = requests.get(url=url,
                                headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        kernels = response.json().get("kernels")
        return [Kernel(**kernel) for kernel in kernels]

    def delete_droplet(self, droplet_id):
        """
        DigitalOcean APIv2 droplet delete method.
        Deletes a requested droplet.
        :param droplet_id: ID of droplet to delete.
        :type  droplet_id: int
        :rtype: dict
        """
        droplet = self.get_droplet(droplet_id)
        if not droplet:
            raise InvalidArgumentError("Unknown droplet")
        url = "%s%s" % (self.droplet_base_url, droplet_id)
        response = requests.delete(url=url,
                                   headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        return {"message": "Successfully deleted droplet" % droplet}


if __name__ == "__main__":
    pass
