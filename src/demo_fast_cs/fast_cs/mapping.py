from dataclasses import dataclass

from .api_methods import APIMethod
from .controller import BaseController, Controller


@dataclass
class SingleMapping:
    controller: BaseController
    methods: list[APIMethod]


class Mapping:
    def __init__(self, controller: Controller):
        self._generate_mapping(controller)

    @staticmethod
    def get_api_methods(controller: BaseController):
        methods = [getattr(controller, method_name) for method_name in dir(controller)]
        return [method for method in methods if isinstance(method, APIMethod)]

    def _generate_mapping(self, controller: Controller):
        self._controller_mapping = SingleMapping(
            controller, self.get_api_methods(controller)
        )

        self._sub_controller_mappings: list[SingleMapping] = []
        for sub_controller in controller.get_sub_controllers():
            self._sub_controller_mappings.append(
                SingleMapping(sub_controller, self.get_api_methods(sub_controller))
            )

    def __str__(self):
        result = f"Top-level mapping: {self._controller_mapping}\n"
        result += "Sub-controller mappings:\n"
        for sub_mapping in self._sub_controller_mappings:
            result += f"{sub_mapping}\n"
        return result

    def get_controller_mapping(self):
        return self._controller_mapping

    def get_sub_controller_mappings(self):
        return self._sub_controller_mappings
