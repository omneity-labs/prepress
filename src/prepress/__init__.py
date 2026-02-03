from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("prepress")
except PackageNotFoundError:
    __version__ = "0.2.0"
