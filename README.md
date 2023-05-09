# Nautobot Device Resources plugin

Plugin for [Nautobot](https://github.com/nautobot/nautobot) to provide device resources info (CPU, RAM, ...) to Nautobot (IPPlan) Device detail view.

This works by extending or replacing several core views to inject device resources information to various places with a goal of seamless integration and behaving as close to part of Nautobot Core as possible. It allows a user to interact with a `Device` and its `Resources` like it is a single model, completely removing any layering between `Device` and `DeviceResources` models.

The goal is to store data on Device HW configuration directly with a Device and to allow answers to questions like:
* Which `Devices` have this CPU model?
* How many `Devices` I have with more than 512GB RAM?
* Which `Devices` have more than 16 cores?
* When did we change disks configuration of this `Device`?

Please check the [Screenshots section](#screenshots) for detailed information on this plugin capabilities.

## View replacements

This plugin replaces some core views. If there is another plugin with core view replacement, please check if there is not a conflict. Replacing same view from multiple sources does not work!

Views replaced:
* dcim:device_add
* dcim:device_edit
* dcim:device_list
* dcim:device_import
* extras:objectchange

## Screenshots

Device view is extended to show resources on the right side. If any field (for example `GPU` is empty, it does not show at all).

![device_detail.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/device_detail.png)

Adding or editing device form is replaced to contain DeviceResources model fields at the very bottom.

![device_edit.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/device_edit.png)

`ObjectChange` view shows any change to `Device` or its `DeviceResources` directly, behaving like single core model. Here is a change to both Device (status) and its `DeviceResources` showing like single change. In reality those are 2 changes but to user it looks like this in UI:

![device_changelog.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/device_changelog.png)

Each CPU has its own model, directly linked from Device. There is direct link to a parent Manufacturer of the CPU and all Devices with this CPU (`Instances` count is direct link to Device list with a filter for this CPU).

![cpu_detail.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/cpu_detail.png)

Manufacturer detail is extended to show CPUs **only** when any CPU has this manufacturer (hidden otherwise). The `Instances` count is direct link to CPu list with this Manufacturer filter.

![manufacturer_detail.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/manufacturer_detail.png)

CPUs can be added through UI, the form is accessible from Device menu under `Device Components`.

![cpu_add.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/cpu_add.png)

Device list view is replaced to have columns for all the resources fields plus it supports filtering by the resources.

![device_list.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/device_list.png)

All CPUs can be listed and filtered in a new separate CPU model view.

![cpu_list.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/cpu_list.png)

Accessing all this data is possible via GraphQL and REST API too, but it is not merged to the core `Device` model APIs as Nautobot does not allow replacing API views. In GraphQL there is a link directly from `Device` called `resources` which provides the information in nested way. In REST API there is a separate endpoint `resources` under the installed plugin.

![graphql_device.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/graphql_device.png)
![rest_api.png](https://raw.githubusercontent.com/thetacz/nautobot-plugin-device-resources/master/docs/screenshots/rest_api.png)

## Development

Have running Nautobot instance (preferably in Docker) with this plugin installed.
Make sure you have `TEST_USE_FACTORIES = True` in you `nautobot_config.py`.

``` shell
pip install -e .[all]
pre-commit run --all-files
nautobot-server migrate
nautobot-server test nautobot_device_resources
```

### Build package

``` shell
pip install build
python -m build --sdist --wheel
twine check dist/*
```