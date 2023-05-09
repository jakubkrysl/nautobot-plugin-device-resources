from rest_framework.viewsets import ModelViewSet

from ..filters import CPUFilterSet
from ..filters import DeviceResourceFilterSet
from ..models import CPU
from ..models import DeviceResource
from .serializers import CPUSerializer
from .serializers import DeviceResourceSerializer


# pylint: disable-next=too-many-ancestors
class DeviceResourceViewSet(ModelViewSet):
    """API viewset for interacting with DeviceResource objects."""

    queryset = DeviceResource.objects.all()
    filterset_class = DeviceResourceFilterSet
    serializer_class = DeviceResourceSerializer


# pylint: disable-next=too-many-ancestors
class CPUViewSet(ModelViewSet):
    """API viewset for interacting with CPU objects."""

    queryset = CPU.objects.all()
    filterset_class = CPUFilterSet
    serializer_class = CPUSerializer
