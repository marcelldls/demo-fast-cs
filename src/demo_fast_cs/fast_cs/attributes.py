import logging as log
from typing import Awaitable, Callable, Generic, Optional, TypeAlias, TypeVar

ATTRIBUTE_TYPES = (
    int,
    float,
)

T = TypeVar("T", int, float)

AttrCallback: TypeAlias = Callable[[T], Awaitable[None]]


class AttrRead(Generic[T]):
    def __init__(self, dtype: type[T]) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype: type[T] = dtype
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

    @property
    def dtype(self) -> type[T]:
        return self._dtype


class AttrWrite(Generic[T]):
    def __init__(self, dtype: type[T]) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype: type[T] = dtype
        self._process_callback: Optional[AttrCallback[T]] = None

    async def process(self, value: T) -> None:
        if self._process_callback is not None:
            await self._process_callback(self._dtype(value))
        else:
            log.warning(f"Process callback is not set for {self}")

    def set_process_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._process_callback = callback

    @property
    def dtype(self) -> type[T]:
        return self._dtype


class AttrReadWrite(Generic[T]):
    def __init__(self, dtype: type[T]) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype: type[T] = dtype
        self._value: T = dtype()
        self._update_callback: Optional[AttrCallback[T]] = None
        self._process_callback: Optional[AttrCallback[T]] = None

    def get(self) -> T:
        return self._value

    async def set(self, value: T) -> None:
        self._value = self._dtype(value)

        if self._update_callback is not None:
            await self._update_callback(value)
        else:
            log.warning(f"Update callback is not set for {self}")

    async def process(self, value: T) -> None:
        await self.set(value)

        if self._process_callback is not None:
            await self._process_callback(self._value)
        else:
            log.warning(f"Process callback is not set for {self}")

    def set_update_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._update_callback = callback

    def set_process_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._process_callback = callback

    @property
    def dtype(self) -> type[T]:
        return self._dtype