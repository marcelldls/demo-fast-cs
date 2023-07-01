import asyncio

from demo_fast_cs.controllers import (
    IPConnectionSettings,
    TempController,
    TempControllerSettings,
)

from .fast_cs.mapping import Mapping


def get_controller() -> TempController:
    ip_settings = IPConnectionSettings()
    settings = TempControllerSettings(4, ip_settings)
    tcont = TempController(settings)
    return tcont


async def run_controller():
    tcont = get_controller()
    await tcont.connect()
    print(f"Initial ramp rate: {tcont.ramp_rate.get()}")
    await tcont.update()
    print(f"Starting ramp rate: {tcont.ramp_rate.get()}")
    await tcont.put_ramp_rate(5)
    await tcont.update()
    print(f"Final ramp rate: {tcont.ramp_rate.get()}")
    # trc = tcont.get_sub_controllers()[0]
    # await trc.update()
    # await tcont.update()
    # await asyncio.sleep(1)
    # await tcont.set_enabled(1)
    # await asyncio.sleep(3)
    # await tcont.update()
    # await asyncio.sleep(3)
    # await tcont.update()
    # await tcont.set_enabled(0)
    # await tcont.update()
    # await tcont.close()


def test_mapping():
    tcont = get_controller()
    m = Mapping(tcont)

    print(str(m))


def main():
    asyncio.run(run_controller())
