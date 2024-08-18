# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


class Action(ActionBase):
    available_actions = Gio.ListStore.new(Gtk.StringObject)
    dirty_action = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        action_id = settings["action_id"]
        action_type = settings["action_type"]

        if action_id is not None:
            try:
                self.plugin_base.backend.send_xivdeck("/action/{}/{}/execute".format(action_type, action_id))
                self.set_center_label(None)
            except Exception as e:
                self.set_center_label('Offline')

    def on_ready(self):
        self.update_button()

    def get_config_rows(self):
        def on_action_type_changed(action_type_combo, param):
            selected_item = action_type_combo.get_selected_item()
            if selected_item is not None:
                action_type_name = selected_item.get_string().replace("(Current) ", "")

                # Clear the second ComboRow
                self.available_actions.remove_all()

                all_available_actions = self.plugin_base.backend.get_actions()

                if action_type_name not in all_available_actions.keys():
                    action_type_name = list(all_available_actions.keys())[0]

                self.settings = self.get_settings()

                saved_action_name = settings.get('action_name')
                saved_action_type = settings.get('action_type')

                settings['action_type_helper'] = action_type_name
                self.set_settings(settings)

                if saved_action_name is not None and saved_action_type == action_type_name:
                    self.available_actions.append(Gtk.StringObject.new("(Current) {}".format(saved_action_name)))
                else:
                    self.available_actions.append(Gtk.StringObject.new("None"))

                for self.action in sorted(all_available_actions[action_type_name], key=lambda d: d['name']):
                    self.available_actions.append(Gtk.StringObject.new(self.action['name']))

        settings = self.get_settings()

        # Create the first ComboRow
        available_action_types = Gio.ListStore.new(Gtk.StringObject)
        saved_action_type = settings.get('action_type')
        if saved_action_type is not None:
            available_action_types.append(Gtk.StringObject.new("(Current) {}".format(saved_action_type)))

        all_action_types = None
        has_action_types = False
        all_actions = self.plugin_base.backend.get_actions(refresh=True)

        if all_actions is not None:
            all_action_types = sorted(all_actions.keys())

        action_type_default_row = 0
        if all_action_types is not None and len(all_action_types) > 0:
            row_counter = 1
            has_action_types = True

            for current_action_type in all_action_types:
                available_action_types.append(Gtk.StringObject.new(current_action_type))
                if current_action_type == settings.get('action_type'):
                    action_type_default_row = row_counter
                row_counter += 1
        else:
            current_action_type = settings.get('action_type')
            self.available_actions.remove_all()

            if current_action_type is not None:
                available_action_types.append(Gtk.StringObject.new("(Offline) {}".format(current_action_type)))
                current_action = settings.get('action_name')
                if current_action is not None:
                    self.available_actions.append(Gtk.StringObject.new("(Offline) {}".format(current_action)))
                else:
                    self.available_actions.append(Gtk.StringObject.new("Offline"))
            else:
                available_action_types.append(Gtk.StringObject.new("Offline"))
                self.available_actions.remove_all()
                self.available_actions.append(Gtk.StringObject.new("Offline"))

        action_type = Adw.ComboRow(title="Select Action Type", model=available_action_types)

        if has_action_types:
            action_type.connect("notify::selected-item", on_action_type_changed)

            action_type.set_selected(action_type_default_row)

            # Create the second ComboRow

            action = Adw.ComboRow(title="Select Action", model=self.available_actions)
            action.connect("notify::selected-item", self.on_action_value_changed)

            # Initialize the second ComboRow with default values
            on_action_type_changed(action_type, None)

            settings = self.get_settings()
            action_type_name = settings.get('action_type_helper')
            row_counter = 1
            for action_dict in sorted(self.plugin_base.backend.get_actions()[action_type_name], key=lambda d: d['name']):
                if action_dict['id'] == settings.get('action_id'):
                    action.set_selected(row_counter)
                row_counter += 1

        else:
            action = Adw.ComboRow(title="Select Action", model=self.available_actions)

        return action_type, action

    async def websocket_event(self, event, message):
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()

    def update_button(self):
        settings = self.get_settings()
        action_name = settings.get('action_name')
        action_type = settings.get('action_type')

        if action_name is not None:
            action_icon = settings.get('action_icon')
            image = self.plugin_base.backend.get_icon(action_icon)
        else:
            image = None

        self.set_media(media_path=image)
        self.set_top_label(action_type)
        self.set_bottom_label(action_name)

    def get_action(self, action_type, name):
        all_actions = self.plugin_base.backend.get_actions()

        for action in all_actions[action_type]:
            if action['name'] == name:
                return action
        return None

    def on_action_value_changed(self, action, status):
        if action.get_selected_item() is not None:
            action_name = action.get_selected_item().get_string()
            if action_name != "None" and not action_name.startswith('(Current) '):
                settings = self.get_settings()
                action_type = settings.get('action_type_helper')
                action_dict = self.get_action(action_type, action_name)
                if action_dict is not None:

                    action_id = action_dict['id']
                    action_icon = action_dict['iconId']

                    settings['action_type'] = action_type
                    settings['action_id'] = action_id
                    settings['action_icon'] = action_icon
                    settings['action_name'] = action_name
                    self.set_settings(settings)
                    self.update_button()
