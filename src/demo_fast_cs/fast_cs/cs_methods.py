from asyncio import iscoroutinefunction
from enum import Enum
from inspect import Signature, getdoc, signature
from typing import Awaitable, Callable, TypeAlias

from .exceptions import FastCSException

ScanCallback: TypeAlias = Callable[..., Awaitable[None]]


class MethodType(Enum):
    scan = "scan"
    put = "put"


class MethodInfo:
    def __init__(self, type: MethodType, fn: Callable, **kwargs) -> None:
        self._type = type
        self._store_method_details(fn)
        self._validate_method(type, fn)

        self.kwargs = kwargs

    def _validate_method(self, type: MethodType, fn: Callable) -> None:

        if self.return_type not in (None, Signature.empty):
            raise FastCSException("Method return type must be None or empty")

        if not iscoroutinefunction(fn):
            raise FastCSException("Method must be async function")

        match type:
            case MethodType.scan:
                self._validate_scan_method(fn)
            case MethodType.put:
                self._validate_put_method(fn)

    def _validate_scan_method(self, fn: Callable) -> None:
        if not len(self.parameters) == 1:
            raise FastCSException("Scan method cannot have arguments")

    def _validate_put_method(self, fn: Callable) -> None:
        if not len(self.parameters) == 2:
            raise FastCSException("Put method can only take one argument")

    def _store_method_details(self, fn):
        self._docstring = getdoc(fn)

        sig = signature(fn)
        self._parameters = sig.parameters
        self._return_type = sig.return_annotation

    @property
    def type(self):
        return self._type

    @property
    def return_type(self):
        return self._return_type

    @property
    def parameters(self):
        return self._parameters

    @property
    def docstring(self):
        return self._docstring
