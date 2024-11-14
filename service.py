import logging
import socket
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from paho.mqtt.client import Client
from thefuzz import fuzz
from tuke_openlab import Controller, environment

import config
from gpt_utils import make_raquest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OlaServis:
    def __init__(
        self,
        host,
        port,
        ola_env: environment.Environment,
        controller_env: environment.Environment,
    ) -> None:
        self.host = host
        self.port = port
        self._client_id = "OlaServis"
        self._device_ip = self._get_ip()
        self._http_port = 8000
        self._http_host = str(self._device_ip)
        self._http_thread = self._create_server()
        self._http_thread.start()

        self.client = Client(client_id=self._client_id)

        self.ola_controller = Controller(ola_env)
        self.controller = Controller(controller_env)

        self.cmd_to_func_map = {
            # audio visualizer
            "start_audio_visualizer": (self.start_visualizer, ["Metamorphosis.mp3"]),
            "stop_audio_visualizer": self.stop_visualizer,
            # lights
            "turn_lights": self.turn_lights,
            "turn_off_lights": self.turn_off_lights,
            # display 2x2
            "turn_on_display_2x2": self.turn_on_display_2x2,
            "turn_off_display_2x2": self.turn_off_display_2x2,
            # vertical displays
            "turn_on_display_vertical": self.turn_on_vertical_displays,
            "turn_off_display_vertical": self.turn_off_vertical_displays,
            # labb
            "turn_off_labb": self.turn_off_labb,
            "turn_on_labb": self.turn_on_labb,
        }

        self.client.connect(self.host, self.port)
        self.client.subscribe(config.AUDIO_VISUALIZER_TOPIC)
        self.ola_controller.voice_recognition.on_recognized(self.recognize)

    def _get_ip(self) -> str:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        return ip

    def run(self) -> None:
        self.ola_controller.loop_forever()

    def excec_cmd(self, cmd: str) -> None:
        if isinstance(self.cmd_to_func_map[cmd], tuple):
            self.cmd_to_func_map[cmd][0](*self.cmd_to_func_map[cmd][1])
            return

        self.cmd_to_func_map[cmd]()

    def recognize_cmd(self, message: str) -> str:
        cmd = ""
        percent = 0

        for cmd_key, aliases in config.OLA_COMMANDS.items():
            for alias in aliases:
                ratio = fuzz.ratio(message, alias)
                logger.info(f"command ratio: {ratio}")
                if ratio > percent:
                    percent = ratio
                    cmd = cmd_key

        if percent < 40:
            return ""

        return cmd

    def sound(self):
        self.client.publish(config.SOUND_TOPIC, str({"say": "testovanie"}))

    def is_ola_called(self, message: str) -> bool:
        for alias in config.OLA_ALIASES:
            ratio = fuzz.partial_ratio(" ".join(message.split(" ")[:2]), alias)
            if ratio > 50:
                return True

        return False

    def recognize(self, message: str) -> None:
        if self.is_ola_called(message):
            cmd = self.recognize_cmd(message)
            print(cmd)

            if cmd == "":
                text = self.gpt_request(message)
                logger.info(text)
                self.tts(text)
                return

            logger.info(f"recognized command: {cmd}")
            self.excec_cmd(cmd)

    def tts(self, text: str) -> None:
        self.client.publish(
            config.SOUND_TOPIC,
            str(
                {
                    "say": text,
                }
            ),
        )

    def gpt_request(self, text: str) -> str:
        return make_raquest(text)

    def turn_off_sound(self) -> None:
        self.client.publish(
            "openlab/process-manager/3x3",
            str({"process": "audioplayer", "action": "stop"}),
        )

    def turn_on_sound(self) -> None:
        self.client.publish(
            "openlab/process-manager/3x3",
            str({"process": "audioplayer", "action": "start"}),
        )

    def start_visualizer(self, song: str = "2.mp3") -> None:
        data = {"play": f"http://{self._device_ip}:{self._http_port}/{song}"}
        self.client.publish(
            config.AUDIO_VISUALIZER_TOPIC,
            json.dumps(data),
        )

    def stop_visualizer(self) -> None:
        self.client.publish(
            config.AUDIO_VISUALIZER_TOPIC,
            json.dumps({"play": "stop"}),
        )

    def _create_server(self):
        server = HTTPServer(
            (self._http_host, self._http_port), SimpleHTTPRequestHandler
        )
        return Thread(target=server.serve_forever)

    def _serve_http(self):
        self._http_thread.start()

    def turn_lights(self) -> None:
        self.tts("Zapinam svetla")
        self.controller.lights.turn_on()

    def turn_off_lights(self) -> None:
        self.tts("Vypinam svetla")
        self.controller.lights.turn_off()

    def turn_on_display_2x2(self) -> None:
        self.tts("Zapinam displej 2x2")
        self.client.publish(config.DISPLAY_2X2_TOPIC, str({"power": "on"}))
        self.controller.screens.panel_2x2.set_default()

    def turn_off_display_2x2(self) -> None:
        self.tts("Vypinam displej")
        self.client.publish(config.DISPLAY_2X2_TOPIC, str({"power": "off"}))

    def turn_on_vertical_displays(self) -> None:
        self.tts("Zapinam vertikalne displeje")
        self.client.publish(config.DISPLAY_VERTICAL_TOPIC, str({"power": "on"}))
        for _, disp in self.controller.vertical_displays.items():
            disp.set_default()

    def turn_off_vertical_displays(self) -> None:
        self.tts("Vypinam vertikalne displeje")
        self.client.publish(config.DISPLAY_VERTICAL_TOPIC, str({"power": "off"}))

    def turn_on_labb(self) -> None:
        self.tts("Zapinam laboratorium")
        self.turn_on_sound()
        self.turn_on_vertical_displays()
        self.turn_on_display_2x2()
        self.turn_on_lights()

    def turn_off_labb(self) -> None:
        self.tts("Vypinam laboratorium")
        self.turn_off_display_2x2()
        self.turn_off_vertical_displays()
        self.turn_off_sound()
        self.turn_off_lights()
