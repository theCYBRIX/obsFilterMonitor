# Manual Configuration

### Table of Contents
- [Introduction](#introduction)
- [Editing monitor.html](#editing-monitorhtml)
    - [Important First Steps](#important-first-steps)
    - [Quick Setup on Windows](#quick-setup-on-windows)
    - [Defining Filters](#defining-filters)
    - [Other Options / Settings](#other-options--settings)
- [FAQ](#faq)
    - [How to Find Color Codes](#how-to-find-color-codes)

### Introduction

Manual configuration can be done by editing the monitor.html file with a normal text editor.  
You only need [monitor.html](../monitor.html) (and the [websocket lib](https://cdn.jsdelivr.net/npm/obs-websocket-js@5.0/dist/obs-ws.global.min.js) auto-loaded from the internet) to run everything; All the other files (and the icons folder) are only there for project management and customization purposes.

By default it is configured with 5 example filter entries (shown in the [example image](https://cdn.lebaston100.de/git/obsfiltermonitor/example1.jpg) of the [readme](../README.md)).  
You can add or remove filters depending on your needs.  
**Note:** Make sure there is no "," after the last entry before the "]".

### Editing monitor.html

#### Important First Steps
Either use the [quick setup method](#quick-setup-on-windows) (Windows only), or do the following:
- Ensure you have the [OBS WebSocket Server enabled and configured](how-to-setup.md#enabling-obs-websocket-server).
    - If `Enable Authentication` was checked, make sure to update the [obsPassword](../monitor.html#L56) field (line 56).
- Ensure the "[useSettingsServer](../monitor.html#L62)" field within `monitor.html` (line 62) is set to `false` when using a manual configuration.

#### Quick setup on Windows:
- To automatically find the settings in your locally installed obs, run [transferSettings.bat](../transferSettings.bat).  
This can only be done once and also will disable use of the settings python script.

#### Defining Filters
The following options are available for the `filterslist` array beginning on [line 12](../monitor.html#L12):
- `filtername` (required): This is the name of the filter itself. This name is set when adding the filter or can be changed in obs and is displayed in the left list in the filter dialog.
- `sourceName` (required): This is the name of the source that the filter is on. If the filter is on a scene, use the scene name here instead.
- `displayName` (optional): If this property is set, the page will show this custom text instead of the source name followed by the filter name
- `onColor` (optional): This is a custom color (in a css format) that is displayed for the filter symbol in the -on- state



