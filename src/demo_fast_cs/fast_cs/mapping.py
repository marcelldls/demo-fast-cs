from .api_methods import APIMethod


class Mapping:
    def __init__(self, methods: list[APIMethod]):
        self._methods = methods

    def get_methods(self):
        return self._methods
