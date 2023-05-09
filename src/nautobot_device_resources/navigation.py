from nautobot.core.apps import NavMenuAddButton
from nautobot.core.apps import NavMenuGroup
from nautobot.core.apps import NavMenuImportButton
from nautobot.core.apps import NavMenuItem
from nautobot.core.apps import NavMenuTab

from .consts import PLUGIN_NAME

menu_items = (
    NavMenuTab(
        name="Devices",
        groups=(
            NavMenuGroup(
                name="Device Components",
                items=(
                    NavMenuItem(
                        link=f"plugins:{PLUGIN_NAME}:cpu_list",
                        name="CPUs",
                        weight=40,
                        permissions=[f"{PLUGIN_NAME}.view_cpu"],
                        buttons=(
                            NavMenuAddButton(
                                link=f"plugins:{PLUGIN_NAME}:cpu_add",
                                permissions=[
                                    f"{PLUGIN_NAME}.add_cpu",
                                ],
                            ),
                            NavMenuImportButton(
                                link=f"plugins:{PLUGIN_NAME}:cpu_import",
                                permissions=[f"{PLUGIN_NAME}.add_cpu"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
