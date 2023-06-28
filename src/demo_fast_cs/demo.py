import asyncio

from demo_fast_cs.controllers import (
    IPConnectionSettings,
    TempController,
    TempControllerSettings,
)


def get_controller() -> TempController:
    settings = TempControllerSettings(4)
    tcont = TempController(settings)
    return tcont


async def run_controller():
    tcont = get_controller()
    ip_settings = IPConnectionSettings()
    await tcont.connect(ip_settings)
    print(f"Initial ramp rate: {tcont.ramp_rate}")
    await tcont.update()
    print(f"Starting ramp rate: {tcont.ramp_rate}")
    await tcont.put_ramp_rate(5)
    await tcont.update()
    print(f"Final ramp rate: {tcont.ramp_rate}")

    trc = tcont.get_sub_controllers()[0]
    await trc.update()
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


def main():
    asyncio.run(run_controller())
