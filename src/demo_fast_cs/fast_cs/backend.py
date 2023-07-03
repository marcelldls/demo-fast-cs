import asyncio
from typing import Callable

from .cs_methods import MethodType
from .mapping import Mapping, MethodData


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


def link_attribute_processing(mapping: Mapping) -> None:
    pass


# def link_attribute_updates(mapping: Mapping, gen: CSAttributeGenerator) -> None:
#     pass
