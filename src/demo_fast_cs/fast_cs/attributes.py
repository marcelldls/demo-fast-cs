from typing import Any

ATTRIBUTE_TYPES = (
    int,
    float,
)


class Attribute:
    def __init__(self, dtype: type) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype = dtype

    @property
    def dtype(self):
        return self._dtype


class AttributeInstance:
    def __init__(self, attribute: Attribute, name: str) -> None:
        self._attribute = attribute
        self._val = attribute.dtype()
        self._name = name

    def get(self) -> Any:
        return self._val

    def set(self, val: Any) -> None:
        self._val = self._attribute.dtype(val)

    @property
    def dtype(self):
        return self._attribute.dtype

    @property
    def name(self):
        return self._name
