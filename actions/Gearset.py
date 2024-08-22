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


class Gearset(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        gearset_id = settings["gearset_id"]
        glam_id = settings["glam_id"]

        if gearset_id is not None:
            glam = None
            if glam_id is not None:
                glam = json.dumps({
                    "glamourPlateId": glam_id
                })

            try:
                self.plugin_base.backend.send_xivdeck("/action/GearSet/{}/execute".format(gearset_id),
                                                      message=glam)
                self.set_center_label(None)
            except Exception as e:
                self.set_center_label('Offline')

    def on_ready(self):
        self.update_button()

    def get_config_rows(self) -> list:
        available_gearsets = Gtk.StringList()

        settings = self.get_settings()
        current_gearset_name = settings.get('gearset')
        has_gearset = False
        all_gearsets = self.plugin_base.backend.get_gearsets()

        if all_gearsets is None:
            if current_gearset_name is not None:
                available_gearsets.append("(Offline) {}".format(current_gearset_name))
            else:
                available_gearsets.append("Offline")
        else:
            if current_gearset_name is not None:
                available_gearsets.append("(Current) {}".format(current_gearset_name))

            available_gearsets.append("Keep gearset equipped")
            for gearset_dict in all_gearsets:
                if not has_gearset:
                    has_gearset = True
                gearset_name = gearset_dict['name']
                available_gearsets.append(gearset_name)

        gearset = Adw.ComboRow(title='Select Gearset', model=available_gearsets)

        if has_gearset:
            gearset.connect("notify::selected", self.on_gearset_value_changed)
            self.on_gearset_value_changed(gearset)

        available_glams = Gtk.StringList()
        available_glams.append("None")
        for i in range(1, 21):
            available_glams.append("Glam {}".format(i))
        glam = Adw.ComboRow(title='Select Glam', model=available_glams)

        glam.connect("notify::selected", self.on_glam_value_changed)

        if settings.get("glam_id") is not None:
            glam.set_selected(settings["glam_id"])

        self.on_glam_value_changed(glam)

        return [gearset, glam]

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
        gearset_id = settings.get("gearset_id")
        gearset_name = None
        gearset_title = None

        if gearset_id is not None:
            if settings["gearset"] == "Keep gearset equipped":
                gearset_name = None
            else:
                gearset_name = settings["gearset"].split(":")[1].strip()
            glam_id = settings.get("glam_id")
            if glam_id is not None:
                gearset_title = "Glam #{}".format(glam_id)
            else:
                gearset_title = "Gearset"
            image = self.plugin_base.backend.get_icon(settings["gearset_icon_id"])

        self.set_media(media_path=image)
        self.set_top_label(gearset_title)
        self.set_bottom_label(gearset_name)

    def on_glam_value_changed(self, glam, status=None):
        glam_name = glam.get_selected()
        settings = self.get_settings()
        if glam_name > 0:
            settings["glam_id"] = glam_name
        else:
            settings["glam_id"] = None
        self.set_settings(settings)
        self.update_button()

    def on_gearset_value_changed(self, gearset, status=None):
        gearset_name = gearset.get_selected_item().get_string()
        if not gearset_name.startswith('(Current) '):
            if gearset_name != "None":
                if gearset_name == "Keep gearset equipped":
                    gearset_id = 0
                    gearset_icon_id = 125
                else:
                    gearset_dict = self.plugin_base.backend.get_gearsets(gearset_name)
                    gearset_id = gearset_dict['id']
                    gearset_icon_id = gearset_dict['iconId']
            else:
                gearset_icon_id = None
                gearset_id = None
            settings = self.get_settings()
            settings["gearset"] = gearset_name
            settings["gearset_id"] = gearset_id
            settings["gearset_icon_id"] = gearset_icon_id
            self.set_settings(settings)
            self.update_button()
