import sys
import json
import random
import asyncio
from os import path
from typing import Optional
from threading import Thread
from configparser import RawConfigParser
import obspython as obs # pyright: ignore[reportMissingImports]
try:
    from lib.websockets.legacy.server import (
        Serve,
        serve,
        WebSocketServerProtocol
    )
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Missing import websockets 9.1.\n" +
        "\tIn the folder this script is in, run 'pip install websockets==9.1 -t ./lib'\n" +
        "\tEnsure the 'lib' directory contains an '__init__.py' file (the file can be empty)."
    ) from e
         

PORT = 6005
SCRIPT_PATH: str = path.dirname(path.abspath(__file__)) + path.sep
CONFIG_FILE: str = SCRIPT_PATH + "fm_config_export.json"
STATE_FILE: str = SCRIPT_PATH + "fm_config_state.ini"

FLT_DISPLAY_NAME: str = "displayName"
FLT_FILTER_NAME: str = "filterName"
FLT_SOURCE_NAME: str = "sourceName"
FLT_ON_COLOR: str = "onColor"

WS_SETTINGS: str = "settings"
WS_FILTERS_CHANGED: str = "filtersChanged"


class ScriptContext:
    def __init__(self) -> None:
        self.obs_data = None
        self.debug: bool = False
        self.obs_properties = None

        self.combo_initialized : bool = False

    def print_debug(self, msg: str) -> None:
        if self.debug:
            print(msg)

    def print_error(self, message: str) -> None:
        print(message, file=sys.stderr)

    def clear(self) -> None:
        self.obs_properties = None
        self.obs_data = None
        self.combo_initialized = False


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
        SCRIPT_CONTEXT.print_debug('Starting settings server...')

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

        SCRIPT_CONTEXT.print_debug("Shutting down settings server...")

        asyncio_loop = self.asyncio_loop

        async def close_all():
            if self.settings_server:
                for peer in self.websocket_peers:
                    await peer.close(code, reason)
                self.settings_server.ws_server.close()
                await self.settings_server.ws_server.wait_closed()
            asyncio_loop.stop()

        asyncio.run_coroutine_threadsafe(close_all(), self.asyncio_loop)

    # -> Awaitable[Any]:
    async def handle_websocket(self, websocket : WebSocketServerProtocol, url : str):
        self.websocket_peers.append(websocket)

        try:
            async for message in websocket:
                SCRIPT_CONTEXT.print_debug(f"Received> {message}")

                request = json.loads(message)

                request_type : Optional[str] = request.get("type", None)

                if request_type == WS_SETTINGS:
                    settings_dict : dict = settings_as_dict(SCRIPT_CONTEXT.obs_data)
                    settings_dict["type"] = WS_SETTINGS
                    await websocket.send(json.dumps(settings_dict))
                    SCRIPT_CONTEXT.print_debug("OK> Request handled.")

                elif request_type in ("test", "testing", "hello", "hi"):
                    await websocket.send(
                        random.choice(("Well, hello there!", "Hi~! ^_^", "Hello! :D"))
                    )
                    SCRIPT_CONTEXT.print_debug("OK> Completed social obligations.")

                else:
                    SCRIPT_CONTEXT.print_debug(f'Request rejected: "{message}"')
                    await websocket.send(f'ERROR> Unknown request "{message}"')
        finally:
            if websocket in self.websocket_peers:
                self.websocket_peers.remove(websocket)


    async def broadcast_message(self, message : str):# -> Awaitable[Any]:
        packet = json.dumps({"type" : message})
        for peer in self.websocket_peers:
            try:
                await peer.send(message)
            except Exception as e:
                SCRIPT_CONTEXT.print_error(f"Error sending message to peer: {e}")


SCRIPT_CONTEXT: ScriptContext = ScriptContext()
SETTINGS_SERVER : SettingsServer = SettingsServer()


