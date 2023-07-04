import asyncio
from dataclasses import dataclass
from typing import Optional, cast

from softioc import asyncio_dispatcher, builder, softioc

from ..fast_cs.attributes import (
    AttrCallback,
    Attribute,
    AttrMode,
    AttrRead,
    AttrReadWrite,
    AttrWrite,
)
from ..fast_cs.backend import get_initial_tasks, get_scan_tasks, link_process_tasks
from ..fast_cs.mapping import Mapping


@dataclass
class EpicsIOCOptions:
    terminal: bool = True


def create_and_link_read_pv(path: str, attr_name: str, attribute: AttrRead) -> None:
    attr_name = attr_name.title()
    pv_name = path.upper() + ":" + attr_name if path else attr_name
    ai = builder.aIn(pv_name)
    attribute.set_update_callback(ai.set)


def create_and_link_write_pv(path: str, attr_name: str, attribute: AttrWrite) -> None:
    attr_name = attr_name.title()
    pv_name = path.upper() + ":" + attr_name if path else attr_name
    pv_name += "_RBV"
    ao = builder.aOut(
        pv_name, always_update=True, on_update=lambda v: attribute.process(v)
    )


def _create_and_link_pvs(mapping: Mapping) -> None:
    for single_mapping in mapping.get_controller_mappings():
        path = single_mapping.controller.path
        for attr_name, attribute in single_mapping.attributes.items():
            match attribute.mode:
                case AttrMode.READ:
                    attribute = cast(AttrRead, attribute)
                    create_and_link_read_pv(path, attr_name, attribute)
                case AttrMode.WRITE:
                    attribute = cast(AttrWrite, attribute)
                    create_and_link_write_pv(path, attr_name, attribute)
                case AttrMode.READ_WRITE:
                    attribute = cast(AttrReadWrite, attribute)
                    create_and_link_read_pv(path, attr_name, attribute)
                    create_and_link_write_pv(path, attr_name, attribute)


class EpicsIOC:
    def __init__(self, mapping: Mapping):
        self._mapping = mapping

    def run(self, options: Optional[EpicsIOCOptions] = None) -> None:
        if options is None:
            options = EpicsIOCOptions()

        # Create an asyncio dispatcher; the event loop is now running
        dispatcher = asyncio_dispatcher.AsyncioDispatcher()

        # Set the record prefix
        builder.SetDeviceName("MY-DEVICE-PREFIX")

        _create_and_link_pvs(self._mapping)

        # Boilerplate to get the IOC started
        builder.LoadDatabase()
        softioc.iocInit(dispatcher)

        link_process_tasks(self._mapping)

        initial_tasks = get_initial_tasks(self._mapping)

        for task in initial_tasks:
            future = asyncio.run_coroutine_threadsafe(task(), dispatcher.loop)
            future.result()

        scan_tasks = get_scan_tasks(self._mapping)

        for task in scan_tasks:
            dispatcher(task)

        # # Run the interactive shell
        # global_variables = globals()
        # global_variables.update(
        #     {
        #         "dispatcher": dispatcher,
        #         "mapping": self._mapping,
        #         "controller": self._mapping.controller,
        #     }
        # )
        softioc.interactive_ioc(globals())
