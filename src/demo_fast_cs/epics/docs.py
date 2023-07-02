from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..fast_cs.mapping import Mapping


@dataclass
class EpicsDocsOptions:
    path: Path = Path.cwd()
    depth: Optional[int] = None


class EpicsDocs:
    def __init__(self, mapping: Mapping) -> None:
        self._mapping = mapping

    def create_docs(self, options: Optional[EpicsDocsOptions] = None) -> None:
        if options is None:
            options = EpicsDocsOptions()
