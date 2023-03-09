from demo.device import DeviceInterface
from fastcs import BaseSettings, Controller, put, scan


class RampSettings(BaseSettings):
    device_ip: str


def get_ramp_settings():
    return RampSettings()


class TempRampController(Controller):
    start: float
    end: float

    def __init__(self, index, device_interface):
        super().__init__(f"ramp{index:02d}")

        self._settings: RampSettings = get_ramp_settings()
        self._device_interface: DeviceInterface = device_interface
        self._index: int = index

    @scan(2)
    def update(self):
        self.start = self._device_interface.get_start(self._index)
        self.end = self._device_interface.get_end(self._index)

    @put("start")
    def put_start(self, value: float):
        self._device_interface.set_start(self._index, value)
        self.update()

    @put("end")
    def put_end(self, value: float):
        self._device_interface.set_start(self._index, value)
        self.update()
