import logging as log
from typing import Awaitable, Callable, Generic, Optional, TypeAlias, TypeVar

ATTRIBUTE_TYPES = (
    int,
    float,
)

T = TypeVar("T", int, float)

AttrCallback: TypeAlias = Callable[[T], Awaitable[None]]


class Attribute(Generic[T]):
    def __init__(self, dtype: type[T]) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype: type[T] = dtype

    @property
    def dtype(self) -> type[T]:
        return self._dtype


class AttrRead(Attribute[T]):
    def __init__(self, dtype: type[T]) -> None:
        super(AttrRead, self).__init__(dtype)
        self._value: T = dtype()
        self._update_callback: Optional[AttrCallback[T]] = None

    def get(self) -> T:
        return self._value

    async def set(self, value: T) -> None:
        self._value = self._dtype(value)

        if self._update_callback is not None:
            await self._update_callback(value)
        else:
            log.warning(f"Update callback is not set for {self}")

    def set_update_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._update_callback = callback


class AttrWrite(Attribute[T]):
    def __init__(self, dtype: type[T]) -> None:
        super(AttrWrite, self).__init__(dtype)
        self._process_callback: Optional[AttrCallback[T]] = None

    async def process(self, value: T) -> None:
        if self._process_callback is not None:
            await self._process_callback(self._dtype(value))
        else:
            log.warning(f"Process callback is not set for {self}")

    def set_process_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._process_callback = callback


class AttrReadWrite(AttrWrite[T], AttrRead[T]):
    def __init__(self, dtype: type[T]) -> None:
        super(AttrReadWrite, self).__init__(dtype)

    async def process(self, value: T) -> None:
        await self.set(value)

        await super(AttrReadWrite, self).process(value)
