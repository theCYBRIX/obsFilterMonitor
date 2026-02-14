import os
import sys
import obspython as obs # pyright: ignore[reportMissingImports]
import json
from configparser import RawConfigParser
import os.path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread
import random
import time
from typing import (
    # Any,
    # Awaitable,
    Optional
)
import asyncio
try:
    from websockets.legacy.server import (
        Serve,
        serve,
        WebSocketServerProtocol
    )
except:
    print("Missing import websockets 9.1.\n\tIn your OBS Python installation run 'pip install websockets==9.1'")


    # TODO: Make monitor.html use Websocket for settings request
    # TODO: Make monitor.html receive refresh requests from Websocket


DEFAULT_RETRY_FREQUENCY: float = 0.5
DEFAULT_RETRY_DURATION: float = 2.0
PORT = 6005
SCRIPT_PATH: str = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
CONFIG_FILE: str = SCRIPT_PATH + "config.json"
STATE_FILE: str = SCRIPT_PATH + "script_state.ini"


class ScriptContext:
    def __init__(self) -> None:
        self.obs_properties = None
        self.obs_data = None
        self.debug: bool = False

    def debug_message(self, msg: str) -> None:
        if self.debug:
            print(msg)

    def print_error(self, message: str) -> None:
        print(message, file=sys.stderr)

    def clear(self) -> None:
        self.obs_properties = None
        self.obs_data = None


class SettingsServer:
    def __init__(self) -> None:
        self.settings_server : Optional[Serve] = None
        self.websocket_peers : list[WebSocketServerProtocol] = []
        self.asyncio_thread : Optional[Thread] = None
        self.asyncio_loop : Optional[asyncio.AbstractEventLoop] = None

    def clear(self):
        self.asyncio_loop = None
        self.asyncio_thread = None
        self.settings_server = None

    def start(self, host : str = "localhost", port : int = PORT) -> None:
        SCRIPT_CONTEXT.debug_message('Starting settings server...')

        def run_service():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.asyncio_loop = loop

            start_server = serve(self.handle_websocket, host, port)
            self.settings_server = start_server

            loop.run_until_complete(start_server)
            loop.run_forever()
        
        thread = Thread(target=run_service, name="Settings Server", daemon=True)
        self.asyncio_thread = thread
        thread.start()

    def stop(self, code : int = 1000, reason : str = "") -> None:
        if not self.asyncio_loop:
            return

        SCRIPT_CONTEXT.debug_message("Shutting down settings server...")
        
        asyncio_loop = self.asyncio_loop

        async def close_all():
            if self.settings_server:
                for peer in self.websocket_peers:
                    await peer.close(code, reason)
                self.settings_server.ws_server.close()
                await self.settings_server.ws_server.wait_closed()
            asyncio_loop.stop()
        
        asyncio.run_coroutine_threadsafe(close_all(), self.asyncio_loop)

    async def handle_websocket(self, websocket : WebSocketServerProtocol, path : str):# -> Awaitable[Any]:
        self.websocket_peers.append(websocket)
        async for message in websocket:
            SCRIPT_CONTEXT.debug_message(f"Received> {message}")
            if message == "?settings":
                await websocket.send(json.dumps(settings_as_dict(SCRIPT_CONTEXT.obs_data)))
                SCRIPT_CONTEXT.debug_message("OK> Request handled.")
            elif message == "!stop":
                await websocket.send("Terminating Websocket Server...")
                SCRIPT_CONTEXT.debug_message("OK> Request handled.")
                self.stop(reason="Shutdown requested.")
                return
            elif message in ("test", "testing", "hello", "hi"):
                await websocket.send(random.choice(("Well, hello there!", "Hi~! ^_^", "Hello! :D")))
                SCRIPT_CONTEXT.debug_message("OK> Completed social obligations.")
            else:
                SCRIPT_CONTEXT.debug_message(f'Request rejected: "{message}"')
                await websocket.send(f'ERROR> Unknown request "{message}"')


