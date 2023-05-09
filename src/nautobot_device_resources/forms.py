from django import forms
from nautobot.dcim.forms import DeviceCSVForm as NautobotDeviceCSVForm
from nautobot.dcim.forms import DeviceFilterForm
from nautobot.dcim.forms import DeviceForm
from nautobot.dcim.models import Manufacturer
from nautobot.extras.forms import NautobotBulkEditForm
from nautobot.extras.forms import NautobotFilterForm
from nautobot.extras.forms import NautobotModelForm
from nautobot.utilities.forms import BootstrapMixin
from nautobot.utilities.forms import CSVModelChoiceField
from nautobot.utilities.forms import CSVModelForm
from nautobot.utilities.forms import DynamicModelChoiceField
from nautobot.utilities.forms import DynamicModelMultipleChoiceField
from nautobot.utilities.forms import SlugField

from .generic.forms import MixedCSVFormMixin
from .generic.forms import MixedFormMixin
from .models import CPU
from .models import DeviceResource


class DeviceResourceForm(BootstrapMixin, forms.ModelForm):
    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = DeviceResource
        fields = ["cpu", "cpu_count", "gpu", "ram", "disks"]


class DeviceResourceCSVForm(DeviceResourceForm):
    cpu = CSVModelChoiceField(
        required=False,
        queryset=CPU.objects.all(),
        to_field_name="name",
        label="CPU",
    )


# pylint: disable=too-many-ancestors
class DeviceCSVForm(NautobotDeviceCSVForm, MixedCSVFormMixin):
    child_model = DeviceResource
    child_foreign_link = "resources"
    child_foreign_field = "device"
    child_form = DeviceResourceCSVForm


# pylint: disable-next=too-many-ancestors
class DeviceMixedForm(DeviceForm, MixedFormMixin):
    child_model = DeviceResource
    child_foreign_link = "resources"
    child_foreign_field = "device"
    child_form = DeviceResourceForm


# pylint: disable-next=too-many-ancestors
class DeviceListFilterForm(DeviceFilterForm):
    cpu = DynamicModelMultipleChoiceField(
        required=False,
        queryset=CPU.objects.all(),
        to_field_name="name",
        display_field="CPU",
        label="CPU",
    )
    cpu_count = forms.IntegerField(
        min_value=1,
        required=False,
        label="CPU count",
    )
    gpu = forms.CharField(
        required=False,
        label="GPU",
    )
    ram = forms.IntegerField(
        min_value=1,
        required=False,
        label="RAM (GB)",
    )
    disks = forms.CharField(
        required=False,
        label="Disks",
    )


# pylint: disable-next=too-many-ancestors
class CPUForm(NautobotModelForm):
    manufacturer = DynamicModelChoiceField(queryset=Manufacturer.objects.all())
    slug = SlugField(slug_source="name")

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU
        fields = [
            "manufacturer",
            "name",
            "slug",
            "cores",
            "threads_per_core",
        ]


class CPUFilterForm(NautobotFilterForm):
    model = CPU
    field_order = [
        "q",
        "manufacturer",
        "cores",
        "threads_per_core",
    ]
    q = forms.CharField(required=False, label="Search")
    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(), to_field_name="name", required=False
    )
    cores = forms.IntegerField(min_value=0, required=False, label="Cores")
    threads_per_core = forms.IntegerField(min_value=0, required=False, label="Threads per Core")


# pylint: disable-next=too-many-ancestors
class CPUBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=CPU.objects.all(), widget=forms.MultipleHiddenInput())
    manufacturer = DynamicModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    cores = forms.IntegerField(min_value=0, required=False, label="Cores")
    threads_per_core = forms.IntegerField(min_value=0, required=False, label="Threads per Core")

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU


class CPUCSVForm(CSVModelForm):
    manufacturer = CSVModelChoiceField(queryset=Manufacturer.objects.all(), to_field_name="name")

    # pylint: disable-next=too-few-public-methods
    class Meta:
        model = CPU
        fields = [
            "name",
            "slug",
            "manufacturer",
            "cores",
            "threads_per_core",
        ]
