import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from nautobot.dcim.models import Device
from nautobot.dcim.models import Manufacturer
from nautobot.dcim.tests.test_views import DeviceTestCase
from nautobot.extras.models import ObjectChange
from nautobot.extras.tests.test_views import ObjectChangeTestCase
from nautobot.users.models import ObjectPermission
from nautobot.utilities.testing.utils import post_data
from nautobot.utilities.testing.views import ViewTestCases

from nautobot_device_resources.models import CPU
from nautobot_device_resources.models import DeviceResource

from . import setups

# All tests must have decorator `@override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])`!
# This is because they need to find objects by UUID from the form.


# pylint: disable-next=too-many-ancestors
class ExtendedDeviceTestCase(DeviceTestCase):
    """Make sure Device views work with existing DeviceResources"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.manufacturer = Manufacturer.objects.first()

        cpus = (
            CPU.objects.create(manufacturer=cls.manufacturer, name="CPU 1", cores=1, threads_per_core=2),
            CPU.objects.create(manufacturer=cls.manufacturer, name="CPU 2", cores=2, threads_per_core=4),
            CPU.objects.create(manufacturer=cls.manufacturer, name="CPU 3", cores=4, threads_per_core=8),
        )

        devices = Device.objects.all()[:3]

        DeviceResource.objects.create(
            device=devices[0], cpu=cpus[0], cpu_count=1, gpu="GPU 1", ram=128, disks="2x200GB SSD"
        )
        DeviceResource.objects.create(
            device=devices[1], cpu=cpus[1], cpu_count=2, gpu="GPU 2", ram=256, disks="2x400GB SSD"
        )
        DeviceResource.objects.create(
            device=devices[2], cpu=cpus[2], cpu_count=4, gpu="GPU 3", ram=512, disks="8x100GB HDD"
        )

        cls.form_data.update(
            {
                "cpu": cpus[0].pk,
                "cpu_count": 2,
                "gpu": "GPU 0",
                "ram": 128,
                "disks": "10x 100GB SSD",
            }
        )

        cls.csv_data = list(cls.csv_data)
        cls.csv_data[0] = cls.csv_data[0] + ",cpu,cpu_count,gpu,ram,disks"
        line_data = f",{cpus[1].name},8,GPU 2,512,10x 200GB HDD"
        for line_number in [1, 2, 3]:
            cls.csv_data[line_number] = cls.csv_data[line_number] + line_data

        cls.bulk_edit_data.update(
            {
                "cpu": cpus[1].pk,
                "cpu_count": 4,
                "gpu": "GPU 1",
                "ram": 256,
                "disks": "5x 100GB SSD",
            }
        )

    def setUp(self):
        super().setUp()
        # add resources columns to list view
        self.user.set_config(
            "tables.DeviceListTable.columns",
            [
                "name",
                "status",
                "tenant",
                "device_role",
                "device_type",
                "site",
                "location",
                "rack",
                "primary_ip",
                "cpu",
                "gpu",
                "ram",
                "disks",
            ],
        )
        self.user.validated_save()

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_list_resources(self):
        response = self.client.get(self._get_url("list"))
        self.assertHttpStatus(response, 200)
        response_body = response.content.decode(response.charset)

        # Check CPU label is correct
        self.assertIn(
            f"{self.manufacturer} CPU 3 (4x)",
            response_body,
        )


# pylint: disable-next=too-many-ancestors
class TestCPUViewsTestCase(setups.CPUSetUp, ViewTestCases.OrganizationalObjectViewTestCase):
    model = CPU

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cpu, _ = CPU.objects.get_or_create(**cls.cpu_data)
        another_cpu_data = {
            **cls.cpu_data,
            "name": "Test CPU 2",
        }
        CPU.objects.get_or_create(**another_cpu_data)

        cls.form_data = {
            "name": "Another Test CPU",
            "slug": "another-test-cpu",
            "manufacturer": cls.cpu_manufacturer.pk,
            "cores": 4,
            "threads_per_core": 4,
        }

        cls.csv_data = (
            "name,slug,manufacturer,cores,threads_per_core",
            "CPU 1,cpu-1,Intel,16,2",
            "CPU 2,cpu-2,Intel,2,4",
            "CPU X,cpu-x,Intel,8,2",
        )
        cls.slug_source = "name"
        cls.slug_test_object = cls.cpu

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_filter_threads(self):
        """Make sure we can filter by total number of threads of CPU"""
        cpu = CPU.objects.first()
        self.assertEqual(cpu.threads, cpu.cores * cpu.threads_per_core)

        response = self.client.get(self._get_url("list") + f"?threads={cpu.threads}")
        self.assertHttpStatus(response, 200)
        response_body = response.content.decode(response.charset)
        self.assertIn(cpu.name, response_body)

        response = self.client.get(self._get_url("list") + f"?threads__gt={cpu.threads - 1}")
        self.assertHttpStatus(response, 200)
        response_body = response.content.decode(response.charset)
        self.assertIn(cpu.name, response_body)

        response = self.client.get(self._get_url("list") + f"?threads__lt={cpu.threads + 1}")
        self.assertHttpStatus(response, 200)
        response_body = response.content.decode(response.charset)
        self.assertIn(cpu.name, response_body)


# pylint: disable-next=too-many-ancestors
class TestObjectChangeDetailTestCase(setups.DeviceResourceSetUp, ObjectChangeTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.form_data = {
            "device_type": cls.device_type.pk,
            "device_role": cls.device_role.pk,
            "tenant": cls.tenant.pk,
            "name": cls.device_data["name"],
            "site": cls.site.pk,
            "status": cls.status.pk,
        }

    def _set_permissions(self):
        # Assign model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(DeviceResource))
        obj_perm.object_types.add(ContentType.objects.get_for_model(Device))

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_device_update(self):
        """Check there are DeviceResource changes in Device change view"""
        self._set_permissions()

        # Make sure we can get the Device
        response = self.client.get(self.device.get_absolute_url())
        self.assertHttpStatus(response, 200)

        another_cpu_data = {
            **self.cpu_data,
            "name": "Test CPU 2",
        }
        another_cpu = CPU.objects.create(**another_cpu_data)

        # Try POST with model-level permission
        new_device_data = {
            **self.form_data,
            "name": "New test name",
            "cpu": another_cpu.pk,
            "cpu_count": 32,
            "gpu": "Another GPU",
            "ram": 1234,
            "disks": "test disks 100GB",
        }
        request = {
            "path": f"{self.device.get_absolute_url()}edit/",
            "data": post_data(new_device_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        self.assertIsNotNone(
            Device.objects.get(name=new_device_data["name"], resources__cpu__id=new_device_data["cpu"])
        )
        request = {
            "path": f"{self.device.get_absolute_url()}edit/",
            "data": post_data(self.form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)

        # Check the changed data is there
        objectchange = ObjectChange.objects.filter(changed_object_id=self.resources.device.id).order_by("time").first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)
        response_body = response.content.decode(response.charset)
        self.assertIn(f"{self.form_data['name']}", response_body)
        self.assertIn(f"{new_device_data['name']}", response_body)
        self.assertIn(f"{new_device_data['cpu']}", response_body)
        self.assertIn(f"{new_device_data['cpu_count']}", response_body)
        self.assertIn(f"{new_device_data['gpu']}", response_body)
        self.assertIn(f"{new_device_data['ram']}", response_body)
        self.assertIn(f"{new_device_data['ram']}", response_body)

        # Check empty data is OK too
        request = {
            "path": f"{self.device.get_absolute_url()}edit/",
            "data": post_data(self.form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        objectchange = ObjectChange.objects.filter(changed_object_id=self.resources.device.id).order_by("time").first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_device_without_resource(self):
        """This should not happen, but make sure we can show the changes anyway"""
        self._set_permissions()
        request = {
            "path": f"{self.device.get_absolute_url()}edit/",
            "data": post_data(self.form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        resource_change = ObjectChange.objects.get(changed_object_id=self.resources.id)
        resource_change.delete()

        self.assertEqual(
            ObjectChange.objects.filter(changed_object_type_id=ContentType.objects.get_for_model(Device)).count(), 1
        )
        self.assertEqual(
            ObjectChange.objects.filter(
                changed_object_type_id=ContentType.objects.get_for_model(DeviceResource)
            ).count(),
            0,
        )

        objectchange = ObjectChange.objects.get(changed_object_id=self.resources.device.id)
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_device_multiple_resource_changes(self):
        """Make sure we get correct change if there are multiple one with same request_id"""
        self._set_permissions()
        request = {
            "path": f"{self.device.get_absolute_url()}edit/",
            "data": post_data(self.form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        resource_change = ObjectChange.objects.get(changed_object_id=self.resources.id)
        resource_change.id = uuid.uuid4()
        resource_change.save()

        self.assertEqual(
            ObjectChange.objects.filter(changed_object_type_id=ContentType.objects.get_for_model(Device)).count(), 1
        )
        self.assertEqual(
            ObjectChange.objects.filter(
                changed_object_type_id=ContentType.objects.get_for_model(DeviceResource)
            ).count(),
            2,
        )

        objectchange = ObjectChange.objects.get(changed_object_id=self.resources.device.id)
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)
