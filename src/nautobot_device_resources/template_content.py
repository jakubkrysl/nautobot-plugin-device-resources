from nautobot.extras.plugins import TemplateExtension

from .consts import PLUGIN_NAME
from .models import CPU
from .models import DeviceResource


# pylint: disable-next=abstract-method
class CPUTemplateExtension(TemplateExtension):
    """Extend Manufacturer detail view to show CPU details"""

    model = "dcim.manufacturer"

    def right_page(self):
        """Plugin content to add to the right column."""

        cpu_count = CPU.objects.filter(manufacturer=self.context["object"]).count

        return self.render(
            f"{PLUGIN_NAME}/cpu_manufacturer_extension.html",
            extra_context={
                "cpu_count": cpu_count,
            },
        )


# pylint: disable-next=abstract-method
class DeviceResourceTemplateExtension(TemplateExtension):
    """Template to show device resources on its detail page."""

    model = "dcim.device"

    def right_page(self):
        """Plugin content to add to the right column."""
        try:
            resources = DeviceResource.objects.get(device=self.context["object"])
        except DeviceResource.DoesNotExist:
            resources = DeviceResource()

        return self.render(
            f"{PLUGIN_NAME}/device_resources.html",
            extra_context={
                "resources": resources,
            },
        )


template_extensions = [CPUTemplateExtension, DeviceResourceTemplateExtension]
