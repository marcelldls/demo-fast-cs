from __future__ import annotations

from copy import copy

from .api_methods import APIMethod


class BaseController:
    def __init__(self) -> None:
        self._bind_api_methods()

    def _bind_api_methods(controller: BaseController):
        for method_name in dir(controller):
            method = getattr(controller, method_name)
            if isinstance(method, APIMethod):
                bound_method: APIMethod = copy(method)
                bound_method.set_bound_instance(controller)
                setattr(controller, method_name, bound_method)


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
