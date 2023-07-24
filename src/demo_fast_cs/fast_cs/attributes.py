from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeAlias,
    TypeVar,
)

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


class Sender(Protocol):
    async def put(self, controller: Any, value: Any) -> None:
        pass


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
    def __init__(self, dtype: type[T], sender: Sender | None = None) -> None:
        super().__init__(dtype)  # type: ignore
        self._process_callback: Optional[AttrCallback[T]] = None
        self._sender = sender

    async def process(self, value: T) -> None:
        if self._process_callback is not None:
            await self._process_callback(self._dtype(value))

    def set_process_callback(self, callback: Optional[AttrCallback[T]]) -> None:
        self._process_callback = callback

    def has_process_callback(self) -> bool:
        return self._process_callback is not None

    @property
    def sender(self) -> Sender | None:
        return self._sender


class AttrReadWrite(AttrWrite[T], AttrRead[T]):
    def __init__(self, dtype: type[T], sender: Sender | None = None) -> None:
        super().__init__(dtype, sender)  # type: ignore
        self._mode = AttrMode.READ_WRITE

    async def process(self, value: T) -> None:
        await self.set(value)

        await super().process(value)  # type: ignore
