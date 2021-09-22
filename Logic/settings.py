""" default setting configurations

each constant is set to its equivalent in environment variables or hardcoded default below

"""

import os
import sys


# --------------- Map -------------- #

MAP_PATH = os.environ.get("MAP_PATH", None) or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "maps", "map9.json")


# --------------- Logging -------------- #

GAME_LOG_DESTINATION = os.environ.get("GAME_LOG_DESTINATION", None) or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../gameLog')
GAME_LOG_STATIC_FILENAME = os.environ.get("GAME_LOG_STATIC_FILENAME", None)

ENGINE_LOG_LOGGER_LEVEL = os.environ.get("ENGINE_LOG_LOGGER_LEVEL", None) or 10
ENGINE_LOG_TO_STDERR = os.environ.get("ENGINE_LOG_TO_STDERR", None) or True
ENGINE_LOG_TO_FILE = os.environ.get("ENGINE_LOG_TO_FILE", None) or True
ENGINE_LOG_DESTINATION = os.environ.get("ENGINE_LOG_DESTINATION", None) or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../')
ENGINE_LOG_FILENAME = os.environ.get("ENGINE_LOG_FILENAME", None) or 'output.log'

AGENT_LOG = os.environ.get("AGENT_LOG", None) or True
AGENT_LOG_TO_FILE = os.environ.get("AGENT_LOG_TO_FILE", None) or True
AGENT_LOG_DESTINATION = os.environ.get("AGENT_LOG_DESTINATION", None) or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../agentLog')


# --------------- Players -------------- #

PLAYER_1_NAME = os.environ.get("PLAYER_1_NAME", None) or 'First player'
PLAYER_2_NAME = os.environ.get("PLAYER_2_NAME", None) or 'Second player'


# --------------- Turn -------------- #

TURN_INIT = int(os.environ.get("TURN_INIT", None) or 0)


# --------------- Timeout -------------- #

TIME_OUT = float(os.environ.get("TIME_OUT", None) or 0.4)
TIME_OUT_BEHAVIOUR = os.environ.get("TIME_OUT_BEHAVIOUR", None) or 'kill'


# --------------- Python -------------- #

exe = None
if 'win' in sys.platform.lower():
    exe = 'py'
elif 'linux' in sys.platform.lower():
    exe = 'python3'
PYTHON_EXECUTABLE = os.environ.get("PYTHON_EXECUTABLE", None) or exe or sys.executable


# --------------- Agent startup delay -------------- #

AGENT_STARTUP_DELAY = float(os.environ.get("AGENT_STARTUP_DELAY", None) or 0)
