from dataclasses import dataclass
from typing import Optional

from ..fast_cs.mapping import Mapping


@dataclass
class EpicsIOCOptions:
    terminal: bool = False


class EpicsIOC:
    def __init__(self, mapping: Mapping):
        self._mapping = mapping

    async def run(self, options: Optional[EpicsIOCOptions] = None) -> None:
        if options is None:
            options = EpicsIOCOptions()
