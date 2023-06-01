from __future__ import annotations


class Controller:
    def __init__(self) -> None:
        self.__sub_controllers: list[SubController] = []

    def register_sub_controller(self, controller: SubController):
        self.__sub_controllers.append(controller)

    def get_sub_controllers(self) -> list[SubController]:
        return self.__sub_controllers


class SubController:
    def __init__(self, path: str) -> None:
        self._path: str = path
