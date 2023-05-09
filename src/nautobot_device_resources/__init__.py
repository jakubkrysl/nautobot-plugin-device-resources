from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from nautobot.extras.plugins import NautobotAppConfig

from .consts import PLUGIN_NAME

try:
    __version__ = version(PLUGIN_NAME)
except PackageNotFoundError:
    __version__ = "package not installed"


class NautobotDeviceResources(NautobotAppConfig):
    """Nautobot plugin to provide device resources info to device."""

    name = PLUGIN_NAME
    verbose_name = "Nautobot Device Resources"
    description = "Provides resources to Device"
    version = __version__
    author = "Jakub Krysl"
    author_email = "jakub.krysl@gmail.com"


# pylint: disable-next=invalid-name
config = NautobotDeviceResources
