"""Python library for interacting with Inception devices."""
import asyncio


# import json
# import os
import aiohttp
import requests



import logging
from urllib.parse import urljoin

from .area import Area
from .zone import Zone
from .const import AreaMode
from .utils import async_request
from .websocket import AIOWSClient

_LOGGER = logging.getLogger(__name__)


USERID = ""
HEADERS = {"Accept": "application/json", "Cookie": "LoginSessId=" + USERID}
__author__ = "Chris Ramon PCX Networks <chris@pcx.net.au>"


class Error(Exception):
    """Base class for exceptions in this module."""


class Client:
    """API wrapper for Inception Alarm Panels."""

    def __init__(self, host, websession, user, passwd, userpin):
        """Initialize the client connection."""
        self.host = host
        self.websession = websession
        self.base_url = "http://" + host + "/api/v1/"
        self.username = user
        self.passwd = passwd
        self.pin = userpin
        self.login()

    def login(self):
        """Login to panel"""
        global HEADERS, USERID
        url = self.base_url + "authentication/login"

        payload = (
            '{\n\t"Username": "'
            + self.username
            + '",\n\t"Password": "'
            + self.passwd
            + '"\n}'
        )
        response = requests.request("POST", url, data=payload, headers=HEADERS)
        authdata = response.json()
        userid = authdata["UserID"]
        HEADERS["Cookie"] = "LoginSessId=" + userid

    async def get_status(self):
        """Query the device status. Returns JSON of the device internal state."""
        url = self.base_url + "system-info"
        try:
            async with self.websession.get(url, timeout=10, headers=HEADERS) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def get_input(self, input_id=None):
        """Get Inputs"""
        url = self.base_url + "control/input/"
        if input_id is None:
            input_id = "summary"
        try:
            async with self.websession.get(
                url + input_id, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def get_inputstate(self, input_id):
        """Get Input States"""
        url = self.base_url + "control/input/"

        try:
            async with self.websession.get(
                url + input_id + "/state", timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def post_controlinput(self, input_id, command):
        # must be Isolate or DeIsolate
        if command is not "Isolate" and command is not "DeIsolate":
            raise Error("Incorrect Command")
        url = self.base_url + "control/input/" + input_id + "/activity"

        payload = {
            "Type": "ControlInput",
            "InputControlType": command,
            "Entity": input_id,
            "ExecuteAsOtherUser": "True",
            "OtherUserPIN": self.pin,
        }

        try:
            async with self.websession.post(
                url, json=payload, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise Client.ClientError(err)

    async def get_area(self, area_id=None):
        url = self.base_url + "control/area/"
        if area_id is None:
            area_id = "summary"
        try:
            async with self.websession.get(
                url + area_id, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def post_controlarea(self, area_id, command):
        # must be Arm , Disarm,
        if command is not "Arm" and command is not "Disarm":
            raise Error("Incorrect Command")
        url = self.base_url + "control/area/" + area_id + "/activity"

        payload = {
            "Type": "ControlArea",
            "AreaControlType": command,
            "Entity": area_id,
            "ExitDelay": "True",
            "ExecuteAsOtherUser": "True",
            "OtherUserPIN": self.pin,
        }
        if command == "Arm":
            payload["ExitDelay"] = "True"
        try:
            async with self.websession.post(
                url, json=payload, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise Client.ClientError(err)

    async def get_door(self, door_id=None):
        url = self.base_url + "control/door/"
        if door_id is None:
            door_id = "summary"
        try:
            async with self.websession.get(
                url + door_id, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def post_controldoor(self, door_id, command):
        # must be Lock, Unlock, Open, Lockout, Reinstate
        if (
            command is not "Lock"
            and command is not "Unlock"
            and command is not "Open"
            and command is not "Lockout"
            and command is not "Reinstate"
        ):
            raise Error("Incorrect Command")
        url = self.base_url + "control/door/" + door_id + "/activity"

        payload = {
            "Type": "ControlDoor",
            "DoorControlType": command,
            "Entity": door_id,
            "ExecuteAsOtherUser": "True",
            "OtherUserPIN": self.pin,
        }
        try:
            async with self.websession.post(
                url, json=payload, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise Client.ClientError(err)

    async def get_output(self, output_id=None):
        url = self.base_url + "control/output/"
        if output_id is None:
            output_id = "summary"
        try:
            async with self.websession.get(
                url + output_id, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.login()
            raise Client.ClientError(err)

    async def post_controloutput(self, output_id, command):
        # must be Off, On, Toggle
        if command is not "Off" and command is not "On" and command is not "Toggle":
            raise Error("Incorrect Command")
        url = self.base_url + "control/output/" + output_id + "/activity"

        payload = {
            "Type": "ControlOutput",
            "OutputControlType": command,
            "Entity": output_id,
            "ExecuteAsOtherUser": "True",
            "OtherUserPIN": self.pin,
        }
        try:
            async with self.websession.post(
                url, json=payload, timeout=10, headers=HEADERS
            ) as resp:
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise Client.ClientError(err)

    class ClientError(Exception):
        """Generic Error."""



class SpcWebGateway:
    """Alarm system representation."""

    def __init__(self, loop, session, api_url, ws_url, async_callback):
        """Initialize the client."""
        self._loop = loop
        self._session = session
        self._api_url = api_url
        self._ws_url = ws_url
        self._areas = {}
        self._zones = {}
        self._websocket = None
        self._async_callback = async_callback

    @property
    def areas(self):
        """Retrieve all available areas."""
        return self._areas

    @property
    def zones(self):
        """Retrieve all available zones."""
        return self._zones

    def start(self):
        """Connect websocket to SPC Web Gateway."""
        self._websocket = AIOWSClient(loop=self._loop,
                                      session=self._session,
                                      url=self._ws_url,
                                      async_callback=self._async_ws_handler)
        self._websocket.start()

    async def async_load_parameters(self):
        """Fetch area and zone info from SPC to initialize."""
        zones = await self._async_get_data('zone')
        areas = await self._async_get_data('area')

        if not zones or not areas:
            return False

        for spc_area in areas:
            area = Area(self, spc_area)
            area_zones = [Zone(area, z) for z in zones
                          if z['area'] == spc_area['id']]
            area.zones = area_zones
            self._areas[area.id] = area
            self._zones.update({z.id: z for z in area_zones})

        return True

    async def change_mode(self, area, new_mode):
        """Set/unset/part set an area."""
        if not isinstance(new_mode, AreaMode):
            raise TypeError("new_mode must be an AreaMode")

        AREA_MODE_COMMAND_MAP = {
            AreaMode.UNSET: 'unset',
            AreaMode.PART_SET_A: 'set_a',
            AreaMode.PART_SET_B: 'set_b',
            AreaMode.FULL_SET: 'set'
        }
        if isinstance(area, Area):
            area_id = area.id
        else:
            area_id = area

        url = urljoin(self._api_url, "spc/area/{area_id}/{command}".format(
            area_id=area_id, command=AREA_MODE_COMMAND_MAP[new_mode]))

        return await async_request(self._session.put, url)

    async def _async_ws_handler(self, data):
        """Process incoming websocket message."""
        sia_message = data['data']['sia']
        spc_id = sia_message['sia_address']
        sia_code = sia_message['sia_code']

        _LOGGER.debug("SIA code is %s for ID %s", sia_code, spc_id)

        if sia_code in Area.SUPPORTED_SIA_CODES:
            entity = self._areas.get(spc_id, None)
            resource = 'area'
        elif sia_code in Zone.SUPPORTED_SIA_CODES:
            entity = self._zones.get(spc_id, None)
            resource = 'zone'
        else:
            _LOGGER.debug("Not interested in SIA code %s", sia_code)
            return
        if not entity:
            _LOGGER.error("Received message for unregistered ID %s", spc_id)
            return

        data = await self._async_get_data(resource, entity.id)
        entity.update(data, sia_code)

        if self._async_callback:
            asyncio.ensure_future(self._async_callback(entity))

    async def _async_get_data(self, resource, id=None):
        """Get the data from the resource."""
        if id:
            url = urljoin(self._api_url, "spc/{}/{}".format(resource, id))
        else:
            url = urljoin(self._api_url, "spc/{}".format(resource))
        data = await async_request(self._session.get, url)
        if not data:
            return False
        if id and isinstance(data['data'][resource], list):
            # for some reason the gateway returns an array with a single
            # element for areas but not for zones...
            return data['data'][resource][0]
        elif id:
            return data['data'][resource]

        return [item for item in data['data'][resource]]
