from __future__ import annotations

from .api_methods import APIMethod
from .mapping import Mapping


class Controller:
    def __init__(self) -> None:
        self.__sub_controllers: list[SubController] = []

    def register(self, controller: SubController):
        self.__sub_controllers.append(controller)

    @staticmethod
    def get_api_methods(controller):
        methods = [getattr(controller, method_name) for method_name in dir(controller)]
        return [method for method in methods if isinstance(method, APIMethod)]

    def get_mapping(self) -> Mapping:
        # TODO: Ensure all methods are stored alongside relevant object
        api_methods = []
        for controller in [self, *self.__sub_controllers]:
            api_methods += self.get_api_methods(controller)

        return Mapping(api_methods)


class SubController:
    def __init__(self, path: str) -> None:
        self._path: str = path
