# Set up Inside OBS
[Return to main page](../README.md)

### Table of Contents
- [Enabling OBS WebSocket Server](#enabling-obs-websocket-server)
- [Adding the FilterMonitor Dock](#adding-the-filtermonitor-dock)

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