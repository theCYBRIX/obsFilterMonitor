This tool shows if one or multiple filters are enabled or disabled. Runs inside OBS custom browser docks or any modern web browser. You can also click on the status to toggle the filter.

![Example image](https://cdn.lebaston100.de/git/obsfiltermonitor/example1.jpg)

### Requirements

- OBS 28 and up

### Setup

- Start OBS, open the "Tools" menu and select "obs-websocket Settings"
- Make sure that "Enable Websocket server" is checked, "Server Port" is 4455
- Copy the websocket password(If "Enable Authentication" is enabled) for later by clicking on "Show Connect Info"-Button -> Next to the "Server Password" field -> "Copy"-Button
- [Download this repository](https://github.com/lebaston100/obsFilterMonitor/archive/master.zip) or clone it (you only need the monitor.html file)

### Configuration using Python script

- Start OBS, open the "Tools" menu and select "Scripts"
- Ensure a valid [Python 3.6.x](https://www.python.org/downloads/) Install Path is defined in the "Python Settings" tab
- Add "[filter-monitor-config.py](./filter-monitor-config.py)" to the "Loaded Scripts" list in the "Scripts" tab
- Select "filter-monitor-config" from the "Loaded Scripts" list, and configure OBS Filter Monitor to your liking, then refresh the monitor.html dock to load the new settings

**Important**: Ensure the "[useSettingsServer](./monitor.html#L45)" field within monitor.html is set to "true" in order to configure the monitor using filter-monitor-config.

[Comment]: <> (Temporary image link)
![Example image](https://private-user-images.githubusercontent.com/102550532/314358838-c2916662-ee9d-4064-9446-c46bd6d6bd76.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzA4NTEyMjQsIm5iZiI6MTczMDg1MDkyNCwicGF0aCI6Ii8xMDI1NTA1MzIvMzE0MzU4ODM4LWMyOTE2NjYyLWVlOWQtNDA2NC05NDQ2LWM0NmJkNmQ2YmQ3Ni5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQxMTA1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTEwNVQyMzU1MjRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kMDRmYmM4NWMxN2Q2MWQ2NGY4OWEyMjRiMWVlYTZmMjRhMzEwZjQ3ZjBiMjk3MWM3NTBhOWQxN2EyMGFlOTk4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.gSP0iZmCQ-sOjlSyQQfMt3Pi1WgAPjBA-Z4zF5ouUW8.jpg) 


### Manual Configuration

Manual configuration can be done by editing the monitor.html file with a normal text editor. You also only need this file (and the websocket lib auto-loaded from the internet) to run everything, all the other files (and the icons folder) is just there for project management purposes or if you want to customize stuff.

By default it is configured with 5 example filter entrys which result in the image shown above. You can remove or add filters depending on what you need. Make sure there is no "," after the last entry before the "]". Just follow the format that is already there if you don't know how to use Javascript arrays and objects.

The following options are available for the main array beginning in line 11:
- "filtername" (required): This is the name of the filter itself. This name is set when adding the filter or can be changed in obs and is displayed in the left list in the filter dialog.
- "sourceName" (required): This is the name of the source that the filter is on. If the filter is on a scene, use the scene name here instead.
- "displayName" (optional): If this property is set, the page will show this custom text instead of the source name followed by the filter name
- "onColor" (optional): This is a custom color (in a css format) that is displayed for the filter symbol in the -on- state

(required) means that this property has to exist for it to work, (optional) means that you can use it, but don't have to have it present.

Other options that you can use/set:
- defaultOffColor (line 27): This is the css color for the -off- state
- defaultOffSymbol (line 29): This is the symbol that is overlayed over the defaultOffColor. Can be:
	- g_x_black (a black X)
	- g_x_white (a white X)
	- g_off_black (black "off" text)
	- g_off_white (white "off" text)
	- g_placeholder (no overlay, only color)
- fallbackOnColor (line 32): This is the css color that is used for the -on- state when no "onColor" is set

If you want to generate the css color codes, search google for "css color picker" and you will get a color picker. Just use the value displayed under "HEX" (please include the "#").

If "Enable Websocket server" was checked and you have a password then make sure to update the "obsPassword" config option in line 38.

**Important**: Ensure the "[useSettingsServer](./monitor.html#L45)" field within monitor.html is set to "false" to stop the monitor from attempting to fetch settings from filter-monitor-config.

### Setup inside OBS

To create a custom dock that can be made part of the main OBS window, follow these steps:
- Open OBS
- Open the "View" menu on the top and select "Docks" -> "Custom Browser Docks..."
- Under "Dock Name" enter a name for the new panel
- On the right side under "URL" enter the URL to the monitor.html file. For example if your file is inside "C:\obsFilterMonitor-master\monitor.html" then use exactly that.
- Click the "Apply" button. This should open the dock. You can drag that into the obs interface or place it wherever you want.
- That's it. If you changed something in the file you can use CTRL + R to reload the page.

### Advanced usage

If you know what you are doing you can create a firewall exception for the obs-websocket port and modify the ip address in line 35 to be able to run this on any device in the network.

You can create custom overlay symbols(the X or off text) by making a transparent 40x30 png image and then encoding it in base64. Then add that as a new variable and specify it as the defaultOffSymbol.

If you want to use the tool offline aka without an internet connection you need to download [this file](https://cdn.jsdelivr.net/npm/obs-websocket-js@5.0.1/dist/obs-ws.min.js) making sure not to rename it, place it in the same folder as the monitor.html, uncomment line 8 and comment out line 7(also in the monitor.html).

### Help

You have trouble setting it up or found a bug, then join my [Discord Server](https://discord.gg/PCYQJwX)

Thanks to [Strike](https://www.twitch.tv/strike) for the idea for this.
