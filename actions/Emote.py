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


class Emote(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        emote_id = settings["emote_id"]
        emote_log = settings["emote_log"]

        match emote_log:
            case 1:
                emote_log_string = "always"
            case 2:
                emote_log_string = "never"
            case _:
                emote_log_string = "default"

        logMode = {
            "logMode": emote_log_string
        }

        if emote_id is not None:
            try:
                self.plugin_base.backend.send_xivdeck("/action/Emote/{}/execute".format(emote_id),
                                                      message=json.dumps(logMode))
                self.set_center_label(None)
            except Exception as e:
                self.set_center_label('Offline')

    def on_ready(self):
        self.update_button()

    def get_config_rows(self) -> list:
        available_emotes = Gtk.StringList()

        settings = self.get_settings()
        current_emote = settings.get('emote_id')

        i = 0
        stored_emote_row = 0
        is_offline = False
        try:
            all_emotes_unsorted = json.loads(self.plugin_base.backend.query_xivdeck("/action/Emote"))

            all_emotes = sorted(all_emotes_unsorted, key=lambda d: d['name'])
            for emote_dict in all_emotes:
                emote_name = emote_dict['name']
                emote_id = emote_dict['id']
                available_emotes.append(emote_name)
                if emote_id == current_emote:
                    stored_emote_row = i
                i += 1
        except Exception as e:
            available_emotes.append("Offline")
            is_offline = True

        self.emote = Adw.ComboRow(title='Select Emote', model=available_emotes)

        if not is_offline:
            self.emote.connect("notify::selected", self.on_emote_value_changed)

        self.emote.set_selected(stored_emote_row)

        available_emotes_log_modes = Gtk.StringList()
        available_emotes_log_modes.append("default")
        available_emotes_log_modes.append("always")
        available_emotes_log_modes.append("never")

        self.emote_log = Adw.ComboRow(title='Should the emote be logged?', model=available_emotes_log_modes)

        self.emote_log.connect("notify::selected", self.on_emote_log_changed)

        if settings.get("emote_log") is not None:
            self.emote_log.set_selected(settings["emote_log"])

        return [self.emote, self.emote_log]

    async def websocket_event(self, event, message):
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()

    def update_button(self):
        image = None

        settings = self.get_settings()
        emote_id = settings["emote_id"]
        emote_name = None
        emote_title = None

        if emote_id is not None:
            emote_name = settings["emote_name"]
            emote_title = "Emote"
            image = self.plugin_base.backend.get_icon(settings["emote_icon_id"])

        self.set_media(media_path=image)
        self.set_top_label(emote_title)
        self.set_bottom_label(emote_name)

    def on_emote_log_changed(self, logmode, status):
        emote_log = logmode.get_selected()
        settings = self.get_settings()
        settings["emote_log"] = emote_log
        self.set_settings(settings)

    def on_emote_value_changed(self, emote, status):
        emote_name = emote.get_selected_item().get_string()
        if emote_name != "None":
            emote_dict = self.plugin_base.backend.get_emotes(emote_name)
            emote_id = emote_dict['id']
            emote_icon_id = emote_dict['iconId']
        else:
            emote_icon_id = None
            emote_id = None
        settings = self.get_settings()
        settings["emote_name"] = emote_name
        settings["emote_id"] = emote_id
        settings["emote_icon_id"] = emote_icon_id
        self.set_settings(settings)
        self.update_button()
