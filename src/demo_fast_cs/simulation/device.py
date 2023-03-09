import logging
from dataclasses import dataclass
import traceback
from os import _exit

import numpy as np
import numpy.typing as npt
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.tcp import ByteFormat, TcpServer
from tickit.adapters.composed import ComposedAdapter
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from typing_extensions import TypedDict


def handle_exceptions(func):
    """Log and exit if the wrapped function raises an Exception.

    Tickit does not properly handle exceptions in e.g. update() methods. This wrapper is
    used to ensure we see the errors as soon as they occur.
    """

    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:  # noqa
            logging.error(traceback.format_exc())
            _exit(-1)

    return wrapped_func


class TempControllerDevice(Device):
    Inputs: TypedDict = TypedDict("Inputs", {"flux": float})
    Outputs: TypedDict = TypedDict("Outputs", {"flux": float})

    def __init__(
        self,
        num_ramp_controllers: int,
        default_start: float,
        default_end: float,
    ) -> None:
        self._num = num_ramp_controllers
        self._start = np.full(num_ramp_controllers, default_start, dtype=float)
        self._end = np.full(num_ramp_controllers, default_end, dtype=float)
        self._current = np.zeros(num_ramp_controllers, dtype=float)
        self._enabled = np.full(num_ramp_controllers, False, dtype=bool)
        self._start_times = np.full(num_ramp_controllers, -1, dtype=int)

        self._ramp_rate: float = 1  # 1 unit/s

    def get_temps(self, index: int):
        return self._current[index]

    def get_start(self, index: int):
        return self._start[index]

    def set_start(self, index: int, value: float):
        self._start[index] = value

    def get_end(self, index: int):
        return self._end[index]

    def set_end(self, index: int, value: float):
        self._end[index] = value

    def set_enabled(self, index: int, value: bool):
        if value:
            self._current[index] = self._start[index]
            self._start_times[index] = -1
            self._enabled[index] = True
        else:
            self._enabled[index] = False

    def get_enabled(self, index: int):
        return self._enabled[index]

    def ramp(
        self,
        periods: npt.NDArray,
    ):
        can_ramp = np.logical_and(self._enabled, self._current < self._end)
        max_temps = self._current.copy()
        max_temps[can_ramp] += self._ramp_rate * (periods[can_ramp] / 1e9)
        self._current = np.minimum(max_temps, self._end)
        self._enabled[self._current >= self._end] = False

    @handle_exceptions
    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        self._start_times[self._start_times == -1] = int(time)
        periods = np.full(self._num, int(time)) - self._start_times
        self.ramp(periods)
        self._start_times = np.full(self._num, int(time))
        call_at = SimTime(int(time) + int(1e8)) if np.any(self._enabled) else None
        return DeviceUpdate(TempControllerDevice.Outputs(flux=inputs["flux"]), call_at)


class TempControllerAdapter(ComposedAdapter):
    device: TempControllerDevice

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
    ) -> None:
        super().__init__(
            TcpServer(host, port, ByteFormat(b"%b\r\n")),
            CommandInterpreter(),
        )

    @RegexCommand(r"T([0-9][0-9])\?", False, "utf-8")
    async def get_temperature(self, index: str) -> bytes:
        return str(self.device.get_temps(int(index))).encode("utf-8")

    @RegexCommand(r"N([0-9][0-9])\?", False, "utf-8")
    async def get_enabled(self, index: str) -> bytes:
        return str(self.device.get_enabled(int(index))).encode("utf-8")

    @RegexCommand(r"N([0-9][0-9])=([Yy]|[Nn])", True, "utf-8")
    async def set_enabled(self, index: str, value: str) -> None:
        state = value in ("y", "Y")
        self.device.set_enabled(int(index), state)

    @RegexCommand(r"S([0-9][0-9])\?", False, "utf-8")
    async def get_start(self, index: str) -> bytes:
        return str(self.device.get_start(int(index))).encode("utf-8")

    @RegexCommand(r"S([0-9][0-9])=(\d+\.?\d*)", True, "utf-8")
    async def set_start(self, index: str, value: str) -> None:
        self.device.set_start(int(index), float(value))

    @RegexCommand(r"E([0-9][0-9])\?", False, "utf-8")
    async def get_end(self, index: str) -> bytes:
        return str(self.device.get_end(int(index))).encode("utf-8")

    @RegexCommand(r"E([0-9][0-9])=(\d+\.?\d*)", True, "utf-8")
    async def set_end(self, index: str, value: str) -> None:
        self.device.set_end(int(index), float(value))


@dataclass
class TempController(ComponentConfig):
    num_ramp_controllers: int
    default_start: float = 0
    default_end: float = 50
    host: str = "localhost"
    port: int = 25565

    def __call__(self) -> Component:
        return DeviceSimulation(
            name=self.name,
            device=TempControllerDevice(
                num_ramp_controllers=self.num_ramp_controllers,
                default_start=self.default_start,
                default_end=self.default_end,
            ),
            adapters=[TempControllerAdapter(host=self.host, port=self.port)],
        )
