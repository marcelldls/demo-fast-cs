from .api_methods import APIMethod
from .mapping import Mapping


class Controller:
    def __init__(self, path):
        self._path = path

    def get_mapping(self) -> Mapping:
        methods = [getattr(self, method_name) for method_name in dir(self)]

        api_methods = [method for method in methods if isinstance(method, APIMethod)]

        return Mapping(api_methods)
