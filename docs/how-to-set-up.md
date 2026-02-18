# How To Set up OBS Filter Monitor
[Return to main page](../README.md)

### Table of Contents
- [Getting the Project Files](#getting-the-project-files)
- [Ways to Set up FilterMonitor](#ways-to-set-up-filtermonitor)
    - [Dynamic Configuration Script](#using-config-script)
    - [Manual Configuration](#manual-config)
- [Set up Inside OBS](#set-up-inside-obs)
    - [Enabling OBS WebSocket Server](#enabling-obs-websocket-server)
    - [Adding the FilterMonitor Dock](#adding-the-filtermonitor-dock)
- [Advanced Usage](#advanced-usage)
    - [Monitoring for Another Device](#monitoring-from-another-device)
    - [Using the Tool Without an Internet Connection](#using-the-tool-without-an-internet-connection)


### Getting the Project Files
To get the repository files, either:
- [Download this repository](https://github.com/lebaston100/obsFilterMonitor/archive/master.zip) and unpack the zip file.
- Use git to clone the repo.


## Ways to Set up FilterMonitor
To set up and use FilterMonitor, you can either:

<a id="using-config-script"></a>
- [Use the configuration manager Python script](python-config.md) (easier to add, remove, reorder and modify filters whenever)
<a id="manual-config"></a>
- [Manually configure the monitor](manual-config.md) (Faster startup times; Less potential points of failure)

## Set up Inside OBS

### Enabling OBS WebSocket Server
- In OBS, go to `Tools > WebSocket Server Settings`
- Under `Plugin Settings`, ensure that `Enable Websocket server` is checked
- Make sure that `Server Port` is set to 4455
- If `Enable Authentication` is checked:
    - go to `Show Connect Info` to view the WebSocket password; You may need this later.


### Adding the FilterMonitor Dock

To create a custom dock that can be part of the OBS window:
- Open OBS
- Go to `Docks > Custom Browser Docks`
- Under `Dock Name` enter a name for the new panel
- On the right side under `URL` enter the path to the monitor.html file.
    - For example: "C:\obsFilterMonitor-master\monitor.html"
- Click `Apply`.

This should open a new dock containing the filter monitor.  
You can drag this dock into the obs interface or place have it popped out of the interface in a separate window.  
**Note:** If you close the filter monitor dock, you can either find it under `Docks > {your-monitor-name}` or simply add it again.


## Customizing FilterMonitor

### Modifying Visuals
- [defaultOffColor](../monitor.html#L28) (line 28): This is the css color for the -off- state
- [defaultOffSymbol](../monitor.html#L30) (line 30): This is the symbol that is overlaid over the defaultOffColor. Can be:
    - [g_x_black](../monitor.html#L22) - a black X
    - [g_x_white](../monitor.html#L23) - a white X
    - [g_off_black](../monitor.html#L24) - black "off" text
    - [g_off_white](../monitor.html#L25) - white "off" text
    - [g_placeholder](../monitor.html#L19) - no overlay, only color
    - Refer to [Creating Custom Overlay Symbols](#creating-custom-overlay-symbols)
- [fallbackOnColor](../monitor.html#L39) (line 39): This is the css color that is used for the -on- state when no "onColor" is set

#### Creating Custom Overlay Symbols
You can create custom overlay symbols (such as the "X" or "off" text) for disabled filters by doing the following:
- make a 40x30 png image with transparent background.
- Encode the image in base64.
- Add the image as a new variable as seen in [monitor.html](../monitor.html#L19-L25) (Lines 19-25)
- Specify your image as the [defaultOffSymbol](../monitor.html#L30) (line 30).


### FAQ
#### How to find color codes
To generate the css color codes, search google for "css color picker".  
Select the desired color and use the value displayed under "HEX" (Include the "#"; If the value starts with "0x" replace this with "#").

## Advanced usage
For those that know what they are doing. For any help, refer to the [help section](../README.md#help).

### Monitoring from Another Device
- Create a firewall exception for the obs-websocket port (4455 by default)
- If using the python script, do the same for the settings-websocket port (6005 by default)
- In monitor.html:
    - Modify the [obsHost](../monitor.html#L53) ip address (line 53) to reflect that of the machine running OBS.
    - If using the python script, do the same for [obsSettingsHost](../monitor.html#L59) (line 59).

The host for the settings script web server can be changed in [monitor.html](../monitor.html#L53) (line 53).  

### Using the tool without an internet connection  
If you want to use the tool without an internet connection:
- Download [this file](https://cdn.jsdelivr.net/npm/obs-websocket-js@5.0/dist/obs-ws.global.min.js) (making sure not to rename it)
- Place the file in the same folder as monitor.html
- In monitor.html:
    - Uncomment [line 8](../monitor.html#L8)
    - Comment out [line 7](../monitor.html#L7) (`<!-- This is a comment -->`)

<p align="center" style="margin: 2rem">
    <a href =#how-to-set-up-obs-filter-monitor>Back to top</a>
</p>