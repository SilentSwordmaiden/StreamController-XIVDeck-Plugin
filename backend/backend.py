import asyncio
import websockets
import json
import requests
import io
import os
from PIL import Image
from streamcontroller_plugin_tools import BackendBase


class Backend(BackendBase):
    host = "127.0.0.1"
    port = "37984"
    ws_uri = "ws://{host}:{port}/ws".format(host=host, port=port)
    http_uri = "http://{host}:{port}".format(host=host, port=port)

    headers = None
    ff_classes_dict = None
    emotes_dict = None
    gearsets_dict = None
    all_actions = None
    all_macros = None

    async def init_xivdeck(self, ws_uri):
        message = {
            "opcode": "init",
            "version": "1.0.0",
            "mode": "Developer"
        }

        async with websockets.connect(ws_uri) as websocket:
            await websocket.send(json.dumps(message))

            response = json.loads(await websocket.recv())
            apiKey = response['apiKey']

            return {
                "Authorization": "Bearer {}".format(apiKey)
            }

    async def update_volume(self, message):
        async with websockets.connect(self.ws_uri) as websocket:
            await websocket.send(json.dumps(message))

    def mute_volume(self, channel="Master"):
        try:
            channel_dict = json.loads(self.query_xivdeck("/volume/{}".format(channel)))
            if channel_dict['muted']:
                new_mode = False
            else:
                new_mode = True

            message = {
                    "opcode": "setVolume",
                    "channel": channel,
                    "data": {
                        "muted": new_mode
                    }
                }
            asyncio.run(self.update_volume(message))
            return new_mode
        except Exception as e:
            print("Can't toggle mute for {}. Reason: {}".format(channel, e))
            return None

    def change_volume(self, channel="Master", delta=0):
        try:
            message = {
                "opcode": "setVolume",
                "channel": channel,
                "data": {
                    "delta": delta
                }
            }
            asyncio.run(self.update_volume(message))
            return True
        except Exception as e:
            print("Can't change volume by {} for {}. Reason: {}".format(delta, channel, e))
            return False

    def set_volume(self, channel="Master", volume=50):
        try:
            message = {
                    "opcode": "setVolume",
                    "channel": channel,
                    "data": {
                        "volume": volume
                    }
                }
            asyncio.run(self.update_volume(message))
            return True
        except Exception as e:
            print("Can't set volume for {}. Reason: {}".format(channel, e))
            return False

    def query_xivdeck(self, query, message=None, blob=False):
        try:
            headers = self.get_headers()
        except Exception as e:
            raise e

        try:
            if headers is not None:
                response = requests.get("{}{}".format(self.http_uri, query), json=message, headers=headers)
                if blob:
                    return response.content
                else:
                    return response.text
        except Exception as e:
            self.headers = None
            raise Exception("query_xivdeck error: {}".format(e))

    def send_xivdeck(self, query, message=None):
        if message is not None:
            message = json.loads(message)
        try:
            headers = self.get_headers()
        except Exception as e:
            raise e

        try:
            if headers is not None:
                response = requests.post("{}{}".format(self.http_uri, query), json=message, headers=headers)
                return response.text
        except Exception as e:
            self.headers = None
            raise Exception("send_xivdeck error: {}".format(e))

    def __init__(self):
        super().__init__()

    def get_icon(self, iconid, hq=False):
        if hq:
            hq_suffix = "_hq"
        else:
            hq_suffix = ""

        image_path = "/tmp/icon_{}{}.png".format(iconid, hq_suffix)

        if not os.path.isfile(image_path):
            query = "/icon/{}".format(iconid)
            try:
                icon_binary_data = self.query_xivdeck(query, blob=True)

                image_stream = io.BytesIO(icon_binary_data)
                image = Image.open(image_stream)

                image.save(image_path)
            except Exception as e:
                image_path = None

        return image_path

    def get_classes(self, name=None):
        try:
            all_classes = json.loads(self.query_xivdeck("/classes/available"))
            self.ff_classes_dict = sorted(all_classes, key=lambda d: d['name'])
        except Exception:
            pass

        if name is None:
            return self.ff_classes_dict
        else:
            for ff_class in self.ff_classes_dict:
                if ff_class['name'] == name:
                    return ff_class
            return []

    def get_emotes(self, name=None, refresh=False):
        if self.emotes_dict is None or refresh:
            available_emotes = []
            try:
                available_emotes = json.loads(self.query_xivdeck("/action/Emote"))
                self.emotes_dict = sorted(available_emotes, key=lambda d: d['name'])
            except Exception:
                pass

        if name is None:
            return self.emotes_dict
        else:
            for emote in self.emotes_dict:
                if emote['name'] == name:
                    return emote
            return []

    def get_gearsets(self, name=None):
        try:
            all_gearsets = json.loads(self.query_xivdeck("/action/GearSet"))
            self.gearsets_dict = sorted(all_gearsets, key=lambda d: d['name'])
        except Exception:
            pass

        if name is None:
            return self.gearsets_dict
        else:
            for gearset in self.gearsets_dict:
                if gearset['name'] == name:
                    return gearset
            return []

    def get_actions(self, refresh=False):
        if self.all_actions is None or refresh:
            try:
                available_actions = json.loads(self.query_xivdeck("/action"))
                self.all_actions = available_actions
            except Exception:
                pass
        return self.all_actions

    def get_macros(self, refresh=False):
        if self.all_macros is None or refresh:
            available_macros = []
            try:
                all_macros = json.loads(self.query_xivdeck("/action/Macro"))
                for current_macro in all_macros:
                    if current_macro['iconId'] != 0:
                        available_macros.append(current_macro)

                self.all_macros = available_macros
            except Exception:
                pass

        return self.all_macros

    def get_headers(self):
        if self.headers is None:
            try:
                self.headers = asyncio.run(self.init_xivdeck(self.ws_uri))
                print("Requested XIVDeck auth header: {}".format(self.headers))
            except Exception as e:
                raise Exception("Can't request XIVDeck auth header from {}: {}".format(self.ws_uri, e))

        return self.headers

    def forget_headers(self):
        self.headers = None
        print("Disconnected from XIVDeck and deleted auth header")

backend = Backend()
