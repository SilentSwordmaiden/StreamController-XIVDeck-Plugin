# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
import json
from time import sleep

# Import gtk
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


class Macro(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        macro_id = settings.get("macro_id")

        try:
            self.plugin_base.backend.send_xivdeck("/action/Macro/{}/execute".format(macro_id))
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
        settings = self.get_settings()
        macro_name = settings.get("macro_name")
        macro_icon = settings.get("macro_icon")

        print(macro_icon)
        image = self.plugin_base.backend.get_icon(macro_icon)
        self.set_media(media_path=image)

        self.set_top_label("Macro")
        self.set_bottom_label(macro_name)

    def get_config_rows(self) -> list:
        settings = self.get_settings()
        all_macros = self.plugin_base.backend.get_macros(True)
        available_macros = Gio.ListStore.new(Gtk.StringObject)
        row_counter = 0
        macro_default_row = 0
        for current_macro_dict in all_macros:
            current_macro_id = current_macro_dict['id']
            current_macro_name = current_macro_dict['name']
            if current_macro_name == "":
                current_macro_name = "<no name>"
            macro_row_string = "{}: {}".format(current_macro_id, current_macro_name)
            available_macros.append(Gtk.StringObject.new(macro_row_string))
            if str(current_macro_id) == settings.get('macro_id'):
                macro_default_row = row_counter
            row_counter += 1

        macro = Adw.ComboRow(title="Select available macro", model=available_macros)
        macro.connect("notify::selected-item", self.on_macro_value_changed)

        macro.set_selected(macro_default_row)

        return [macro]

    def on_macro_value_changed(self, macro, status):
        settings = self.get_settings()

        macro_id = macro.get_selected_item().get_string().split(":")[0]
        macro_name = None
        macro_icon = None

        all_available_macros = self.plugin_base.backend.get_macros()

        for current_macro in all_available_macros:
            if str(current_macro['id']) == macro_id:
                macro_name = current_macro['name']
                macro_icon = current_macro['iconId']

        settings["macro_id"] = macro_id
        settings["macro_name"] = macro_name
        settings["macro_icon"] = macro_icon

        self.set_settings(settings)
        self.update_button()
