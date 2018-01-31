"""
Support for SleepIQ sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sleepiq/
"""
import logging
from datetime import timedelta

from homeassistant.components import sleepiq
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['sleepiq']
ICON = 'mdi:hotel'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the SleepIQ sensors."""
    if discovery_info is None:
        return

    data = sleepiq.DATA
    data.update()

    client = sleepiq.CLIENT

    dev = list()
    for bed_id, _ in data.beds.items():
        for side in sleepiq.SIDES:
            favsleepnumber_data = client.get_favsleepnumber(bed_id)
            if type(SleepNumberSensor(data, bed_id, side).name) != type(None):
                dev.append(SleepNumberSensor(data, bed_id, side))
                dev.append(SleepNumberFavSensor(favsleepnumber_data, data, bed_id, side, client))
    add_devices(dev)


class SleepNumberSensor(sleepiq.SleepIQSensor):
    """Implementation of a SleepIQ sensor."""

    def __init__(self, sleepiq_data, bed_id, side):
        """Initialize the sensor."""
        sleepiq.SleepIQSensor.__init__(self, sleepiq_data, bed_id, side)

        self._state = None
        self.type = sleepiq.SLEEP_NUMBER
        self._name = sleepiq.SENSOR_TYPES[self.type]

        self.update()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Get the latest data from SleepIQ and updates the states."""
        sleepiq.SleepIQSensor.update(self)
        if type(self.side) != type(None):
            self._state = self.side.sleep_number

class SleepNumberFavSensor(Entity):
    """Implementation of a SleepIQ sensor."""

    def __init__(self, sleepiq_fav_data, sleepiq_data, bed_id, side, client):
        """Initialize the sensor."""
        self._bed_id = bed_id
        self.bed = sleepiq_data.beds[self._bed_id]
        self._side = side
        self.side = getattr(self.bed, self._side)
        self.sleepiq_fav_data = sleepiq_fav_data
        self.client = client
        self.type = sleepiq.FAV_SLEEP_NUMBER
        self._state = getattr(sleepiq_fav_data, side)
        self._name = sleepiq.SENSOR_TYPES[self.type]
        self.update()

    @property
    def name(self):
        """Return the name of the sleeper."""
        if type(self.side) != type(None):
            return 'SleepNumber {} {} {}'.format(
                self.bed.name, self.side.sleeper.first_name, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from SleepIQ and updates the states."""
        favsleepnumber = self.client.get_favsleepnumber(self._bed_id)
        if favsleepnumber == False:
            return
        self._state = getattr(favsleepnumber, self._side)

