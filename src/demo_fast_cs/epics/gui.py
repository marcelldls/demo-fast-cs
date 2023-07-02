from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from ..fast_cs.mapping import Mapping


class EpicsGUIFormat(Enum):
    bob = ".bob"
    edl = ".edl"


@dataclass
class EpicsGUIOptions:
    path: Path = Path.cwd()
    file_format: EpicsGUIFormat = EpicsGUIFormat.bob


class EpicsGUI:
    def __init__(self, mapping: Mapping) -> None:
        self._mapping = mapping

    def create_gui(self, options: Optional[EpicsGUIOptions] = None) -> None:
        if options is None:
            options = EpicsGUIOptions()
