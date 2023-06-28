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

    def get(self) -> Any:
        # TODO: How to best handle these methods which should never get called?
        return self._dtype()

    def set(self, val: Any) -> None:
        pass

    @property
    def dtype(self):
        return self._dtype


class AttributeInstance:
    def __init__(self, attribute: Attribute) -> None:
        self._attribute = attribute
        self._val = attribute.dtype()

    def get(self) -> Any:
        return self._val

    def set(self, val: Any) -> None:
        self._val = self._attribute.dtype(val)

    @property
    def dtype(self):
        return self._attribute.dtype
