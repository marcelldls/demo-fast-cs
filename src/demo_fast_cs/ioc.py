# from fastcs import Controller

# from demo_fast_cs.controllers import TempRampController


# class XZ123TempController(Controller):
#     ramp_controllers: list[TempRampController] = []

#     def __init__(self, num_ramp_controllers):
#         super().__init__("temp")
#         device_interface = DeviceInterface(num_ramp_controllers)
#         for i in range(num_ramp_controllers):
#             self.ramp_controllers.append(TempRampController(i, device_interface))
