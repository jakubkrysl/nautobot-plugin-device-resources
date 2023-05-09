from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import reverse
from nautobot.core.fields import AutoSlugField
from nautobot.core.models.generics import OrganizationalModel
from nautobot.extras.utils import extras_features

from .consts import PLUGIN_NAME


@extras_features(
    "export_templates",
    "graphql",
)
# pylint: disable-next=too-many-ancestors
class DeviceResource(OrganizationalModel):
    """Single record of device resources."""

    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="resources",
        null=False,
        unique=True,
    )
    cpu = models.ForeignKey(
        to=f"{PLUGIN_NAME}.CPU",
        verbose_name="CPU",
        on_delete=models.PROTECT,
        related_name="instances",
        blank=True,
        null=True,
    )
    cpu_count = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="CPU count")
    gpu = models.CharField(max_length=200, blank=True, verbose_name="GPU")
    ram = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="RAM", help_text="Value in GB")
    disks = models.CharField(max_length=200, blank=True)

    # pylint: disable-next=too-few-public-methods
    class Meta:
        ordering = ["device"]
        verbose_name = "Device Resource"
        verbose_name_plural = "Device Resources"

    def __str__(self) -> str:
        """Overwrite __str__ method to return correct item."""
        return str(self.device) or super().__str__()

    @property
    def label(self) -> str:
        """Set label so pynautobot has string representation of the object."""
        return str(self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def cpu_threads(self) -> int | None:
        """Calculate total number of CPU threads."""
        if not self.cpu:
            return None
        return self.cpu.threads * self.cpu_count

    def clean(self):
        super().clean()
        # remove cores when removing CPU
        if self.cpu is None and self.present_in_database and DeviceResource.objects.get(id=self.id).cpu_count:
            self.cpu_count = None

        if self.cpu and not self.cpu_count:
            raise ValidationError(
                {
                    "cpu_count": "Please set number of CPUs when setting 'CPU'.",
                }
            )
        if self.cpu_count and not self.cpu:
            raise ValidationError(
                {
                    "cpu_count": "Cannot set 'CPU count' without setting 'CPU'.",
                }
            )


@extras_features(
    "export_templates",
    "graphql",
)
# pylint: disable-next=too-many-ancestors
class CPU(OrganizationalModel):
    """Single record of device CPU."""

    manufacturer = models.ForeignKey(to="dcim.Manufacturer", on_delete=models.PROTECT, related_name="cpus")
    name = models.CharField(max_length=200, blank=False, verbose_name="CPU")
    slug = AutoSlugField(populate_from="name", unique=True, db_index=True)
    cores = models.PositiveSmallIntegerField(blank=False, verbose_name="CPU cores", help_text="Number of cores")
    threads_per_core = models.PositiveSmallIntegerField(
        blank=False, null=False, verbose_name="Threads per Core", help_text="Number of threads per core.", default=2
    )

    csv_headers = ["name", "slug", "manufacturer", "cores", "threads_per_core"]

    # pylint: disable-next=too-few-public-methods
    class Meta:
        ordering = ["name"]
        verbose_name = "CPU"
        verbose_name_plural = "CPUs"

    def __str__(self) -> str:
        """Overwrite __str__ method to return correct item."""
        return str(self.name)

    @property
    def label(self) -> str:
        """Set label so pynautobot has string representation of the object."""
        return str(self)

    @property
    def threads(self) -> int | None:
        """Calculate number of CPU threads from cores."""
        return self.cores * self.threads_per_core

    def clean(self):
        super().clean()

        # make sure threads_per_core is power of 2 (including 1)
        if self.threads_per_core and not (self.threads_per_core & (self.threads_per_core - 1) == 0):
            raise ValidationError(
                {
                    "threads_per_core": f"Invalid value {self.cores}, must be power of 2,",
                }
            )

    def get_absolute_url(self):
        return reverse(f"plugins:{PLUGIN_NAME}:cpu", args=[self.slug])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.manufacturer.name,
            self.cores,
            self.threads_per_core,
        )
