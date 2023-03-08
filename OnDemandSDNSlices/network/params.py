from os.path import join, dirname, realpath
import os

SCENARIOS_PATH = os.path.normpath(dirname(realpath(__file__)) + os.sep + os.pardir)
SCENARIOS_PATH = join(SCENARIOS_PATH,"scenarios")

CONTROLLER_NAME = "c1"
CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = 6633
CONTROLLER_PATH = join(dirname(realpath(__file__)),'controller.py')

BRIDGE_HOST = "localhost"
BRIDGE_PORT = 2223
