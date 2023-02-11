from importlib.metadata import version

__version__ = version("demo-fast-cs")
del version

__all__ = ["__version__"]
