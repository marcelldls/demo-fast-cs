from dataclasses import dataclass

from .api_methods import APIMethod
from .attributes import AttributeInstance
from .controller import BaseController, Controller


@dataclass
class SingleMapping:
    controller: BaseController
    methods: list[APIMethod]
    attributes: list[AttributeInstance]


class Mapping:
    def __init__(self, controller: Controller):
        self._generate_mapping(controller)

    @staticmethod
    def get_api_methods(controller: BaseController):
        attrs = [getattr(controller, attr) for attr in dir(controller)]
        methods = [attr for attr in attrs if isinstance(attr, APIMethod)]
        return methods

    @staticmethod
    def get_attributes(controller: BaseController):
        attrs = [getattr(controller, attr_name) for attr_name in dir(controller)]
        attributes = [attr for attr in attrs if isinstance(attr, AttributeInstance)]
        return attributes

    def _generate_mapping(self, controller: Controller):
        self._controller_mapping = SingleMapping(
            controller,
            self.get_api_methods(controller),
            self.get_attributes(controller),
        )

        self._sub_controller_mappings: list[SingleMapping] = []
        for sub_controller in controller.get_sub_controllers():
            self._sub_controller_mappings.append(
                SingleMapping(
                    sub_controller,
                    self.get_api_methods(sub_controller),
                    self.get_attributes(sub_controller),
                )
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
