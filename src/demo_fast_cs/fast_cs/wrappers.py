from .api_methods import PutMethod, ScanMethod

put = PutMethod


def scan(rate: float):
    return lambda fn: ScanMethod(fn, rate)
