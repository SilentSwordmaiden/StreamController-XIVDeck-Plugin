import threading
from websocket import create_connection
from time import sleep
from src.backend.PluginManager.EventHolder import EventHolder
import psutil


class WebsocketEvent(EventHolder):
    def __init__(self, plugin_base, event_id: str):
        super().__init__(plugin_base=plugin_base, event_id=event_id)
        self.websocket_url = None
        while self.websocket_url is None:
            try:
                self.websocket_url = self.plugin_base.backend.ws_uri
            except Exception as e:
                self.websocket_url = None

        self.websocket_port = None
        while self.websocket_port is None:
            try:
                self.websocket_port = int(self.plugin_base.backend.port)
            except Exception as e:
                self.websocket_port = None

        self.websocket_thread = threading.Thread(target=self._start_loop)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

    def _start_loop(self):
        self._loop()

    def _loop(self):
        count_tries = 0
        while True:
            ffxiv_running = False
            for connection in psutil.net_connections(kind='inet'):
                laddr = connection[3]
                status = connection[5]
                if laddr is not None:
                    if len(laddr) > 0:
                        port = laddr[1]
                        if port == self.websocket_port and status == "LISTEN":
                            ffxiv_running = True

            if ffxiv_running:
                try:
                    websocket = create_connection(self.websocket_url)
                    self.plugin_base.backend.get_headers()
                    self.trigger_event("connect")
                    try:
                        while True:
                            websocket_event = websocket.recv()
                            self.trigger_event(websocket_event)
                    except Exception:
                        continue
                except Exception:
                    if self.plugin_base.backend.headers is not None:
                        self.plugin_base.backend.forget_headers()
                    self.trigger_event("disconnect")
            elif count_tries < 10:
                # only trigger a disconnect event the first 10 tries to tell the buttons on startup
                count_tries += 1
                self.trigger_event("disconnect")

            sleep(1)