SCRIPT_CONTEXT: ScriptContext = ScriptContext()
SETTINGS_SERVER : SettingsServer = SettingsServer()


def script_load(settings) -> None:
    load_state()
    SCRIPT_CONTEXT.obs_data = settings
    SETTINGS_SERVER.start()


def script_unload():
    SETTINGS_SERVER.stop(reason="Script Unloading.")

    if SETTINGS_SERVER.asyncio_thread:
        SETTINGS_SERVER.asyncio_thread.join()

    SCRIPT_CONTEXT.clear()
    SETTINGS_SERVER.clear()


def script_save(settings) -> None:
    save_state()


def script_defaults(settings) -> None:
    swing_array = obs.obs_data_array_create()
    obs.obs_data_set_default_array(settings, "_filter_list", swing_array)
    obs.obs_data_set_default_string(settings, "_pass", "secret-password")
    obs.obs_data_set_default_string(settings, "_address", "127.0.0.1")
    obs.obs_data_set_default_int(settings, "_port", int(4455))
    obs.obs_data_set_default_int(settings, "_color", int("ff32Cd32", 16))
    obs.obs_data_set_default_string(
        settings, "_browser_dock_name", "Filter Monitor")


def script_description():
    return "<h1>OBS Filter Monitor Config</h1>\n<p>Add and remove filters from OBS Filter Monitor on the fly.</p>"


