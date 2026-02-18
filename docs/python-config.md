# Configuration using Python Script

### Table of Contents
- [Important First Steps](#important-first-steps)
- [Setup](#setup)
- [Adding monitor elements](#add-monitor-element)
- [Removing monitor elements](#remove-monitor-element)
- [Editing monitor elements](#edit-monitor-element)
- [Changing the order of elements](#changing-element-order)

### Important First Steps
- Ensure you have the [OBS WebSocket Server enabled and configured](how-to-setup.md#enabling-obs-websocket-server).
- Ensure the "[useSettingsServer](../monitor.html#L62)" field within `monitor.html` (line 62) is set to `true`.  
Otherwise the monitor will not retrieve settings from the `filter_monitor_config.py`.

### Setup

1) Start OBS and navigate to `Tools > Scripts`.
2) Ensure a valid Python <= 3.11 Install Path is defined in the `Python Settings` tab
3) In the `Scripts` tab, add `filter_monitor_config.py` to the `Loaded Scripts` list
4) Select `filter_monitor_config` from the list. More options will appear on the right.
5) If WebSocket authentication is enabled:
    - Scroll down to `OBS WebSocket Settings` and input your settings (Address/Port/Password)

<a id="add-monitor-element"></a>
To **add a new monitor element**:  
Below the `Filters` list, fill in the filter properties:
- `Source` name
- `Filter` name
- `Display Name` (optional)
- `Active Color`

Then press the `Add Filter` button.

**Note:** Unless you know what you are doing, don't edit the filter configurations inside the filters list by hand;  
If an element is incorrectly formatted, it can cause issues beyond just that specific single filter element.

<a id="remove-monitor-element"></a>
To **remove a monitor element**:  
In the `Filters` list
- Select the element
- Press the trash button on the right side of the list

<a id="edit-monitor-element"></a>
To **edit a monitor element**:
- Select the element from the list under `Use Existing Filter as Template` and press `Copy`.  
This will load the filter properties into the `Add Filter` section.
- Remove the existing filter from the `Filters` list. (Make sure the transferred properties are correct first)
- Make your changes and add your modified filter back to the list.

<a id="changing-element-order"></a>
To **change the order of monitor elements**:  
In the `Filters` list
- Select the element
- Use the `∧` and `∨` buttons on the right side of the list to shift the element's position


