from django.test import TestCase
from nautobot.dcim.models import Device
from nautobot.dcim.models import DeviceRole
from nautobot.dcim.models import DeviceType
from nautobot.dcim.models import Manufacturer
from nautobot.dcim.models import Site
from nautobot.extras.models import Status
from nautobot.tenancy.models import Tenant

from nautobot_device_resources.models import CPU
from nautobot_device_resources.models import DeviceResource


class DeviceSetUp(TestCase):
    """Provide test Device instance"""

    def setUp(self):
        super().setUp()
        self.device, _ = Device.objects.get_or_create(**self.device_data)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tenant, _ = Tenant.objects.get_or_create(
            slug="dirty",
            defaults={
                "name": "DIRTY",
            },
        )
        cls.site, _ = Site.objects.get_or_create(
            name="Test Site 1",
            defaults={
                "status": Status.objects.get_for_model(Site).get(slug="active"),
                "tenant": cls.tenant,
            },
        )
        manufacturer, _ = Manufacturer.objects.get_or_create(name="Test Manufacturer 1", slug="test-manufacturer-1")
        cls.device_type, _ = DeviceType.objects.get_or_create(
            manufacturer=manufacturer,
            model="Test Device Type 1",
            slug="test-device-type-1",
        )
        cls.device_role, _ = DeviceRole.objects.get_or_create(name="Test Device Role 1", slug="test-device-role-1")
        cls.status = Status.objects.get_for_model(Device).get(slug="active")
        cls.device_data = {
            "name": "Test Device 1",
            "site": cls.site,
            "tenant": cls.tenant,
            "status": cls.status,
            "device_type": cls.device_type,
            "device_role": cls.device_role,
        }


class CPUSetUp(DeviceSetUp, TestCase):
    """Provide test CPU instance"""

    def setUp(self):
        super().setUp()
        self.cpu, _ = CPU.objects.get_or_create(**self.cpu_data)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cpu_manufacturer, _ = Manufacturer.objects.get_or_create(
            slug="intel",
            defaults={
                "name": "Intel",
            },
        )
        cls.cpu_data = {
            "manufacturer": cls.cpu_manufacturer,
            "name": "Test CPU 1",
            "cores": 8,
        }


class DeviceResourceSetUp(CPUSetUp, TestCase):
    """Provide test DeviceResource instance"""

    def setUp(self):
        super().setUp()
        self.resources, _ = DeviceResource.objects.get_or_create(
            device=self.device,
            cpu=self.cpu,
            cpu_count="5",
            gpu="Test GPU 1",
            ram="256",
            disks="2x512 GB SSD, 24x4 TB SAS SSD (2xRAID 5 with 12 discs)",
        )
