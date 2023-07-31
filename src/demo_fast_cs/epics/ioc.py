import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional, cast

from softioc import asyncio_dispatcher, builder, softioc

from ..fast_cs.attributes import AttrMode, AttrRead, AttrReadWrite, AttrWrite
from ..fast_cs.backend import get_initial_tasks, get_scan_tasks, link_process_tasks
from ..fast_cs.cs_methods import MethodType
from ..fast_cs.mapping import Mapping


@dataclass
class EpicsIOCOptions:
    terminal: bool = True


def _get_input_record(pv_name: str, dtype: type) -> Any:
    if dtype is bool:
        return builder.boolIn(pv_name, ZNAM="OFF", ONAM="ON")
    else:
        return builder.aIn(pv_name)


def _create_and_link_read_pv(pv_name: str, attribute: AttrRead) -> None:
    record = _get_input_record(pv_name, attribute.dtype)

    async def async_wrapper(v):
        record.set(v)

    attribute.set_update_callback(async_wrapper)


def _get_output_record(pv_name: str, dtype: type, on_update: Callable) -> Any:
    if dtype is bool:
        return builder.boolOut(
            pv_name, ZNAM="OFF", ONAM="ON", always_update=True, on_update=on_update
        )
    else:
        return builder.aOut(pv_name, always_update=True, on_update=on_update)


def _create_and_link_write_pv(pv_name: str, attribute: AttrWrite) -> None:
    record = _get_output_record(
        pv_name, attribute.dtype, on_update=attribute.process_without_display_update
    )

    async def async_wrapper(v):
        record.set(v)

    attribute.set_write_display_callback(async_wrapper)


def _create_and_link_command_pv(pv_name: str, method: Callable) -> None:
    async def wrapped_method(_: Any):
        await method()

    builder.aOut(pv_name, always_update=True, on_update=wrapped_method)


def _create_and_link_attribute_pvs(mapping: Mapping) -> None:
    for single_mapping in mapping.get_controller_mappings():
        path = single_mapping.controller.path
        for attr_name, attribute in single_mapping.attributes.items():
            attr_name = attr_name.title().replace("_", "")
            pv_name = path.upper() + ":" + attr_name if path else attr_name

            match attribute.mode:
                case AttrMode.READ:
                    attribute = cast(AttrRead, attribute)
                    _create_and_link_read_pv(pv_name, attribute)
                case AttrMode.WRITE:
                    attribute = cast(AttrWrite, attribute)
                    _create_and_link_write_pv(pv_name, attribute)
                case AttrMode.READ_WRITE:
                    attribute = cast(AttrReadWrite, attribute)
                    _create_and_link_read_pv(pv_name + "_RBV", attribute)
                    _create_and_link_write_pv(pv_name, attribute)


def _create_and_link_command_pvs(mapping: Mapping) -> None:
    for single_mapping in mapping.get_controller_mappings():
        path = single_mapping.controller.path
        for method_data in single_mapping.methods:
            if method_data.info.method_type == MethodType.command:
                name = method_data.name.title().replace("_", "")
                pv_name = path.upper() + ":" + name if path else name

                _create_and_link_command_pv(pv_name, method_data.method)


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

        _create_and_link_attribute_pvs(self._mapping)

        _create_and_link_command_pvs(self._mapping)

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

        # Run the interactive shell
        global_variables = globals()
        global_variables.update(
            {
                "dispatcher": dispatcher,
                "mapping": self._mapping,
                "controller": self._mapping.controller,
            }
        )
        softioc.interactive_ioc(globals())
