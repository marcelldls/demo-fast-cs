from fastcs.backends import EpicsBackend
from fastcs.mapping import Mapping

from demo_fast_cs.controllers import (
    SerialConnectionSettings,
    ThorlabsMFF,
    ThorlabsMFFSettings,
)


def get_controller() -> ThorlabsMFF:
    serial_settings = SerialConnectionSettings(port="/dev/ttyUSB0")
    settings = ThorlabsMFFSettings(serial_settings)
    tcont = ThorlabsMFF(settings)
    return tcont


def create_gui() -> None:
    tcont = get_controller()
    m = Mapping(tcont)
    backend = EpicsBackend(m)
    backend.create_gui()


def test_ioc() -> None:
    tcont = get_controller()
    m = Mapping(tcont)
    backend = EpicsBackend(m)
    ioc = backend.get_ioc()
    ioc.run()


def main() -> None:
    create_gui()
    test_ioc()


if __name__ == "__main__":
    main()
