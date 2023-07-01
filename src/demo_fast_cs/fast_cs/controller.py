from __future__ import annotations

from copy import copy

from .api_methods import APIMethod
from .attributes import Attribute


class BaseController:
    def __init__(self) -> None:
        self._bind_attrs()

    def _bind_attrs(self) -> None:
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, APIMethod):
                bound_method: APIMethod = copy(attr)
                bound_method.set_bound_instance(self)
                setattr(self, attr_name, bound_method)
            elif isinstance(attr, Attribute):
                new_attribute = copy(attr)
                setattr(self, attr_name, new_attribute)


class Controller(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.__sub_controllers: list[SubController] = []

    def register_sub_controller(self, controller: SubController):
        self.__sub_controllers.append(controller)

    def get_sub_controllers(self) -> list[SubController]:
        return self.__sub_controllers


class SubController(BaseController):
    def __init__(self, path: str) -> None:
        super().__init__()
        self._path: str = path
