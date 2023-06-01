from functools import update_wrapper
from inspect import Signature, getdoc, signature
from typing import Any, Callable

from .exceptions import FastCSException


class APIMethod:
    def __init__(self, fn: Callable) -> None:
        self._fn = fn
        update_wrapper(self, fn)
        self.store_method_details(fn)

    def store_method_details(self, fn):
        self.help_message = getdoc(fn)

        sig = signature(fn)
        self._parameters = sig.parameters
        self._return_type = sig.return_annotation

    def get_return_type(self):
        return self._return_type

    def get_parameters(self):
        return self._parameters

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)


class UpdateMethod(APIMethod):
    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

        if self._return_type not in (bool, Signature.empty):
            raise FastCSException("Update method return type must be boolean or empty")

        if self._parameters:
            raise FastCSException("Update method cannot have parameters")


class GetMethod(APIMethod):
    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

        if self._parameters:
            raise FastCSException("Get method cannot have parameters")


class PutMethod(APIMethod):
    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

        if self._return_type not in (bool, Signature.empty):
            raise FastCSException("Put method return type must be boolean or empty")

        if not len(self._parameters) == 2:
            raise FastCSException("Put method can only take one additional argument")

    def get_value_type(self):
        return self._parameters[1].annotation
