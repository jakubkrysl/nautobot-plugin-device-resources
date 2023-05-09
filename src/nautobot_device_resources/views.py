from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from nautobot.core.views import generic
from nautobot.dcim.models import Device
from nautobot.dcim.views import DeviceBulkImportView
from nautobot.dcim.views import DeviceEditView
from nautobot.dcim.views import DeviceListView
from nautobot.extras.models import ObjectChange
from nautobot.extras.views import ObjectChangeLogView
from nautobot.extras.views import ObjectChangeView
from nautobot.utilities.forms.forms import DynamicFilterForm
from nautobot.utilities.utils import (
    convert_querydict_to_factory_formset_acceptable_querydict,
)
from nautobot.utilities.utils import count_related

from . import filters
from . import forms
from . import tables
from .consts import PLUGIN_NAME
from .generic.views import EditViewMixin
from .models import CPU
from .models import DeviceResource


class DeviceResourceEditView(DeviceEditView, EditViewMixin):
    model_form = forms.DeviceMixedForm
    template_name = f"{PLUGIN_NAME}/device_resources_edit.html"


class FixedDynamicFilterForm(DynamicFilterForm):
    """Fix advanced filters"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # correct contenttype on the dynamic widget in advanced search to be able to search for Device fields
        # BUG: DeviceResource fields in advanced filters cannot be searched in UI, has to be manually typed to URL
        self.fields["lookup_type"].widget.attrs["data-contenttype"] = "dcim.device"


# This is taken from nautobot.utilities.forms.forms with replaced `filter_form`
def dynamic_formset_factory(filterset_class, data=None, **kwargs):
    filter_form = FixedDynamicFilterForm
    filter_form.filterset_class = filterset_class

    params = {
        "can_delete_extra": True,
        "can_delete": True,
        "extra": 3,
    }
    kwargs.update(params)
    form = formset_factory(form=filter_form, **kwargs)
    if data:
        form = form(data=data)

    return form


class DeviceResourceListView(DeviceListView):
    filterset = filters.DeviceFilterSet
    filterset_form = forms.DeviceListFilterForm
    table = tables.DeviceListTable

    def extra_context(self):
        """Provide extra context to GET request of Device list view."""
        # first get instance of fixed DynamicFilterFormSet
        if self.request.GET:
            factory_formset_params = convert_querydict_to_factory_formset_acceptable_querydict(
                self.request.GET, self.filterset
            )
            dynamic_filter_form = dynamic_formset_factory(filterset_class=self.filterset, data=factory_formset_params)
        else:
            dynamic_filter_form = dynamic_formset_factory(filterset_class=self.filterset)
        # Now replace `dynamic_filter_form` in original context with our patched one
        extra_context = super().extra_context()
        extra_context.update(
            {
                "dynamic_filter_form": dynamic_filter_form,
            }
        )
        return extra_context


class DeviceResourceBulkImportView(DeviceBulkImportView):
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = "dcim/device_import.html"


class CPUView(generic.ObjectView):
    queryset = CPU.objects.select_related("manufacturer")

    def get_extra_context(self, request, instance):
        instance_count = DeviceResource.objects.filter(cpu=instance).count()
        return {
            "instance_count": instance_count,
        }


class CPUListView(generic.ObjectListView):
    queryset = CPU.objects.select_related("manufacturer").annotate(
        instance_count=count_related(Device, "resources__cpu")
    )
    filterset = filters.CPUFilterSet
    filterset_form = forms.CPUFilterForm
    table = tables.CPUTable


class CPUDeleteView(generic.ObjectDeleteView):
    queryset = CPU.objects.all()


class CPUEditView(generic.ObjectEditView):
    queryset = CPU.objects.all()
    model_form = forms.CPUForm
    template_name = f"{PLUGIN_NAME}/cpu_edit.html"


class CPUChangeLogView(ObjectChangeLogView):
    base_template = f"{PLUGIN_NAME}/cpu.html"


class CPUBulkImportView(generic.BulkImportView):
    queryset = CPU.objects.all()
    model_form = forms.CPUCSVForm
    table = tables.CPUImportTable


class CPUBulkEditView(generic.BulkEditView):
    queryset = CPU.objects.select_related("manufacturer")
    filterset = filters.CPUFilterSet
    table = tables.CPUTable
    form = forms.CPUBulkEditForm


class CPUBulkDeleteView(generic.BulkDeleteView):
    queryset = CPU.objects.select_related("manufacturer")
    filterset = filters.CPUFilterSet
    table = tables.CPUTable


class DeviceChangeLogView(ObjectChangeView):
    @staticmethod
    def get_resource_change(device_change: ObjectChange) -> ObjectChange | None:
        """Get change of related DeviceResource for this Device change."""
        resource_changes = ObjectChange.objects.filter(
            request_id=device_change.request_id,
            changed_object_type_id=ContentType.objects.get(
                app_label="nautobot_device_resources",
                model="deviceresource",
            ).id,
        )
        if resource_changes.count() == 1:
            return resource_changes[0]
        if resource_changes.count() > 1:
            for change in resource_changes:
                if change.object_data["device"] == str(device_change.changed_object_id):
                    return change
        return None

    def get_extra_context(self, request, instance):
        """Add change data of DeviceResource to change of Device"""
        extra_context = super().get_extra_context(request, instance)
        if instance.changed_object_type != ContentType.objects.get(app_label="dcim", model="device"):
            return extra_context
        resource_change = self.get_resource_change(instance)
        if resource_change is None:
            return extra_context
        snapshots = resource_change.get_snapshots()
        for diff_type in ["diff_added", "diff_removed"]:
            diff = extra_context[diff_type]
            filtered_resource_diff = {
                k: v
                for k, v in (snapshots["differences"][diff_type.split("_")[1]] or {}).items()
                if k in ["cpu", "cpu_count", "gpu", "disks", "ram"]
            }
            if diff is None:
                extra_context[diff_type] = filtered_resource_diff
            else:
                extra_context[diff_type].update(filtered_resource_diff)

        resource_data = resource_change.object_data
        instance.object_data.update(
            {
                "cpu": CPU.objects.get(id=resource_data["cpu"]).name if resource_data["cpu"] else resource_data["cpu"],
                "cpu_count": resource_data["cpu_count"],
                "gpu": resource_data["gpu"],
                "disks": resource_data["disks"],
                "ram": resource_data["ram"],
            }
        )
        return extra_context


override_views = {
    "dcim:device_add": DeviceResourceEditView.as_view(),
    "dcim:device_edit": DeviceResourceEditView.as_view(),
    "dcim:device_list": DeviceResourceListView.as_view(),
    "dcim:device_import": DeviceResourceBulkImportView.as_view(),
    "extras:objectchange": DeviceChangeLogView.as_view(),
}
