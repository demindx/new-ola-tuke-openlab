import environ

env = environ.Env()
environ.Env.read_env(".env")


GPT_KEY = env("GPT_KEY")

HOST = "openlab.kpi.fei.tuke.sk"
PORT = 1883

DISPLAY_2X2_TOPIC = "openlab/display/2x2/command"
DISPLAY_VERTICAL_TOPIC = "openlab/display/vertical/command"
SOUND_TOPIC = "openlab/audio"
AUDIO_VISUALIZER_TOPIC = "openlab/audio-visualizer"

OLA_ALIASES = ("Hej ola", "hej ola", "ola", "Ola")

OLA_COMMANDS = {
    "turn_lights": ("zapni svetla", "svetla", "zapni svetlo"),
    "turn_off_lights": ("vypni svetla", "vypni svetlo"),
    "turn_on_display_2x2": ("zapni displej",),
    "turn_off_display_2x2": ("vypni displej",),
    "turn_on_display_vertical": ("zapni vertikalne displeje",),
    "turn_off_display_vertical": ("vypni vertikalne displeje",),
    "start_audio_visualizer": (
        "spusti visualizator",
        "visualizator",
    ),
    "stop_audio_visualizer": (
        "vypni visualizator",
        "vypni visualizaciu",
    ),
    "turn_off_labb": ("Vypni laboratorium", "Vypni všetko"),
    "turn_on_labb": ("Zapni laboratorium", "Zapni všetko"),
}
