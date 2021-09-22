import json

from enum import Enum


class Tile_State(Enum):
    deadzone = 0
    fire = 1
    box = 2
    wall = 3
    bomb = 4
    upgrade_range = 5
    upgrade_health = 6
    upgrade_trap = 7
    player = 8
    trap = 9
    box_broken = 10


def has_state(_state_mask, _state_to_check):
    return _state_mask & int(pow(2, _state_to_check.value))


def add_state(_state_mask, _state_to_add):
    return _state_mask | int(pow(2, _state_to_add.value))


def remove_state(_state_mask, _state_to_remove):
    return _state_mask & ~(int(pow(2, _state_to_remove.value)))


class Map():
    def __init__(self, filename: str):
        try:
            jsonFile = open(filename)
        except IOError:
            raise ValueError("Could not open file")
        else:
            jsonData = json.load(jsonFile)
            self.width = jsonData['width']
            self.height = jsonData['height']
            self.player1_initial_x = jsonData['player1_initial_x']
            self.player1_initial_y = jsonData['player1_initial_y']
            self.player2_initial_x = jsonData['player2_initial_x']
            self.player2_initial_y = jsonData['player2_initial_y']
            self.player_vision = jsonData['player_vision']
            self.player_initial_health = jsonData['player_initial_health']
            self.player_initial_bomb_range = jsonData['player_initial_bomb_range']
            self.player_initial_trap_count = jsonData['player_initial_trap_count']
            self.bomb_delay = jsonData['bomb_delay']
            self.max_bomb_range = jsonData['max_bomb_range']
            self.deadzone_starting_step = jsonData['deadzone_starting_step']
            self.deadzone_expansion_delay = jsonData['deadzone_expansion_delay']
            self.max_step = jsonData['max_step']
            self.mapData = jsonData['map']  # mapData[rowNumber][columnNumber]
            jsonFile.close()

    def setTileState(self, rowNumber, columnNumber, state):
        try:
            self.mapData[rowNumber][columnNumber] = state
        except IndexError:
            raise IndexError("Tile not found")

    def getTileState(self, rowNumber, columnNumber):
        try:
            return self.mapData[rowNumber][columnNumber]
        except IndexError:
            raise IndexError("Tile not found")

    def hasTileState(self, rowNumber, columnNumber, state):
        try:
            return has_state(self.mapData[rowNumber][columnNumber], state)
        except IndexError:
            raise IndexError("Tile not found")

    def addTileState(self, rowNumber, columnNumber, state):
        try:
            self.mapData[rowNumber][columnNumber] = add_state(
                self.mapData[rowNumber][columnNumber], state)
        except IndexError:
            raise IndexError("Tile not found")

    def removeTileState(self, rowNumber, columnNumber, state):
        try:
            self.mapData[rowNumber][columnNumber] = remove_state(
                self.mapData[rowNumber][columnNumber], state)
        except IndexError:
            raise IndexError("Tile not found")
