import asyncio
from typing import Callable, cast

from .attributes import AttrCallback, AttrMode, AttrWrite
from .cs_methods import MethodType
from .mapping import Mapping, MethodData, SingleMapping


def get_initial_tasks(mapping: Mapping) -> list[Callable]:
    initial_tasks: list[Callable] = []

    initial_tasks.append(mapping.controller.connect)

    return initial_tasks


def get_scan_method(method_data: MethodData) -> Callable:
    period = method_data.info.kwargs["period"]
    method = method_data.method

    async def scan_method() -> None:
        while True:
            await method()
            await asyncio.sleep(period)

    return scan_method


def get_scan_tasks(mapping: Mapping) -> list[Callable]:
    methods: list[Callable] = []
    for single_mapping in mapping.get_controller_mappings():
        for method_data in single_mapping.methods:
            if method_data.info.method_type == MethodType.scan:
                methods.append(get_scan_method(method_data))

    return methods


def _link_single_controller_process_tasks(single_mapping: SingleMapping):
    put_methods = [
        method_data
        for method_data in single_mapping.methods
        if method_data.info.method_type == MethodType.put
    ]

    for method_data in put_methods:
        method = cast(AttrCallback, method_data.method)
        name = method_data.name.removeprefix("put_")

        attribute = single_mapping.attributes[name]
        assert attribute.mode in [
            AttrMode.WRITE,
            AttrMode.READ_WRITE,
        ], f"Mode {attribute.mode} does not support put operations for {name}"
        attribute = cast(AttrWrite, attribute)

        attribute.set_process_callback(method)


def link_process_tasks(mapping: Mapping) -> None:
    for single_mapping in mapping.get_controller_mappings():
        _link_single_controller_process_tasks(single_mapping)

