import os

# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import actions
from .actions.Command import Command
from .actions.Hotbar import Hotbar
from .actions.FFClass import FFClass
from .actions.Action import Action
from .actions.Emote import Emote
from .actions.Gearset import Gearset
from .actions.Macro import Macro
from .actions.Volume.Mute import Mute
from .actions.Volume.Set import Set
from .actions.Volume.Change import Change
from .actions.Helper.IconID import IconID

from .internal.WebsocketEventListener import WebsocketEvent


class XIVDeckPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        ## Launch backend
        self.launch_backend(os.path.join(self.PATH, "backend", "backend.py"), os.path.join(self.PATH, "backend", ".venv"), open_in_terminal=False)

        ## Register actions
        self.command_action_holder = ActionHolder(
            plugin_base = self,
            action_base = Command,
            action_id = "com_swordmaiden_xivdeck::Command",
            action_name = "Execute Command",
        )
        self.add_action_holder(self.command_action_holder)

        self.hotbar_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Hotbar,
            action_id = "com_swordmaiden_xivdeck::Hotbar",
            action_name = "Press Hotbar Key",
        )
        self.add_action_holder(self.hotbar_action_holder)

        self.ff_class_action_holder = ActionHolder(
            plugin_base = self,
            action_base =FFClass,
            action_id = "com_swordmaiden_xivdeck::FFClass",
            action_name = "Switch to Class",
        )
        self.add_action_holder(self.ff_class_action_holder)

        self.action_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Action,
            action_id = "com_swordmaiden_xivdeck::Action",
            action_name = "Perform Action",
        )
        self.add_action_holder(self.action_action_holder)

        self.emote_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Emote,
            action_id = "com_swordmaiden_xivdeck::Emote",
            action_name = "Play Emote",
        )
        self.add_action_holder(self.emote_action_holder)

        self.gearset_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Gearset,
            action_id = "com_swordmaiden_xivdeck::Gearset",
            action_name = "Equid Gearset",
        )
        self.add_action_holder(self.gearset_action_holder)

        self.helper_iconid_action_holder = ActionHolder(
            plugin_base = self,
            action_base =IconID,
            action_id = "com_swordmaiden_xivdeck::HelperIconID",
            action_name = "Get IconID of hotbar slot",
        )
        self.add_action_holder(self.helper_iconid_action_holder)

        self.macro_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Macro,
            action_id = "com_swordmaiden_xivdeck::Macro",
            action_name = "Execute Macro",
        )
        self.add_action_holder(self.macro_action_holder)

        self.volume_mute_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Mute,
            action_id = "com_swordmaiden_xivdeck::VolumeMute",
            action_name = "Volume: Mute Audio",
        )
        self.add_action_holder(self.volume_mute_action_holder)

        self.volume_set_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Set,
            action_id = "com_swordmaiden_xivdeck::VolumeSet",
            action_name = "Volume: Set to fixed Value",
        )
        self.add_action_holder(self.volume_set_action_holder)

        self.volume_change_action_holder = ActionHolder(
            plugin_base = self,
            action_base =Change,
            action_id = "com_swordmaiden_xivdeck::VolumeChange",
            action_name = "Volume: Lower or raise",
        )
        self.add_action_holder(self.volume_change_action_holder)

        # Register Events
        self.websocket_event_holder = WebsocketEvent(
            plugin_base = self,
            event_id="com_swordmaiden_xivdeck::WebsocketEvent"
        )
        self.add_event_holder(self.websocket_event_holder)

        # Register plugin
        self.register(
            plugin_name="XIVDeck",
            github_repo="https://github.com/SilentSwordmaiden/StreamController-XIVDeck-Plugin",
            plugin_version="1.0.0",
            app_version="1.5.0-beta.6"
        )
