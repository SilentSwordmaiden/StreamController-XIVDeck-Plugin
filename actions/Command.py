# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
import json

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class Command(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        command = settings.get("command")
        message = {
            "command": command
        }
        message = json.dumps(message)
        try:
            self.plugin_base.backend.send_xivdeck('/command', message)
            self.set_center_label(None)
        except Exception as e:
            self.set_center_label('Offline')

    def on_ready(self):
        self.update_button()

    async def websocket_event(self, event, message):
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()

    def update_button(self):
        image = self.plugin_base.backend.get_icon(32)
        self.set_media(media_path=image)
        self.set_top_label("Command")
        settings = self.get_settings()
        self.set_bottom_label(settings.get("command"))

    def get_config_rows(self) -> list:
        self.entry = Adw.EntryRow()
        self.entry.set_title('Command to execute starting with /')

        self.load_config_values()
        
        self.entry.connect("changed", self.on_entry_value_changed)

        return [self.entry]

    def load_config_values(self):
        settings = self.get_settings()
        self.entry.set_text(settings.get("command", ''))

    def on_entry_value_changed(self, entry):
        settings = self.get_settings()
        settings["command"] = entry.get_text()
        self.update_button()
