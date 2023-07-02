from typing import Optional

from ..fast_cs.mapping import Mapping
from .docs import EpicsDocs, EpicsDocsOptions
from .gui import EpicsGUI, EpicsGUIOptions
from .ioc import EpicsIOC


class EpicsBackend:
    def __init__(self, mapping: Mapping):
        self._mapping = mapping

    def create_docs(self, options: Optional[EpicsDocsOptions] = None) -> None:
        docs = EpicsDocs(self._mapping)
        docs.create_docs(options)

    def create_gui(self, options: Optional[EpicsGUIOptions] = None) -> None:
        gui = EpicsGUI(self._mapping)
        gui.create_gui(options)

    def get_ioc(self) -> EpicsIOC:
        return EpicsIOC(self._mapping)
