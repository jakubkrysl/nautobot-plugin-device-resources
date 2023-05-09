import django_filters
from django.db.models import F
from nautobot.dcim.filters import DeviceFilterSet as NautobotDeviceFilterSet
from nautobot.dcim.filters.mixins import DeviceComponentModelFilterSetMixin
from nautobot.dcim.models import Device as NautobotDevice
from nautobot.dcim.models import Manufacturer
from nautobot.extras.filters import NautobotFilterSet
from nautobot.extras.filters.mixins import CustomFieldModelFilterSetMixin
from nautobot.extras.filters.mixins import RelationshipModelFilterSetMixin
from nautobot.utilities.filters import BaseFilterSet
from nautobot.utilities.filters import NameSlugSearchFilterSet
from nautobot.utilities.filters import NaturalKeyOrPKMultipleChoiceFilter
from nautobot.utilities.filters import SearchFilter

from .models import CPU
from .models import DeviceResource

# Caution: All filter classes are expected to be '{Model}FilterSet' in Nautobot internal logic.


class DeviceResourceFilterSet(BaseFilterSet, DeviceComponentModelFilterSetMixin):
    """Filter capabilities for DeviceResource instances."""

    q = SearchFilter(filter_predicates={})

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="device",
        to_field_name="name",
        queryset=NautobotDevice.objects.all(),
        label="Device (name or ID)",
    )

    cpu = django_filters.ModelMultipleChoiceFilter(
        field_name="cpu__slug",
        queryset=CPU.objects.all(),
        to_field_name="slug",
        label="CPU (slug)",
    )

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = DeviceResource
        fields = ["id", "device", "cpu", "cpu_count", "gpu", "ram", "disks"]


# pylint: disable-next=too-many-ancestors
class Device(NautobotDevice):
    """Add DeviceResource fields to Device model for filtering purposes"""

    cpu = DeviceResource.cpu
    cpu_count = DeviceResource.cpu_count
    gpu = DeviceResource.gpu
    ram = DeviceResource.ram
    disks = DeviceResource.disks

    # pylint: disable-next=too-few-public-methods
    class Meta(NautobotDevice.Meta):
        # This makes sure there are no migrations created
        abstract = True


# pylint: disable-next=too-many-ancestors
class DeviceFilterSet(NautobotDeviceFilterSet):
    """Add DeviceResource filters to original DeviceFilterSet"""

    # pylint: disable-next=too-few-public-methods
    class Meta(NautobotDeviceFilterSet.Meta):
        # replace original model in (Nautobot)DeviceFilterSet with one with DeviceResource fields
        # This allows to filter using predefined form (see nautobot_device_resources.forms.DeviceListFilterForm)
        model = Device

    def __init__(self, *args, **kwargs):
        # We need to initialize with the new model to add Resources filters
        super().__init__(*args, **kwargs)
        # This adds filters which get added based on the model content type
        self._meta.model = NautobotDevice
        CustomFieldModelFilterSetMixin.__init__(self, *args, **kwargs)
        RelationshipModelFilterSetMixin.__init__(self, *args, **kwargs)
        self._meta.model = Device

    cpu = django_filters.ModelMultipleChoiceFilter(
        field_name="resources__cpu__slug",
        queryset=CPU.objects.all(),
        to_field_name="slug",
        label="CPU (slug)",
    )
    cpu_count = django_filters.NumberFilter(
        field_name="resources__cpu_count",
        min_value=1,
        label="CPU count",
    )
    cpu_count__gt = django_filters.NumberFilter(
        field_name="resources__cpu_count",
        lookup_expr="gt",
    )
    cpu_count__lt = django_filters.NumberFilter(
        field_name="resources__cpu_count",
        lookup_expr="lt",
    )
    gpu = django_filters.CharFilter(
        field_name="resources__gpu",
        label="GPU",
    )
    ram = django_filters.NumberFilter(
        field_name="resources__ram",
        min_value=1,
        label="RAM (GB)",
    )
    disks = django_filters.CharFilter(
        field_name="resources__disks",
        label="Disks",
    )


# pylint: disable-next=too-many-ancestors
class CPUFilterSet(NautobotFilterSet, NameSlugSearchFilterSet):
    """Filter capabilities for DeviceResource instances."""

    manufacturer = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="manufacturer",
        to_field_name="name",
        queryset=Manufacturer.objects.all(),
        label="Manufacturer (name or ID)",
    )

    threads = django_filters.NumberFilter(
        field_name="threads_number",
        min_value=1,
        label="Threads",
    )
    threads__gt = django_filters.NumberFilter(
        field_name="threads_number",
        lookup_expr="gt",
    )
    threads__lt = django_filters.NumberFilter(
        field_name="threads_number",
        lookup_expr="lt",
    )

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU
        fields = ["id", "name", "cores", "threads", "threads_per_core"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.annotate(threads_number=(F("cores") * F("threads_per_core")))