def script_load(settings) -> None:
    load_state()
    SCRIPT_CONTEXT.obs_data = settings
    SETTINGS_SERVER.start()


def script_unload() -> None:
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
    obs.obs_data_set_default_string(settings, "_address", "localhost")
    obs.obs_data_set_default_int(settings, "_port", int(4455))
    obs.obs_data_set_default_int(settings, "_color", int("ff32Cd32", 16))
    obs.obs_data_set_default_string(
        settings, "_browser_dock_name", "Filter Monitor")


def script_description() -> str:
    return "<h1>OBS Filter Monitor Config</h1>\n" + \
    "<p>Modify OBS Filter Monitor on the fly.</p>"


# Initializes UI elements
def script_properties():

    props = obs.obs_properties_create()
    SCRIPT_CONTEXT.obs_properties = props

    # Start > Filter Monitor Elements
    filter_group = obs.obs_properties_create()
    filter_list = obs.obs_properties_add_editable_list(
        filter_group, "_filter_list", "", obs.OBS_EDITABLE_LIST_TYPE_STRINGS, "", "")
    obs.obs_property_set_modified_callback(filter_list, on_filter_list_changed)

    # >> Add Filter
    add_filter_group = obs.obs_properties_create()
    obs.obs_properties_add_text(
        add_filter_group, "_source", "Source: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        add_filter_group, "_filter", "Filter: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        add_filter_group, "_name", "Display Name: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_color(add_filter_group, "_color", "Active Color: ")
    obs.obs_properties_add_button(
        add_filter_group, "_add_button", "Add", on_add_filter_pressed)
    obs.obs_properties_add_group(
        filter_group, "_add_filter_group", "Add Filter", obs.OBS_GROUP_NORMAL, add_filter_group)

    # >> Copy Filter Properties
    copy_filter_group = obs.obs_properties_create()
    filter_combo = obs.obs_properties_add_list(
        copy_filter_group, "_filter_combo", "Filter: ",
        obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_INT
    )
    obs.obs_properties_add_button(
        copy_filter_group, "_copy_button", "Load Filters", on_copy_filter_pressed
    )
    obs.obs_properties_add_group(
        filter_group, "_copy_filter_group", "Use Existing Filter as Template",
        obs.OBS_GROUP_NORMAL, copy_filter_group
    )

    # End > Filter Monitor Elements
    obs.obs_properties_add_group(
        props, "_filter_monitor", "Filters", obs.OBS_GROUP_NORMAL, filter_group)

    # OBS Websocket
    obs_websocket_group = obs.obs_properties_create()
    obs.obs_properties_add_text(
        obs_websocket_group, "_address", "Address: ", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(
        obs_websocket_group, "_port", "Port: ", 0, 65535, 1)
    obs.obs_properties_add_text(
        obs_websocket_group, "_pass", "Password: ", obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_group(
        props, "_obs_websocket", "OBS Websocket Settings",
        obs.OBS_GROUP_NORMAL, obs_websocket_group
    )

    # Import Layout
    import_group = obs.obs_properties_create()
    obs.obs_properties_add_path(import_group, "_import_path",
                                "Import Path: ", obs.OBS_PATH_FILE, "*.json", SCRIPT_PATH)

    import_options = obs.obs_properties_add_list(
        import_group, "_import_method", "Import method: ",
        obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING
    )
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
                                  f'Debug {"Enabled" if SCRIPT_CONTEXT.debug else "Disabled"}',
                                  on_debug_toggled
                                )

    return props


def on_add_filter_pressed(props, prop, *args, **kwargs) -> bool:
    data = SCRIPT_CONTEXT.obs_data
    add_filters(
        props, data, [{
            FLT_FILTER_NAME: obs.obs_data_get_string(data, "_filter"),
            FLT_SOURCE_NAME: obs.obs_data_get_string(data, "_source"),
            FLT_DISPLAY_NAME: obs.obs_data_get_string(data, "_name"),
            FLT_ON_COLOR: int_to_rgb_hex(obs.obs_data_get_int(data, "_color"))
        }]
    )
    return True


def on_copy_filter_pressed(props, prop, *args, **kwargs) -> bool:
    data = SCRIPT_CONTEXT.obs_data
    selected_dict : Optional[dict] = get_selected_filter_as_dict(data)

    if selected_dict is None or not SCRIPT_CONTEXT.combo_initialized:
        update_filter_combo_box(data)
        update_copy_button_state(props)
        SCRIPT_CONTEXT.combo_initialized = True
        return True

    filter_name = selected_dict.get(FLT_FILTER_NAME, "")
    source_name = selected_dict.get(FLT_SOURCE_NAME, "")
    display_name = selected_dict.get(FLT_DISPLAY_NAME, "")
    on_color = selected_dict.get(FLT_ON_COLOR, "")

    if filter_name:
        obs.obs_data_set_string(data, "_filter", filter_name)
    if source_name:
        obs.obs_data_set_string(data, "_source", source_name)
    if display_name:
        obs.obs_data_set_string(data, "_name", display_name)
    if on_color:
        obs.obs_data_set_int(data, "_color", rgb_hex_to_int(on_color))
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
        filter_list, password, host = load_config(file_path)

        if import_method == "_import_add_filters":
            if not filter_list:
                raise ValueError("Missing filterList")
            add_filters(props, data, filter_list)

        if import_method in ("_import_set_filters", "_import_set_all"):
            if not filter_list:
                raise ValueError("Missing filterList")
            set_filters(props, data, filter_list)

        if import_method in ("_import_set_websocket", "_import_set_all"):
            if not (host and password):
                raise ValueError("Missing obsHost and/or password")
            set_websocket(data, host)
            obs.obs_data_set_string(data, "_pass", password)

    except (FileNotFoundError, IsADirectoryError) as error:
        SCRIPT_CONTEXT.print_error(f"Unable to load config: {error}")
    except ValueError as error:
        raise ValueError(f"Unable to find requested keys in file: {error}") from error

    return True


def on_filter_list_changed(props, prop, settings) -> bool:
    filter_list = get_filters(settings)

    update_filter_combo_box(settings, filter_list)
    update_copy_button_state(props)

    if SETTINGS_SERVER.asyncio_loop is not None:
        broadcast_msg : str = json.dumps(
                {
                    "type" : WS_FILTERS_CHANGED,
                    "filterList": filter_list
                }
            )
        asyncio.run_coroutine_threadsafe(
            SETTINGS_SERVER.broadcast_message(broadcast_msg),
            SETTINGS_SERVER.asyncio_loop
        )

    return True


def update_copy_button_state(props) -> None:
    copy_button = obs.obs_properties_get(props, "_copy_button")
    filter_combo = obs.obs_properties_get(props, "_filter_combo")
    item_count : int = obs.obs_property_list_item_count(filter_combo)
    if item_count > 0:
        obs.obs_property_set_description(copy_button, "Copy")
    else:
        obs.obs_property_set_description(copy_button, "Load Filters")


def update_filter_combo_box(data, filter_list : Optional[list] = None) -> None:
    if filter_list is None:
        filter_list = get_filters(data)

    item_names : list[str] = []
    for i, filter_props in enumerate(filter_list):
        item_names.append(get_readable_filter_name(i, filter_props))

    filter_combo = obs.obs_properties_get(SCRIPT_CONTEXT.obs_properties, "_filter_combo")
    obs.obs_property_list_clear(filter_combo)

    for index, name in enumerate(item_names):
        obs.obs_property_list_add_int(filter_combo, name, index)


def get_readable_filter_name(index : int, filter_dict : dict) -> str:
    name : Optional[str] = None

    if filter_dict is not None:
        if FLT_DISPLAY_NAME in filter_dict:
            name = filter_dict[FLT_DISPLAY_NAME]
        elif FLT_SOURCE_NAME in filter_dict or FLT_FILTER_NAME in filter_dict:
            if FLT_FILTER_NAME in filter_dict and FLT_SOURCE_NAME in filter_dict:
                name = f'{filter_dict[FLT_SOURCE_NAME]}  >  {filter_dict[FLT_FILTER_NAME]}'
            elif FLT_SOURCE_NAME in filter_dict:
                name = filter_dict[FLT_SOURCE_NAME]
            else:
                name = filter_dict[FLT_FILTER_NAME]

    return f'{name if name is not None else f"#{index + 1} (Unnamed)"}'


def get_selected_filter_as_dict(data) -> Optional[dict]:
    index : Optional[int] = obs.obs_data_get_int(data, "_filter_combo")
    if index is None or index < 0:
        if SCRIPT_CONTEXT.combo_initialized:
            SCRIPT_CONTEXT.print_error("Unable to get combo box value.")
        return None

    filter_list : list = get_filters(data)
    filter_count : int = len(filter_list)

    if index >= filter_count:
        if filter_count > 0:
            SCRIPT_CONTEXT.print_error(
                f"Invalid index {index} returned for selected filter. (# filters: {filter_count})")
        return None
    selected_item = filter_list[index]

    return selected_item


def add_filters(props, data, filters: list) -> None:
    swing_array = obs.obs_data_get_array(data, "_filter_list")
    swing_array_append_filters(swing_array, filters)
    obs.obs_data_array_release(swing_array)
    on_filter_list_changed(props, None, data)


def set_filters(props, data, filters: list) -> None:
    swing_array = obs.obs_data_array_create()
    swing_array_append_filters(swing_array, filters)
    prev_array = obs.obs_data_get_array(data, "_filter_list")
    obs.obs_data_set_array(data, "_filter_list", swing_array)
    obs.obs_data_array_release(prev_array)
    obs.obs_data_array_release(swing_array)
    on_filter_list_changed(props, None, data)


def get_filter_list_swing_items_json(data) -> list:
    swing_array = obs.obs_data_get_array(data, "_filter_list")
    array_size = obs.obs_data_array_count(swing_array)
    json_items: list = []
    for i in range(array_size):
        swing_item = obs.obs_data_array_item(swing_array, i)
        obj_json = obs.obs_data_get_json(swing_item)
        json_items.append(obj_json)
        obs.obs_data_release(swing_item)
    obs.obs_data_array_release(swing_array)
    return json_items


def get_filters(data) -> list:
    swing_array = obs.obs_data_get_array(data, "_filter_list")
    array_size = obs.obs_data_array_count(swing_array)
    filters: list[dict] = []
    for i in range(array_size):
        swing_item = obs.obs_data_array_item(swing_array, i)
        filters.append(swing_item_to_dict(swing_item))
        obs.obs_data_release(swing_item)
    obs.obs_data_array_release(swing_array)
    return filters


def set_websocket(data, obs_host: str) -> None:
    address, port = obs_host.split(":")
    obs.obs_data_set_int(data, "_port", int(port))
    obs.obs_data_set_string(data, "_address", address)


def save_config(settings, file_path: str) -> None:
    try:
        save_to_file(file_path, json.dumps(settings_as_dict(settings)))
        SCRIPT_CONTEXT.print_debug(f"Saved config to: {file_path}")
    except (FileNotFoundError, ValueError) as error:
        SCRIPT_CONTEXT.print_debug(f"Failed to save config file: {error}")


def load_config(file_path: str) -> tuple:
    config: dict = json.loads(load_from_file(file_path))
    return config.get("filterList", None), \
           config.get("obsPassword", None), \
           config.get("obsHost", None)


def save_state() -> None:
    try:
        parser = RawConfigParser()
        parser.add_section("STATE")
        parser["STATE"]['debug'] = 'enabled' if SCRIPT_CONTEXT.debug else 'disabled'
        mode: str = get_available_write_mode(STATE_FILE)
        with open(STATE_FILE, mode, encoding="UTF-8") as file:
            parser.write(file)
        SCRIPT_CONTEXT.print_debug(f"State saved to: {STATE_FILE}")
    except BaseException as error:
        SCRIPT_CONTEXT.print_debug(f"Error saving state: {error}")


def load_state() -> None:
    if not path.isfile(STATE_FILE):
        return
    parser = RawConfigParser()
    parser.read(STATE_FILE)
    SCRIPT_CONTEXT.debug = parser['STATE']['debug'] == 'enabled'


def save_to_file(file_path: str, data: str) -> None:
    mode: str = get_available_write_mode(file_path)
    with open(file_path, mode, encoding="UTF-8") as file:
        file.write(data)


def load_from_file(file_path: str) -> str:
    file_path = path.abspath(file_path)
    if not path.exists(file_path):
        raise FileNotFoundError(f"Unable to locate config file: {file_path}")
    if not path.isfile(file_path):
        raise IsADirectoryError(f"Path is not a file: {file_path}")
    data: str
    with open(file_path, encoding="UTF-8") as file:
        data = file.read()
    return data


def get_available_write_mode(file_path: str) -> str:
    file_path = path.abspath(file_path)
    if path.isfile(file_path):
        return "w"

    parent_dir = path.dirname(file_path)
    if path.isdir(parent_dir):
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
    for f in filters:
        try:
            item_as_json = create_list_item_json(
                filter_as_json(
                    f[FLT_FILTER_NAME],
                    f[FLT_SOURCE_NAME],
                    f.get(FLT_DISPLAY_NAME, None),
                    f.get(FLT_ON_COLOR, None)
                )
            )
            swing_item = obs.obs_data_create_from_json(item_as_json)
            obs.obs_data_array_push_back(swing_array, swing_item)
            obs.obs_data_release(swing_item)
        except Exception as e:
            SCRIPT_CONTEXT.print_error(
                f"Failed to parse filter: {e}\n{json.dumps(f)}")


def int_to_rgb_hex(num: int) -> str:
    # 0xAABBGGRR (The obs_data_get_int color format)
    hex_str = hex(num)

    r = hex_str[8:10]
    g = hex_str[6:8]
    b = hex_str[4:6]

    return "".join(('#', r, g, b))


def rgb_hex_to_int(rgb_hex: str) -> int:
    rgb_hex = rgb_hex.strip()
    if rgb_hex.startswith("#"):
        rgb_hex = rgb_hex[1:]
    if rgb_hex.startswith("0x"):
        rgb_hex = rgb_hex[2:]

    r = rgb_hex[0:2]
    g = rgb_hex[2:4]
    b = rgb_hex[4:6]

    # 0xAABBGGRR (The obs_data_get_int color format)
    abgr_hex : str = "".join(("0xFF", b, g, r))

    return int(abgr_hex, base=16)


def filter_as_json(
        filter_name: str,
        source_name: str,
        display_name: Optional[str] = None,
        on_color: Optional[str] = None
    ) -> str:

    item_json = "{" + f'\\\"{FLT_FILTER_NAME}\\\": \\\"{filter_name}\\\", ' + \
                      f'\\\"{FLT_SOURCE_NAME}\\\": \\\"{source_name}\\\"'
    if display_name and not display_name.isspace():
        item_json += f', \\\"{FLT_DISPLAY_NAME}\\\": \\\"{display_name}\\\"'
    if on_color and not on_color.isspace():
        item_json += f', \\\"{FLT_ON_COLOR}\\\": \\\"{on_color}\\\"'
    item_json += "}"
    return item_json



def create_list_item_json(value : str) -> str:
    return '{"value":"%s","selected":false,"hidden":false}' % value