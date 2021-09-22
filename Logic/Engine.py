import json
import os
import errno
from copy import deepcopy
import secrets
from datetime import datetime
from enum import Enum
import queue

from .settings import *
from .Map import *
from .Player import *
from .Logger import *
from .Bomb import *


MAX_LEGAL_MOVE = 9


class Action(Enum):
    left = 0
    right = 1
    up = 2
    down = 3
    stay = 4
    place_bomb = 5
    place_trap_left = 6
    place_trap_right = 7
    place_trap_up = 8
    place_trap_down = 9
    init_action = 10
    no_action = 11
    no_action_timeout = 12


class Engine():
    def __init__(
        self,
        mapPath=MAP_PATH,

    ):
        info("="*80)
        info(f"Opening map from {mapPath}.")
        self.map = Map(mapPath)
        self.turn = TURN_INIT
        self.deadZonePolicyOffset = 0
        self.initPlayersPosition = [
            {'x': self.map.player1_initial_x, 'y': self.map.player1_initial_y},
            {'x': self.map.player2_initial_x, 'y': self.map.player2_initial_y}
        ]
        self.players = [
            Player(
                health=self.map.player_initial_health, bombRange=self.map.player_initial_bomb_range, trapCount=self.map.player_initial_trap_count,
                initX=self.initPlayersPosition[0]['x'], initY=self.initPlayersPosition[0]['y'], name=PLAYER_1_NAME, max_bomb_range=self.map.max_bomb_range),
            Player(
                health=self.map.player_initial_health, bombRange=self.map.player_initial_bomb_range, trapCount=self.map.player_initial_trap_count,
                initX=self.initPlayersPosition[1]['x'], initY=self.initPlayersPosition[1]['y'], name=PLAYER_2_NAME, max_bomb_range=self.map.max_bomb_range)]
        for player in self.players:
            self.map.addTileState(player.x, player.y, Tile_State.player)
        self.bombs = []
        self.stepCount = 0
        self.currentRoundDeadPlayers = []
        self.lastAction = [Action.init_action, Action.init_action]
        self.playerVision = self.map.player_vision
        self.initialMapData = deepcopy(self.map.mapData)
        self.gameLog = {'initial_game_data': {}, 'steps': []}

    def __str__(self) -> str:
        return str(self.map.mapData)

    def changeTurn(self):
        self.turn = 1 - self.turn

    def nextStep(self):
        self.stepCount += 1

    def clearDeadList(self):
        self.currentRoundDeadPlayers.clear()

    def isAccessibleForPlayer(self, x, y):
        if (
            x < 0 or x >= self.map.height or
            y < 0 or y >= self.map.width or
            self.map.hasTileState(x, y, Tile_State.wall) or
            self.map.hasTileState(x, y, Tile_State.box) or
            self.map.hasTileState(x, y, Tile_State.player)
        ):
            return False
        return True

    def isAccessibleForTrap(self, x, y):
        if (
            x < 0 or x >= self.map.height or
            y < 0 or y >= self.map.width or
            self.map.hasTileState(x, y, Tile_State.wall) or
            self.map.hasTileState(x, y, Tile_State.box)
        ):
            return False
        return True

    def isAccessible(self, x, y):
        if (
            x < 0 or x >= self.map.height or
            y < 0 or y >= self.map.width or
            self.map.hasTileState(x, y, Tile_State.wall)
        ):
            return False
        return True

    def collectUpgrades(self):
        x = self.players[self.turn].x
        y = self.players[self.turn].y

        if self.map.hasTileState(x, y, Tile_State.upgrade_health):
            self.players[self.turn].upgradeHealth()
            self.map.removeTileState(x, y, Tile_State.upgrade_health)

        if self.map.hasTileState(x, y, Tile_State.upgrade_range):
            self.players[self.turn].upgradeBombRange()
            self.map.removeTileState(x, y, Tile_State.upgrade_range)

        if self.map.hasTileState(x, y, Tile_State.upgrade_trap):
            self.players[self.turn].upgradeTrapCount()
            self.map.removeTileState(x, y, Tile_State.upgrade_trap)

    def doAction(self, action: Action):
        x = self.players[self.turn].x
        y = self.players[self.turn].y

        if action.value == Action.right.value:
            if not self.isAccessibleForPlayer(x, y+1):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! 'right' tile is not accessible ({x}, {y+1}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            self.map.removeTileState(x, y, Tile_State.player)
            self.map.addTileState(x, y+1, Tile_State.player)
            self.players[self.turn].y += 1
            self.collectUpgrades()
            self.lastAction[self.turn] = Action.right
            return None

        elif action.value == Action.down.value:
            if not self.isAccessibleForPlayer(x+1, y):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! 'down' tile is not accessible ({x+1}, {y}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            self.map.removeTileState(x, y, Tile_State.player)
            self.map.addTileState(x+1, y, Tile_State.player)
            self.players[self.turn].x += 1
            self.collectUpgrades()
            self.lastAction[self.turn] = Action.down
            return None

        elif action.value == Action.left.value:
            if not self.isAccessibleForPlayer(x, y-1):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! 'left' tile is not accessible ({x}, {y-1}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            self.map.removeTileState(x, y, Tile_State.player)
            self.map.addTileState(x, y-1, Tile_State.player)
            self.players[self.turn].y -= 1
            self.collectUpgrades()
            self.lastAction[self.turn] = Action.left
            return None

        elif action.value == Action.up.value:
            if not self.isAccessibleForPlayer(x-1, y):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! 'up' tile is not accessible ({x-1}, {y}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            self.map.removeTileState(x, y, Tile_State.player)
            self.map.addTileState(x-1, y, Tile_State.player)
            self.players[self.turn].x -= 1
            self.collectUpgrades()
            self.lastAction[self.turn] = Action.up
            return None

        elif action.value == Action.place_bomb.value:
            if self.map.hasTileState(x, y, Tile_State.bomb):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! There is already a bomb in this tile ({x}, {y}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            self.bombs.append(
                Bomb(x, y, self.stepCount, self.players[self.turn].getBombRange()))
            self.map.addTileState(x, y, Tile_State.bomb)
            self.players[self.turn].placeBomb()
            self.lastAction[self.turn] = Action.place_bomb

        elif action.value == Action.place_trap_left.value or action.value == Action.place_trap_right.value or action.value == Action.place_trap_up.value or action.value == Action.place_trap_down.value:
            trap_x = x
            trap_y = y
            if action.value == Action.place_trap_up.value:
                trap_x -= 1
            if action.value == Action.place_trap_down.value:
                trap_x += 1
            if action.value == Action.place_trap_right.value:
                trap_y += 1
            if action.value == Action.place_trap_left.value:
                trap_y -= 1

            if not self.isAccessibleForTrap(trap_x, trap_y):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! Tile is not accessible to place a trap ({trap_x}, {trap_y}).")
                self.lastAction[self.turn] = Action.no_action
                return -1

            if self.map.hasTileState(trap_x, trap_y, Tile_State.trap):
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! There is already a trap in this tile ({trap_x}, {trap_y}).")
                self.lastAction[self.turn] = Action.no_action
                return -1
            if self.players[self.turn].isTrapAvailable():
                self.map.addTileState(trap_x, trap_y, Tile_State.trap)
                self.players[self.turn].placeTrap()
                self.lastAction[self.turn] = action
            else:
                warning(
                    f"Player {self.turn + 1} action in step {self.stepCount} ignored! There are no traps left.")
                self.lastAction[self.turn] = Action.no_action

        elif action.value == Action.stay.value:
            self.lastAction[self.turn] = Action.stay

        elif action.value == Action.no_action.value:
            warning(
                f"Player {self.turn + 1} action in step {self.stepCount} is illegal! Action was replaced with 'no_action'.")
            self.lastAction[self.turn] = Action.no_action

    def clearEffects(self, states_to_clear):
        for i in range(self.map.height):
            for j in range(self.map.width):
                for state in states_to_clear:
                    self.map.removeTileState(i, j, state)

    def saveLogOfGame(self, end=False, winnerId=0):
        players_data = []

        for idx in range(len(self.players)):
            players_data.append({
                'id': idx + 1,
                'health': self.players[idx].getHealth(),
                "x_position": self.players[idx].x,
                "y_position": self.players[idx].y,
                "bomb_power_level": self.players[idx].getBombRange(),
                "traps_left": self.players[idx].getTrapCount(),
                "action_taken": self.lastAction[idx].value
            })

        self.gameLog['steps'].append({
            "step": self.stepCount,
            "players_data": deepcopy(players_data),
            "map_data": deepcopy(self.map.mapData),
            "bombs": [{'x': b.x, 'y': b.y, 'steps_passed': self.stepCount - b.startStep} for b in self.bombs]})

        if end:
            self.gameLog['initial_game_data'] = {
                "last_step": self.stepCount,
                "winner": self.players[winnerId-1].name,
                "winnerId": winnerId,
                "map_width": self.map.width,
                "map_height": self.map.height,
                "map_data": self.initialMapData,
                "is_vision_limited": True,
                "player_x_vision": self.playerVision,
                "player_y_vision": self.playerVision,
                "player_1_name": self.players[0].name,
                "player_2_name": self.players[1].name,
                "player_1_init_x": self.initPlayersPosition[0]['x'],
                "player_1_init_y": self.initPlayersPosition[0]['y'],
                "player_2_init_x": self.initPlayersPosition[1]['x'],
                "player_2_init_y": self.initPlayersPosition[1]['y'],
                "initial_health": 3,
                "bomb_delay": self.map.bomb_delay,
            }

            game_log_filename = GAME_LOG_STATIC_FILENAME
            if game_log_filename is None:
                game_log_filename = 'game_log' + str(datetime.now().microsecond) + '.json'

            p = os.path.join(GAME_LOG_DESTINATION, game_log_filename)

            try:
                if not os.path.exists(os.path.dirname(p)):
                    try:
                        os.makedirs(os.path.dirname(p))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                with open(p, 'w') as f:
                    f.write(json.dumps(self.gameLog))
                    info(f"Game log saved in: {p}")
            except Exception as e:
                warning("There was a problem saving the game log:\n" + str(e))
                raise

    def activateTraps(self):
        for i in range(len(self.players)):

            x = self.players[i].x
            y = self.players[i].y

            if self.map.hasTileState(x, y, Tile_State.trap):
                self.map.removeTileState(x, y, Tile_State.trap)
                if not i in self.currentRoundDeadPlayers:
                    self.players[i].damage()
                    self.currentRoundDeadPlayers.append(i)

    def bombEffect(self, x, y):
        self.map.addTileState(x, y, Tile_State.fire)

        if self.map.hasTileState(x, y, Tile_State.box):
            self.map.removeTileState(x, y, Tile_State.box)
            self.map.addTileState(x, y, Tile_State.box_broken)

    def bombsExplosion(self):
        bombQueue = queue.Queue()

        for i in range(len(self.bombs) - 1, -1, -1):
            if (self.stepCount - self.bombs[i].startStep) > self.map.bomb_delay:
                bombQueue.put(self.bombs.pop(i))

        while not bombQueue.empty():
            currentBomb = bombQueue.get()
            x = currentBomb.x
            y = currentBomb.y
            self.map.removeTileState(x, y, Tile_State.bomb)

            # ---------------------------------- Center ---------------------------------- #

            self.bombEffect(x, y)

            if self.map.hasTileState(x, y, Tile_State.player):
                for j in range(len(self.players)):
                    if j not in self.currentRoundDeadPlayers and self.players[j].x == x and self.players[j].y == y:
                        self.currentRoundDeadPlayers.append(j)
                        self.players[j].damage()

            if self.map.hasTileState(x, y, Tile_State.bomb):
                for j in range(len(self.bombs) - 1, -1, -1):
                    if self.bombs[j].x == x and self.bombs[j].y == y:
                        bombQueue.put(self.bombs.pop(j))

            # ------------------------------------ RIGHT ------------------------------------ #
            for i in range(1, currentBomb.bombRange+1):
                if not self.isAccessible(x, y+i):
                    break

                self.bombEffect(x, y+i)

                if self.map.hasTileState(x, y+i, Tile_State.box_broken):
                    break

                if self.map.hasTileState(x, y+i, Tile_State.player):
                    for j in range(len(self.players)):
                        if j not in self.currentRoundDeadPlayers and self.players[j].x == x and self.players[j].y == y+i:
                            self.currentRoundDeadPlayers.append(j)
                            self.players[j].damage()

                if self.map.hasTileState(x, y+i, Tile_State.bomb):
                    for j in range(len(self.bombs) - 1, -1, -1):
                        if self.bombs[j].x == x and self.bombs[j].y == y+i:
                            bombQueue.put(self.bombs.pop(j))

            # ----------------------------------- DOWN ---------------------------------- #
            for i in range(1, currentBomb.bombRange+1):
                if not self.isAccessible(x+i, y):
                    break

                self.bombEffect(x+i, y)

                if self.map.hasTileState(x+i, y, Tile_State.box_broken):
                    break

                if self.map.hasTileState(x+i, y, Tile_State.player):
                    for j in range(len(self.players)):
                        if not j in self.currentRoundDeadPlayers and self.players[j].x == x+i and self.players[j].y == y:
                            self.currentRoundDeadPlayers.append(j)
                            self.players[j].damage()

                if self.map.hasTileState(x+i, y, Tile_State.bomb):
                    for j in range(len(self.bombs) - 1, -1, -1):
                        if self.bombs[j].x == x+i and self.bombs[j].y == y:
                            bombQueue.put(self.bombs.pop(j))

            # ----------------------------------- LEFT ----------------------------------- #
            for i in range(1, currentBomb.bombRange+1):
                if not self.isAccessible(x, y-i):
                    break

                self.bombEffect(x, y-i)

                if self.map.hasTileState(x, y-i, Tile_State.box_broken):
                    break

                if self.map.hasTileState(x, y-i, Tile_State.player):
                    for j in range(len(self.players)):
                        if not j in self.currentRoundDeadPlayers and self.players[j].x == x and self.players[j].y == y-i:
                            self.currentRoundDeadPlayers.append(j)
                            self.players[j].damage()

                if self.map.hasTileState(x, y-i, Tile_State.bomb):
                    for j in range(len(self.bombs) - 1, -1, -1):
                        if self.bombs[j].x == x and self.bombs[j].y == y-i:
                            bombQueue.put(self.bombs.pop(j))

            # ----------------------------------- UP ----------------------------------- #
            for i in range(1, currentBomb.bombRange+1):
                if not self.isAccessible(x-i, y):
                    break

                self.bombEffect(x-i, y)

                if self.map.hasTileState(x-i, y, Tile_State.box_broken):
                    break

                if self.map.hasTileState(x-i, y, Tile_State.player):
                    for j in range(len(self.players)):
                        if not j in self.currentRoundDeadPlayers and self.players[j].x == x-i and self.players[j].y == y:
                            self.currentRoundDeadPlayers.append(j)
                            self.players[j].damage()

                if self.map.hasTileState(x-i, y, Tile_State.bomb):
                    for j in range(len(self.bombs) - 1, -1, -1):
                        if self.bombs[j].x == x-i and self.bombs[j].y == y:
                            bombQueue.put(self.bombs.pop(j))

    def deadZonePolicy(self):
        # -------------------------------- make border ------------------------------- #
        if self.stepCount >= self.map.deadzone_starting_step and (self.stepCount - self.map.deadzone_starting_step) % self.map.deadzone_expansion_delay == 0 and self.deadZonePolicyOffset <= min(
                (self.map.width+1)/2, (self.map.height+1)/2):

            for i in range(self.deadZonePolicyOffset, self.map.width - self.deadZonePolicyOffset):
                self.map.addTileState(
                    self.deadZonePolicyOffset, i, Tile_State.deadzone)
                self.map.addTileState(
                    self.map.height - 1 - self.deadZonePolicyOffset, i, Tile_State.deadzone)

            for i in range(self.deadZonePolicyOffset, self.map.height - self.deadZonePolicyOffset):
                self.map.addTileState(
                    i, self.deadZonePolicyOffset, Tile_State.deadzone)
                self.map.addTileState(
                    i, self.map.width - 1 - self.deadZonePolicyOffset, Tile_State.deadzone)

            self.deadZonePolicyOffset += 1

        # ----------------------- check for players in deadzone ---------------------- #
        for i in range(len(self.players)):
            x = self.players[i].x
            y = self.players[i].y

            if self.map.hasTileState(x, y, Tile_State.deadzone):
                if not i in self.currentRoundDeadPlayers:
                    self.currentRoundDeadPlayers.append(i)
                    self.players[i].damage()

    def selectWinner(self):
        # NOTE: Incompatible with more than 2 agents.
        deadPlayers = []

        for i in range(len(self.players)):
            if not self.players[i].isAlive():
                deadPlayers.append(i)

        # --------------- No winner yet -------------- #
        if len(deadPlayers) == 0 and self.stepCount < self.map.max_step:
            return -1

        # --------------- There is a winner. --------------- #
        info(f'Calculating the winner...')
        winner = None

        # --------------- 0. death -------------- #
        if len(deadPlayers) == 1:
            winner = 1 - deadPlayers[0] + 1
        if winner:
            info(f'Winner is player {winner}. Policy: Other player is dead.')
            return winner

        # --------------- 1. health comparison (more is better) -------------- #
        if self.players[0].getHealth() < self.players[1].getHealth():
            winner = 1
        if self.players[0].getHealth() > self.players[1].getHealth():
            winner = 2
        if winner:
            info(f'Winner is player {winner}. Policy: More health.')
            return winner

        # --------------- 2. health upgrade comparison (less is better) -------------- #
        if self.players[0].getHealthUpgradeCount() < self.players[1].getHealthUpgradeCount():
            winner = 1
        if self.players[0].getHealthUpgradeCount() > self.players[1].getHealthUpgradeCount():
            winner = 2
        if winner:
            info(f'Winner is player {winner}. Policy: Picked up less health upgrades.')
            return winner

        # ------------------ 3. bombs placed count (more is better) ----------------- #
        if self.players[0].getBombPlaceCount() > self.players[1].getBombPlaceCount():
            winner = 1
        if self.players[0].getBombPlaceCount() < self.players[1].getBombPlaceCount():
            winner = 2
        if winner:
            info(f'Winner is player {winner}. Policy: Placed more bombs.')
            return winner

        # -------------------- 4. bombs placed count (more is better) ------------------- #
        if self.players[0].getTrapPlaceCount() > self.players[1].getTrapPlaceCount():
            winner = 1
        if self.players[0].getTrapPlaceCount() < self.players[1].getTrapPlaceCount():
            winner = 2
        if winner:
            info(f'Winner is player {winner}. Policy: Placed more traps.')
            return winner

        # ------------------------------- 5. random ------------------------------ #
        winner = secrets.choice([1, 2])
        if winner:
            info(f'Winner is player {winner}. Policy: Random.')
            return winner

    def step(self, action: Action):
        self.clearEffects([Tile_State.fire])
        self.clearDeadList()

        self.doAction(action)

        self.collectUpgrades()

        self.bombsExplosion()
        self.clearEffects([Tile_State.box_broken])

        self.activateTraps()

        self.deadZonePolicy()

        winner = self.selectWinner()
        end = True if winner != -1 else False

        self.saveLogOfGame(end, winner)
        self.changeTurn()
        self.nextStep()
        return winner

    def terminatePlayer(self, player_id):
        winner = 1 - player_id + 1
        info(f'Winner is player {winner}. Policy: Other player was terminated.')
        self.saveLogOfGame(True, winner)
        return winner  # return winner id (1-based)