# Initializes UI elements
def script_properties():

    props = obs.obs_properties_create()

    # Filter Monitor Elements
    filter_group = obs.obs_properties_create()
    obs.obs_properties_add_editable_list(
        filter_group, "_filter_list", "Filters: ", obs.OBS_EDITABLE_LIST_TYPE_STRINGS, "", "")

    obs.obs_properties_add_text(
        filter_group, "_source", "Source: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        filter_group, "_filter", "Filter: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        filter_group, "_name", "Display Name: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_color(filter_group, "_color", "Active Color: ")
    obs.obs_properties_add_button(
        filter_group, "add_button", "Add Filter", on_add_filter_pressed)
    obs.obs_properties_add_group(
        props, "_filter_monitor", "Filter Monitor Elements", obs.OBS_GROUP_NORMAL, filter_group)

    # OBS Websocket
    obs_websocket_group = obs.obs_properties_create()
    obs.obs_properties_add_text(
        obs_websocket_group, "_address", "Address: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(
        obs_websocket_group, "_port", "Port: ", 0, 65535, 1)
    obs.obs_properties_add_text(
        obs_websocket_group, "_pass", "Password: ", obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_group(
        props, "_obs_websocket", "OBS Websocket Settings", obs.OBS_GROUP_NORMAL, obs_websocket_group)

    # Import Layout
    import_group = obs.obs_properties_create()
    obs.obs_properties_add_path(import_group, "_import_path",
                                "Import Path: ", obs.OBS_PATH_FILE, "*.json", SCRIPT_PATH)

    import_options = obs.obs_properties_add_list(
        import_group, "_import_method", "Import method: ", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        import_options, 'Add Filters', "_import_add_filters")
    obs.obs_property_list_add_string(
        import_options, 'Set Filters', "_import_set_filters")
    obs.obs_property_list_add_string(
        import_options, 'Set Websocket', "_import_set_websocket")
    obs.obs_property_list_add_string(
        import_options, 'Set All', "_import_set_all")

    obs.obs_properties_add_button(
        import_group, "_import_btn", 'Import', on_import_config_pressed)
    obs.obs_properties_add_group(
        props, "_import", "Import Layout", obs.OBS_GROUP_NORMAL, import_group)

    # Export Current Layout
    export_settings = obs.obs_properties_create()
    obs.obs_properties_add_path(export_settings, "_export_path",
                                "Export Path: ", obs.OBS_PATH_FILE_SAVE, "*.json", CONFIG_FILE)
    obs.obs_properties_add_button(
        export_settings, "_export_btn", 'Export', on_export_config_pressed)
    obs.obs_properties_add_group(
        props, "_export", "Export Current Layout", obs.OBS_GROUP_NORMAL, export_settings)

    # Debug Button
    obs.obs_properties_add_button(props, "_debug",
                                  f'Debug {"Enabled" if SCRIPT_CONTEXT.debug else "Disabled"}', on_debug_toggled)

    SCRIPT_CONTEXT.obs_properties = props

    return props

def on_add_filter_pressed(props, prop, *args, **kwargs) -> bool:
    data = SCRIPT_CONTEXT.obs_data
    add_filters(
        data, [{
            "filterName": obs.obs_data_get_string(data, "_filter"),
            "sourceName": obs.obs_data_get_string(data, "_source"),
            "displayName": obs.obs_data_get_string(data, "_name"),
            "onColor": int_to_rgb_hex(obs.obs_data_get_int(data, "_color"))
        }]
    )
    return True


def on_debug_toggled(props, prop) -> bool:
    SCRIPT_CONTEXT.debug = not SCRIPT_CONTEXT.debug
    obs.obs_property_set_description(
        prop, f'Debug {"Enabled" if SCRIPT_CONTEXT.debug else "Disabled"}')
    return True


def on_export_config_pressed(props, prop) -> bool:
    data = SCRIPT_CONTEXT.obs_data
    file_path: str = obs.obs_data_get_string(data, "_export_path")
    save_config(data, file_path)
    return True


def on_import_config_pressed(props, prop) -> bool:
    data = SCRIPT_CONTEXT.obs_data
    import_method = obs.obs_data_get_string(data, "_import_method")
    file_path: str = obs.obs_data_get_string(data, "_import_path")

    try:
        filterList, password, host = load_config(file_path)

        if import_method == "_import_add_filters":
            if not filterList:
                raise ValueError("Missing filterList")
            add_filters(data, filterList)

        if import_method == "_import_set_filters" or import_method == "_import_set_all":
            if not filterList:
                raise ValueError("Missing filterList")
            set_filters(data, filterList)

        if import_method == "_import_set_websocket" or import_method == "_import_set_all":
            if not (host and password):
                raise ValueError("Missing obsHost and/or password")
            set_websocket(data, host)
            obs.obs_data_set_string(data, "_pass", password)

    except FileNotFoundError or IsADirectoryError as error:
        SCRIPT_CONTEXT.print_error(f"Unable to load config: {error}")
    except ValueError as error:
        raise ValueError(f"Unable to find requested keys in file: {error}")

    return True


def add_filters(data, filters: list) -> None:
    swing_array = obs.obs_data_get_array(data, "_filter_list")
    swing_array_append_filters(swing_array, filters)
    obs.obs_data_array_release(swing_array)


def set_filters(data, filters: list) -> None:
    swing_array = obs.obs_data_array_create()
    swing_array_append_filters(swing_array, filters)
    prev_array = obs.obs_data_get_array(data, "_filter_list")
    obs.obs_data_set_array(data, "_filter_list", swing_array)
    obs.obs_data_array_release(prev_array)


def get_filters(settings):
    swing_array = obs.obs_data_get_array(settings, "_filter_list")
    array_size = obs.obs_data_array_count(swing_array)
    filters: list[dict] = []
    for i in range(array_size):
        swing_item = obs.obs_data_array_item(swing_array, i)
        filters.append(swing_item_to_dict(swing_item))
        obs.obs_data_release(swing_item)
    obs.obs_data_array_release(swing_array)
    return filters


def set_websocket(data, obsHost: str) -> None:
    address, port = obsHost.split(":")
    obs.obs_data_set_int(data, "_port", int(port))
    obs.obs_data_set_string(data, "_address", address)


def save_config(settings, file_path: str) -> None:
    try:
        save_to_file(file_path, json.dumps(settings_as_dict(settings)))
        SCRIPT_CONTEXT.debug_message(f"Saved config to: {file_path}")
    except (FileNotFoundError, ValueError) as error:
        SCRIPT_CONTEXT.debug_message(f"Failed to save config file: {error}")


def load_config(file_path: str):
    config: dict = json.loads(load_from_file(file_path))
    return config.get("filterList", None), config.get("obsPassword", None), config.get("obsHost", None)


def save_state() -> None:
    try:
        parser = RawConfigParser()
        parser.add_section("STATE")
        parser["STATE"]['debug'] = 'enabled' if SCRIPT_CONTEXT.debug else 'disabled'
        mode: str = get_available_write_mode(STATE_FILE)
        with open(STATE_FILE, mode, encoding="UTF-8") as file:
            parser.write(file)
        SCRIPT_CONTEXT.debug_message(f"State saved to: {STATE_FILE}")
    except BaseException as error:
        SCRIPT_CONTEXT.debug_message(f"Error saving state: {error}")


def load_state() -> None:
    if not os.path.isfile(STATE_FILE):
        return
    parser = RawConfigParser()
    parser.read(STATE_FILE)
    SCRIPT_CONTEXT.debug = (parser['STATE']['debug'] is 'enabled')


def save_to_file(file_path: str, data: str) -> None:
    mode: str = get_available_write_mode(file_path)
    with open(file_path, mode, encoding="UTF-8") as file:
        file.write(data)


def load_from_file(file_path: str) -> str:
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Unable to locate config file: {file_path}")
    if not os.path.isfile(file_path):
        raise IsADirectoryError(f"Path is not a file: {file_path}")
    data: str
    with open(file_path, encoding="UTF-8") as file:
        data = file.read()
    return data


def get_available_write_mode(file_path: str) -> str:
    file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        return "w"

    parent_dir = os.path.dirname(file_path)
    if os.path.isdir(parent_dir):
        return "x"

    raise FileNotFoundError(
        f'Requested directory does not exist: {parent_dir}')


def settings_as_dict(settings) -> dict:
    host_address = obs.obs_data_get_string(settings, "_address")
    port = obs.obs_data_get_int(settings, "_port")
    obs_password = obs.obs_data_get_string(settings, "_pass")

    return {"obsHost": f'{host_address}:{port}',
            "obsPassword": obs_password,
            "filterList": get_filters(settings)}


def swing_item_to_dict(swing_array_item) -> dict:
    obj = obs.obs_data_get_json(swing_array_item)
    return json.loads(json.loads(obj)["value"])


def swing_array_append_filters(swing_array, filters: list) -> None:
    for filter in filters:
        try:
            item_as_json = create_list_item_json(filter["filterName"], filter["sourceName"], filter.get(
                "displayName", None), filter.get("onColor", None))
            swing_item = obs.obs_data_create_from_json(item_as_json)
            obs.obs_data_array_push_back(swing_array, swing_item)
            obs.obs_data_release(swing_item)
        except:
            SCRIPT_CONTEXT.debug_message(
                f"Failed to parse filter: {json.dumps(filter)}")


def int_to_rgb_hex(num: int) -> str:
    hex_str = hex(num)  # 0xAABBGGRR (The obs_data_get_int color format)

    r = hex_str[8:10]
    g = hex_str[6:8]
    b = hex_str[4:6]

    return "".join(('#', r, g, b))


def create_list_item_json(filter_name: str, source_name: str, display_name: str = "", on_color: str = "") -> str:
    filter = '{\\\"filterName\\\": \\\"%s\\\", \\\"sourceName\\\": \\\"%s\\\"' % (
        filter_name, source_name)
    if display_name != "":
        filter += f', \\\"displayName\\\": \\\"{display_name}\\\"'
    if on_color != "":
        filter += f', \\\"onColor\\\": \\\"{on_color}\\\"'
    filter += "}"
    return '{"value":"%s","selected":false,"hidden":false}' % filter
