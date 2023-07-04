import asyncio

from softioc import asyncio_dispatcher, softioc

from .backend import get_initial_tasks, get_scan_tasks
from .mapping import Mapping


class AsyncioBackend:
    def __init__(self, mapping: Mapping):
        self._mapping = mapping

    def run_interactive_session(self):
        # Create an asyncio dispatcher; the event loop is now running
        dispatcher = asyncio_dispatcher.AsyncioDispatcher()

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
