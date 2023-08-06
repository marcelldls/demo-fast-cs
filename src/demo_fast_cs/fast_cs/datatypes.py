from dataclasses import dataclass
from typing import Awaitable, Callable, ClassVar, Generic, TypeVar

T = TypeVar("T", int, float, bool)
ATTRIBUTE_TYPES: tuple[type] = T.__constraints__  # type: ignore


AttrCallback = Callable[[T], Awaitable[None]]


class DataType(Generic[T]):
    dtype: ClassVar[type]


@dataclass(frozen=True)
class Int(DataType[int]):
    dtype: ClassVar[type] = int
    min: int | None = None
    max: int | None = None


@dataclass(frozen=True)
class Float(DataType[float]):
    dtype: ClassVar[type] = float
    min: float | None = None
    max: float | None = None


@dataclass(frozen=True)
class Bool(DataType[bool]):
    dtype: ClassVar[type] = bool
    zval: str = "OFF"
    oval: str = "ON"
