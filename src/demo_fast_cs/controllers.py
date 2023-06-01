import asyncio
from typing import NamedTuple, Type

from .fast_cs import BaseSettings, Controller

FieldInfo = NamedTuple("FieldInfo", (("name", str), ("prefix", str), ("type", Type)))


class TempControllerSettings(BaseSettings):
    device_ip: str = "127.0.0.1"
    device_port: int = 25565


def get_settings():
    return TempControllerSettings()


class IPConnection:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

    @classmethod
    async def connect(cls, ip, port):
        reader, writer = await asyncio.open_connection(ip, port)
        return cls(reader, writer)

    async def send_command(self, message) -> None:
        self._writer.write(message.encode("utf-8"))
        await self._writer.drain()

    async def send_query(self, message) -> str:
        await self.send_command(message)
        data = await self._reader.readline()
        return data.decode("utf-8")

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()


class TempRampController(Controller):
    start: float
    end: float
    current: float
    enabled: int

    _fields = (
        FieldInfo("start", "S", float),
        FieldInfo("end", "E", float),
        FieldInfo("current", "T", float),
        FieldInfo("enabled", "N", int),
    )

    def __init__(self, index, conn):
        suffix: str = f"{index:02d}"
        super().__init__(f"ramp{suffix}")
        self._conn: IPConnection = conn
        self._suffix: str = suffix

    @classmethod
    async def create(cls, index):
        settings = get_settings()
        conn = await IPConnection.connect(settings.device_ip, settings.device_port)
        return cls(index, conn)

    async def close(self):
        await self._conn.close()

    # @scan(0.1)
    async def update(self):
        for field in self._fields:
            response = await self._conn.send_query(f"{field.prefix}{self._suffix}?\r\n")
            setattr(self, field.name, field.type(response))

        print(f"Start: {self.start}")
        print(f"End: {self.end}")
        print(f"Current: {self.current}")
        print(f"Enabled: {self.enabled}")

    # @put("enabled")
    async def set_enabled(self, value: int):
        await self._conn.send_command(f"N{self._suffix}={value}\r\n")

    # @get("enabled")
    async def get_enabled(self) -> int:
        return int(await self._conn.send_query(f"N{self._suffix}?"))

    # # @get("start")
    # def get_start(self):
    #     pass

    # # @put("start")
    # def put_start(self, value: float):
    #     self._device_interface.set_start(self._index, value)
    #     self.update()

    # # @put("end")
    # def put_end(self, value: float):
    #     self._device_interface.set_start(self._index, value)
    #     self.update()

    def get_mapping(self) -> Mapping:
        pass


async def run_controller():
    tcont = await TempRampController.create(2)

    await tcont.update()
    await asyncio.sleep(1)
    await tcont.set_enabled(1)
    await asyncio.sleep(3)
    await tcont.update()
    await asyncio.sleep(3)
    await tcont.update()
    await tcont.set_enabled(0)
    await tcont.update()
    await tcont.close()


def main():
    asyncio.run(run_controller())
