# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
import json

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from GtkHelper.GtkHelper import ScaleRow
from gi.repository import Gtk, Adw


class Set(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        channel = settings.get("channel")
        volume = settings.get("volume")
        was_successful = self.plugin_base.backend.set_volume(channel, volume)
        if was_successful is None:
            self.set_center_label('Offline')
        else:
            self.update_button()

    def on_ready(self):
        self.update_button()

    async def websocket_event(self, event, message):
        print("Set: Got event")
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()
            elif json.loads(message)['messageType'] == "volumeUpdate":
                print("Set: Got volumeUpdate")
                self.update_button()

    def update_button(self):
        channel_name = None
        vol_state = None
        image = None

        settings = self.get_settings()

        saved_volume = settings.get("volume")
        if saved_volume is None:
            saved_volume = ""
        else:
            saved_volume = "Set: {}%".format(saved_volume)

        if settings.get("channel") is not None:
            channel_name = settings.get("channel")
            image = self.plugin_base.backend.get_icon(66331)

            try:
                channel_dict = json.loads(self.plugin_base.backend.query_xivdeck("/volume/{}".format(channel_name)))
                if channel_dict['muted']:
                    vol_state = "Muted"
                    image = self.plugin_base.backend.get_icon(66328)
                else:
                    vol_state = "Cur: {}%".format(channel_dict['volume'])
                    image = self.plugin_base.backend.get_icon(66327)

            except Exception as e:
                vol_state = "N/A"

        self.set_media(media_path=image)
        self.set_top_label(channel_name)
        self.set_center_label(vol_state)
        self.set_bottom_label(saved_volume)

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

        channel = Adw.ComboRow(title='Select audio channel', model=available_channels)

        channel.set_selected(current_channel_row)

        channel.connect("notify::selected", self.on_channel_value_changed)

        current_volume = settings.get("volume")
        if current_volume is None:
            current_volume = 50

        volume = ScaleRow(
            title="Set volume",
            value=current_volume,
            min=-0,
            max=100,
            step=1,
            text_left="0",
            text_right="100"
        )

        volume.scale.set_draw_value(True)

        volume.scale.connect("value-changed", self.on_volume_value_changed)

        self.on_channel_value_changed(channel)
        self.on_volume_value_changed(volume.scale)

        return [channel, volume]

    def on_volume_value_changed(self, volume):
        settings = self.get_settings()
        settings["volume"] = int(volume.get_value())
        self.set_settings(settings)
        self.update_button()

    def on_channel_value_changed(self, channel, status=None):
        settings = self.get_settings()
        settings["channel"] = channel.get_selected_item().get_string()
        self.set_settings(settings)
        self.update_button()
