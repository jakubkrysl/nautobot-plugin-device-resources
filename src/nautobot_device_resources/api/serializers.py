from nautobot.core.api import ValidatedModelSerializer
from nautobot.core.api import WritableNestedSerializer
from nautobot.dcim.api.nested_serializers import NestedDeviceSerializer
from nautobot.dcim.api.nested_serializers import NestedManufacturerSerializer
from rest_framework import serializers

from ..consts import PLUGIN_NAME
from ..models import CPU
from ..models import DeviceResource


class NestedCPUSerializer(WritableNestedSerializer):
    """Nested field for CPU."""

    url = serializers.HyperlinkedIdentityField(view_name=f"plugins-api:{PLUGIN_NAME}-api:cpu-detail")

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU
        fields = ["id", "url", "name"]


class DeviceResourceSerializer(ValidatedModelSerializer):
    """API serializer for interacting with DeviceResource objects."""

    device = NestedDeviceSerializer()
    cpu = NestedDeviceSerializer()

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = DeviceResource
        fields = ("id", "label", "device", "cpu", "cpu_count", "gpu", "ram", "disks")


class CPUSerializer(ValidatedModelSerializer):
    """API serializer for interacting with CPU objects."""

    url = serializers.HyperlinkedIdentityField(view_name=f"plugins-api:{PLUGIN_NAME}-api:cpu-detail")
    manufacturer = NestedManufacturerSerializer()

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU
        fields = ("id", "url", "label", "name", "slug", "manufacturer", "cores", "threads_per_core", "threads")
