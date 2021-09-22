from Logic.Map import remove_state, Tile_State, has_state


class MessageHandler():
    def __init__(self, engine):
        self.engine = engine

    def GetInitiationMessage(self, playerIdx):
        return f"init {self.engine.map.height} {self.engine.map.width} {self.engine.players[playerIdx].x} {self.engine.players[playerIdx].y} {self.engine.players[playerIdx].getHealth()} {self.engine.players[playerIdx].getBombRange()} {self.engine.players[playerIdx].getTrapCount()} {self.engine.playerVision} {self.engine.map.bomb_delay} {self.engine.map.max_bomb_range} {self.engine.map.deadzone_starting_step} {self.engine.map.deadzone_expansion_delay} {self.engine.map.max_step}"

    def GetLoopMessage(self):
        message = ''

        # this plyaer's info
        message += f'{self.engine.stepCount} {self.engine.lastAction[self.engine.turn].value} {self.engine.players[self.engine.turn].x} {self.engine.players[self.engine.turn].y} '

        # upgrades
        message += f'{self.engine.players[self.engine.turn].getHealth()} '
        message += f'{self.engine.players[self.engine.turn].getHealthUpgradeCount()} '
        message += f'{self.engine.players[self.engine.turn].getBombRange()} '
        message += f'{self.engine.players[self.engine.turn].getTrapCount()} '

        # other player's info
        playerX = self.engine.players[self.engine.turn].x
        playerY = self.engine.players[self.engine.turn].y
        otherX = self.engine.players[1 - self.engine.turn].x
        otherY = self.engine.players[1 - self.engine.turn].y

        distance = abs(playerX - otherX) + abs(playerY - otherY)
        vision = self.engine.playerVision

        if (distance > vision):
            message += f'0 '
        else:
            message += f'1 {otherX} {otherY} {self.engine.players[1 - self.engine.turn].getHealth()} '

        # Tiles (in vision) info
        numberOfTileInfoTuples = 0
        tmp = ''
        for i in range(-vision, vision+1):
            for j in range(-vision, vision+1):
                x = playerX + i
                y = playerY + j
                if x < 0 or x >= self.engine.map.height or y < 0 or y >= self.engine.map.width or (abs(i) + abs(j)) > vision:
                    continue

                try:
                    tileState = self.engine.map.getTileState(x, y)
                    # Remove unobservable states
                    tileState = remove_state(tileState, Tile_State.trap)
                    if has_state(tileState, Tile_State.box):
                        tileState = remove_state(tileState, Tile_State.upgrade_trap)
                        tileState = remove_state(tileState, Tile_State.upgrade_health)
                        tileState = remove_state(tileState, Tile_State.upgrade_range)

                    tmp += f'{x} {y} {tileState} '
                    numberOfTileInfoTuples += 1
                except:
                    continue

        message += f'{numberOfTileInfoTuples} {tmp}'
        message += f'EOM'

        return message

    def GetTerminationMessage(self, result, playerTerminated):
        step = self.engine.stepCount
        if not playerTerminated:
            step -= 1
        return f"term {step} {result}"
