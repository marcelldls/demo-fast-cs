from enum import Enum
from typing import Awaitable, Callable, Generic, Optional, TypeAlias, TypeVar

ATTRIBUTE_TYPES = (
    int,
    float,
)

T = TypeVar("T", int, float)

AttrCallback: TypeAlias = Callable[[T], Awaitable[None]]


class AttrMode(Enum):
    READ = 1
    WRITE = 2
    READ_WRITE = 3


class Attribute(Generic[T]):
    def __init__(self, dtype: type[T], mode: AttrMode) -> None:
        assert (
            dtype in ATTRIBUTE_TYPES
        ), f"Attribute type must be one of {ATTRIBUTE_TYPES}, received type {dtype}"
        self._dtype: type[T] = dtype
        self._mode: AttrMode = mode

    @property
    def dtype(self) -> type[T]:
        return self._dtype

    @property
    def mode(self) -> AttrMode:
        return self._mode


class AttrRead(Attribute[T]):
    def __init__(self, dtype: type[T]) -> None:
        super().__init__(dtype, AttrMode.READ)  # type: ignore
        self._value: T = dtype()
        self._update_callback: Optional[AttrCallback[T]] = None

    def get(self) -> T:
        return self._value

    async def set(self, value: T) -> None:
        self._value = self._dtype(value)

        if self._update_callback is not None:
            await self._update_callback(self._value)

    def set_update_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._update_callback = callback


class AttrWrite(Attribute[T]):
    def __init__(self, dtype: type[T]) -> None:
        super().__init__(dtype)  # type: ignore
        self._process_callback: Optional[AttrCallback[T]] = None

    async def process(self, value: T) -> None:
        if self._process_callback is not None:
            await self._process_callback(self._dtype(value))

    def set_process_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._process_callback = callback


class AttrReadWrite(AttrWrite[T], AttrRead[T]):
    def __init__(self, dtype: type[T]) -> None:
        super().__init__(dtype)  # type: ignore
        self._mode = AttrMode.READ_WRITE

    async def process(self, value: T) -> None:
        await self.set(value)

        await super().process(value)  # type: ignore
