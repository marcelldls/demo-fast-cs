from dataclasses import dataclass
from typing import NamedTuple

from .api_methods import APIMethod
from .attributes import Attribute
from .controller import BaseController, Controller

MethodData = NamedTuple("MethodData", (("name", str), ("method", APIMethod)))
AttributeData = NamedTuple("AttributeData", (("name", str), ("attribute", Attribute)))


@dataclass
class SingleMapping:
    controller: BaseController
    methods: list[MethodData]
    attributes: list[AttributeData]


class Mapping:
    def __init__(self, controller: Controller):
        self._generate_mapping(controller)

    @staticmethod
    def _get_single_mapping(controller: BaseController) -> SingleMapping:
        methods = []
        attributes = []
        for attr_name in dir(controller):
            attr = getattr(controller, attr_name)
            if isinstance(attr, APIMethod):
                methods.append(MethodData(attr_name, attr))
            elif isinstance(attr, Attribute):
                attributes.append(AttributeData(attr_name, attr))

        return SingleMapping(controller, methods, attributes)

    def _generate_mapping(self, controller: Controller):
        self._controller_mapping = self._get_single_mapping(controller)

        self._sub_controller_mappings: list[SingleMapping] = []
        for sub_controller in controller.get_sub_controllers():
            self._sub_controller_mappings.append(
                self._get_single_mapping(sub_controller)
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
