from demo.controllers import TempRampController
from demo.device import DeviceInterface
from fastcs import Controller


class XZ123TempController(Controller):
    ramp_controllers: list[TempRampController] = []

    def __init__(self, num_ramp_controllers):
        super().__init__("temp")
        device_interface = DeviceInterface(num_ramp_controllers)
        for i in range(num_ramp_controllers):
            self.ramp_controllers.append(
                TempRampController(i, device_interface)
            )
