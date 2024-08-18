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

class Hotbar(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        hotbar_id = self.get_value('hotbar') - 1
        slot_id = self.get_value('slot') - 1

        try:
            self.plugin_base.backend.send_xivdeck("/hotbar/{}/{}/execute".format(hotbar_id, slot_id))
            self.set_center_label(None)
        except Exception as e:
            self.set_center_label('Offline')

    def on_ready(self):
        self.update_button()

    def get_config_rows(self) -> list:
        hotbars = Gtk.StringList()
        hotbars.append("None")
        for i in range(1, 11):
            hotbars.append("Hotbar {}".format(i))
        hotbar = Adw.ComboRow(title='Select Hotbar', model=hotbars)

        slots = Gtk.StringList()
        slots.append("None")
        for i in range(1, 13):
            slots.append("Slot {}".format(i))
        slot = Adw.ComboRow(title='Select Slot', model=slots)

        settings = self.get_settings()
        if settings.get('hotbar') is not None:
            hotbar.set_selected(settings.get('hotbar'))
        if settings.get('slot') is not None:
            slot.set_selected(settings.get('slot'))

        hotbar.connect("notify::selected", self.on_hotbar_value_changed)
        slot.connect("notify::selected", self.on_slot_value_changed)

        return [hotbar, slot]

    def get_value(self, entry):
        settings = self.get_settings()
        return settings.get(entry)

    async def websocket_event(self, event, message):
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()
            elif json.loads(message)['type'] == "Hotbar":
                self.update_button()

    def update_button(self):
        image = None
        hotbar_string = None
        slot_string = None

        hotbar_id = self.get_value('hotbar')
        slot_id = self.get_value('slot')

        if hotbar_id is not None and slot_id is not None:
            if hotbar_id >= 1 and slot_id >= 1:
                try:
                    query_json = self.plugin_base.backend.query_xivdeck("/hotbar/{}/{}".format(hotbar_id-1, slot_id-1))
                    hotbar_item = json.loads(query_json)
                    image = self.plugin_base.backend.get_icon(hotbar_item['iconId'])
                    self.set_center_label(None)
                except Exception:
                    self.set_center_label('Offline')
                    image = self.get_value('skill_icon')

                hotbar_string = "Hotbar: {}".format(hotbar_id)
                slot_string = "Slot: {}".format(slot_id)

        self.set_media(media_path=image)
        self.set_top_label(hotbar_string)
        self.set_bottom_label(slot_string)

    def on_hotbar_value_changed(self, hotbar, status):
        settings = self.get_settings()
        settings["hotbar"] = hotbar.get_selected()
        settings = self.add_icon_id(settings)
        self.set_settings(settings)
        self.update_button()

    def on_slot_value_changed(self, slot, status):
        settings = self.get_settings()
        settings["slot"] = slot.get_selected()
        settings = self.add_icon_id(settings)
        self.set_settings(settings)
        self.update_button()

    def add_icon_id(self, settings):
        hotbar_id = settings.get('hotbar')
        slot_id = settings.get('slot')
        try:
            query_json = self.plugin_base.backend.query_xivdeck("/hotbar/{}/{}".format(hotbar_id - 1, slot_id - 1))
            hotbar_item = json.loads(query_json)
            settings["skill_icon"] = hotbar_item['iconId']
            print("Set icon")
        except Exception as e:
            print("Don't set icon: {}".format(e))
            pass

        return settings
