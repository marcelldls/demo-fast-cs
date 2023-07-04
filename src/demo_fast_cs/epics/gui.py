from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from pvi._format import Formatter
from pvi._format.base import Formatter
from pvi._yaml_utils import deserialize_yaml
from pvi.device import (
    Component,
    Device,
    Grid,
    Group,
    SignalR,
    SignalRW,
    SignalW,
    TextRead,
    TextWrite,
    Tree,
)

from ..fast_cs.attributes import Attribute, AttrMode
from ..fast_cs.exceptions import FastCSException
from ..fast_cs.mapping import Mapping

FORMATTER_YAML = Path.cwd() / ".." / "pvi" / "formatters" / "dls.bob.pvi.formatter.yaml"


class EpicsGUIFormat(Enum):
    bob = ".bob"
    edl = ".edl"


@dataclass
class EpicsGUIOptions:
    output_path: Path = Path.cwd() / "output.bob"
    file_format: EpicsGUIFormat = EpicsGUIFormat.bob


class EpicsGUI:
    def __init__(self, mapping: Mapping) -> None:
        self._mapping = mapping

    @staticmethod
    def _get_pv(attr_path: str, name: str):
        if attr_path:
            attr_path = ":" + attr_path
        attr_path += ":"

        pv = attr_path.upper() + name.title()

        return pv

    @classmethod
    def _get_attribute_component(cls, attr_path: str, name: str, attribute: Attribute):
        pv = cls._get_pv(attr_path, name)
        name = name.title()

        match attribute.mode:
            case AttrMode.READ:
                return SignalR(name, pv, TextRead())
            case AttrMode.WRITE:
                return SignalW(name, pv, TextWrite())
            case AttrMode.READ_WRITE:
                return SignalRW(name, pv, TextWrite(), pv + "_RBV", TextRead())

    def create_gui(self, options: Optional[EpicsGUIOptions] = None) -> None:
        if options is None:
            options = EpicsGUIOptions()

        if options.file_format is EpicsGUIFormat.edl:
            raise FastCSException("FastCS does not support .edl screens.")

        assert options.output_path.suffix == options.file_format.value

        formatter = deserialize_yaml(Formatter, FORMATTER_YAML)

        components: Tree[Component] = []
        for single_mapping in self._mapping.get_controller_mappings():
            attr_path = single_mapping.controller.path

            group_name = type(single_mapping.controller).__name__ + " " + attr_path
            group_children: list[Component] = []

            for attr_data in single_mapping.attributes:
                group_children.append(
                    self._get_attribute_component(
                        attr_path,
                        attr_data.name,
                        attr_data.attribute,
                    )
                )

            components.append(Group(group_name, Grid(), group_children))

        device = Device("Simple Device", children=components)

        formatter.format(device, "$(P)", options.output_path)
