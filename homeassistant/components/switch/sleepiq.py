"""
Demo platform that has two fake switches.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import logging
from datetime import timedelta

from homeassistant.components import sleepiq
from homeassistant.components.switch import SwitchDevice
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['sleepiq']

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=15)

LIGHT_NAMES = {
    1: "Right Night Stand",
    2: "Left Night Stand",
    3: "Right Night Light",
    4: "Left Night Light",
}

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the SleepIQ switches."""
    if discovery_info is None:
        return

    data = sleepiq.DATA

    from sleepyq import Sleepyq

    client = sleepiq.CLIENT

    dev = list()
    for bed_id, _ in data.beds.items():
        if getattr(client.foundation_features(bed_id), 'HasUnderbedLight'):
            for light in range(1, 5):
                #_LOGGER.debug(light)
                light_data = client.get_light(bed_id, light)
                dev.append(BedSwitch(light_data, data.beds, client))
    add_devices(dev)

class BedSwitch(SwitchDevice):

    def __init__(self, sleepiq_data, beds, client):
        """Initialize the sensor."""
        self._bed_id = sleepiq_data.bedId
        self._light = sleepiq_data.outlet
        self.sleepiq_data = sleepiq_data
        self.client = client
        self._icon = None
        self.type = sleepiq.SWITCH
        self._state = sleepiq_data.setting
        self._name = 'SleepNumber {} {}'.format(
                beds[sleepiq_data.bedId].name, LIGHT_NAMES[sleepiq_data.outlet])
        self.update()

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from SleepIQ and updates the states."""
        light = self.client.get_light(self._bed_id, self._light)
        if light == False:
            return
        self._state = light.setting

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.client.set_light(self._bed_id, self._light, 1)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.client.set_light(self._bed_id, self._light, 0)
        self._state = False
        self.schedule_update_ha_state()

