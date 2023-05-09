import django_tables2 as tables
from django_tables2.utils import Accessor
from nautobot.dcim.tables import DeviceImportTable as NautobotDeviceImportTable
from nautobot.dcim.tables import DeviceTable
from nautobot.utilities.tables import BaseTable
from nautobot.utilities.tables import LinkedCountColumn
from nautobot.utilities.tables import ToggleColumn

from .filters import Device
from .models import CPU


def cpu_text(record):
    cpu_string = f"{record.resources.cpu.manufacturer} {record.resources.cpu}"
    cpu_count = record.resources.cpu_count
    if cpu_count > 1:
        cpu_string = cpu_string + f" ({cpu_count}x)"
    return cpu_string


class DeviceListTable(DeviceTable):
    cpu = tables.LinkColumn(
        viewname="plugins:nautobot_device_resources:cpu",
        accessor="resources__cpu",
        kwargs={"slug": tables.A("resources__cpu__slug")},
        verbose_name="CPU",
        text=cpu_text,
    )
    gpu = tables.Column(
        accessor="resources__gpu",
        verbose_name="GPU",
    )
    ram = tables.Column(
        accessor="resources__ram",
        verbose_name="RAM",
    )
    disks = tables.Column(
        accessor="resources__disks",
        verbose_name="Disks",
    )

    # pylint: disable-next=too-few-public-methods
    class Meta(DeviceTable.Meta):
        fields = DeviceTable.Meta.fields + (
            "cpu",
            "gpu",
            "ram",
            "disks",
        )


class DeviceImportTable(NautobotDeviceImportTable):
    cpu = tables.LinkColumn(
        viewname="plugins:nautobot_device_resources:cpu",
        accessor="resources__cpu",
        kwargs={"slug": tables.A("resources__cpu__slug")},
        verbose_name="CPU",
        text=cpu_text,
    )
    cpu_count = tables.Column(
        accessor="resources__cpu_count",
        verbose_name="CPU count",
    )
    gpu = tables.Column(
        accessor="resources__gpu",
        verbose_name="GPU",
    )
    ram = tables.Column(
        accessor="resources__ram",
        verbose_name="RAM",
    )
    disks = tables.Column(
        accessor="resources__disks",
        verbose_name="Disks",
    )

    # pylint: disable-next=too-few-public-methods
    class Meta(NautobotDeviceImportTable.Meta):
        model = Device
        fields = NautobotDeviceImportTable.Meta.fields + (
            "cpu",
            "cpu_count",
            "gpu",
            "ram",
            "disks",
        )


class CPUTable(BaseTable):
    pk = ToggleColumn()
    manufacturer = tables.LinkColumn(
        viewname="dcim:manufacturer",
        args=[Accessor("manufacturer__slug")],
        verbose_name="Manufacturer",
        text=lambda record: record.manufacturer.name,
    )
    name = tables.Column(linkify=True, verbose_name="CPU")
    cores = tables.Column(verbose_name="Cores")
    threads_per_core = tables.Column(verbose_name="Threads per Core")
    instance_count = LinkedCountColumn(
        viewname="dcim:device_list",
        url_params={"cpu": "slug"},
        verbose_name="Instances",
    )

    # pylint: disable-next=too-few-public-methods
    class Meta(BaseTable.Meta):
        model = CPU
        fields = (
            "pk",
            "name",
            "manufacturer",
            "cores",
            "threads_per_core",
            "instance_count",
        )
        default_columns = (
            "pk",
            "name",
            "manufacturer",
            "cores",
            "threads_per_core",
            "instance_count",
        )


class CPUImportTable(BaseTable):
    # pylint: disable-next=too-few-public-methods
    class Meta(BaseTable.Meta):
        model = CPU
        fields = (
            "slug",
            "name",
            "manufacturer",
            "cores",
            "threads_per_core",
        )
        empty_text = False
