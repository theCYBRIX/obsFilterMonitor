# Manual Configuration
[Return to main page](../README.md)

### Table of Contents
- [Introduction](#introduction)
- [Important First Steps](#important-first-steps)
- [Quick Setup on Windows](#quick-setup-on-windows)
- [Defining Filters](#defining-filters)

### Introduction

Manual configuration can be done by **editing the monitor.html file** with a normal text editor.  
You only need [monitor.html](../monitor.html) (and the [websocket lib](https://cdn.jsdelivr.net/npm/obs-websocket-js@5.0/dist/obs-ws.global.min.js) auto-loaded from the internet) to run everything; All the other files (and the icons folder) are only there for project management and customization purposes.

### Important First Steps
1) Ensure you have the [OBS WebSocket Server enabled and configured](set-up-inside-obs.md#enabling-obs-websocket-server).
2) Either use the [quick setup method](#quick-setup-on-windows) (Windows only), or do the following:
    - If `Enable Authentication` is checked in `WebSocket Server Settings`, make sure to update the "[obsPassword](../monitor.html#L56)" field in `monitor.html` (line 56).
    - Ensure the "[useSettingsServer](../monitor.html#L62)" field within `monitor.html` (line 62) is set to `false` when using a manual configuration.

### Quick setup on Windows:
To automatically find the settings in your locally installed obs, run [transferSettings.bat](../transferSettings.bat).  
This can only be done once and will also disable use of the settings python script.

### Defining Filters
The following options are available for the "[filterslist](../monitor.html#L12)" array in `monitor.html` (line 12):
- `filtername` (required): This is the name of the filter itself. This name is set when adding the filter or can be changed in obs and is displayed in the left list in the filter dialog.
- `sourceName` (required): This is the name of the source that the filter is on. If the filter is on a scene, use the scene name here instead.
- `displayName` (optional): If this property is set, the page will show this custom text instead of the source name followed by the filter name
- `onColor` (optional): This is a custom color (in a css format) that is displayed for the filter symbol in the -on- state

By default, FilterMonitor is configured with 5 example filter entries (shown in the [example image](https://cdn.lebaston100.de/git/obsfiltermonitor/example1.jpg)). You can add, edit or remove filters depending on your needs.  
**Note:** Make sure there is no "," after the last entry before the "]".