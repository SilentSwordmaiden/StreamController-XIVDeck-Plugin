# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
import json

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class Mute(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        channel = settings.get("channel")
        mute_status = self.plugin_base.backend.mute_volume(channel)
        if mute_status is None:
            self.set_center_label('Offline')
        else:
            self.set_center_label(None)

    def on_ready(self):
        self.update_button()

    async def websocket_event(self, event, message):
        print("Mute: Got event")
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()
            elif json.loads(message)['messageType'] == "volumeUpdate":
                print("Mute: Got volumeUpdate")
                self.update_button()

    def update_button(self):
        channel_name = None
        mute_state = None
        image = None

        settings = self.get_settings()
        if settings.get("channel") is not None:
            channel_name = settings.get("channel")
            try:
                channel_dict = json.loads(self.plugin_base.backend.query_xivdeck("/volume/{}".format(channel_name)))
                if channel_dict['muted']:
                    mute_state = "Muted"
                    image = self.plugin_base.backend.get_icon(66328)
                else:
                    mute_state = "Playing"
                    image = self.plugin_base.backend.get_icon(66327)

            except Exception as e:
                mute_state = "N/A"

        self.set_media(media_path=image)
        self.set_top_label(channel_name)
        self.set_bottom_label(mute_state)

    def get_config_rows(self) -> list:
        available_channels = Gtk.StringList()
        channels_list = ("Master", "BackgroundMusic", "SoundEffects", "Voice", "System", "Ambient", "Performance")
        try:
            channels_list = json.loads(self.plugin_base.backend.query_xivdeck("/volume"))
            self.set_center_label(None)
        except Exception as e:
            self.set_center_label('Offline')

        settings = self.get_settings()
        current_channel = settings.get("channel")

        i = 0
        current_channel_row = 0
        for channel_name in channels_list:
            available_channels.append(channel_name)
            if channel_name == current_channel:
                current_channel_row = i
            i += 1

        channel = Adw.ComboRow(title='Toggle Mute Channel', model=available_channels)

        channel.set_selected(current_channel_row)

        channel.connect("notify::selected", self.on_channel_value_changed)

        self.on_channel_value_changed(channel, True)

        return [channel]

    def on_channel_value_changed(self, channel, status):
        settings = self.get_settings()
        settings["channel"] = channel.get_selected_item().get_string()
        self.set_settings(settings)
        self.update_button()
