from nautobot.core.api import OrderedDefaultRouter

from . import views

router = OrderedDefaultRouter()

router.register("resources", views.DeviceResourceViewSet)
router.register("cpus", views.CPUViewSet)

urlpatterns = router.urls
