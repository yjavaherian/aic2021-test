import time
import argparse
import re

from Logic.Logger import *
from Logic.Engine import Engine, Action, MAX_LEGAL_MOVE
from Logic import settings
from ProcessManagement.ProcessManager import Process as PlayerProcess
from ProcessManagement.MessageHandler import *


timeout = settings.TIME_OUT  # sec
timeout_behaviour = settings.TIME_OUT_BEHAVIOUR
player_count = 2


def main(args):
    players: list(PlayerProcess) = []
    for playerIdx in range(player_count):
        players.append(PlayerProcess(
            args.p1 if playerIdx == 0 else args.p2, timeout, timeout_behaviour, agentLogFilename=f'{playerIdx+1}' if settings.AGENT_LOG and settings.AGENT_LOG_TO_FILE else None))

    # Avoiding race condition. Agent processes might throw an excpection even before game initiation.
    time.sleep(0.3)
    # Giving agents some time to finish setting up (and load a model if necessary).
    time.sleep(settings.AGENT_STARTUP_DELAY)

    end = False
    engine = Engine()
    messageHandler = MessageHandler(engine)

    # INITIATION
    for playerIdx in range(player_count):
        try:
            player_response = players[playerIdx].communicate(
                messageHandler.GetInitiationMessage(playerIdx))
        except Exception as e:
            warning(f'Player {playerIdx+1} failed to respond to initiation message. Penalising player and ending the game.')
            result = engine.terminatePlayer(playerIdx)
            end = True
            break

        if "init confirm" not in player_response:
            warning(
                f'Player {playerIdx+1} failed to correctly respond to initiation message. Penalising player {playerIdx+1} and ending the game.')
            result = engine.terminatePlayer(playerIdx)
            end = True
            break

    # LOOP
    while not end:
        player_response = None  # Resets player_response
        try:
            player_response = players[engine.turn].communicate(
                messageHandler.GetLoopMessage())
        except Exception as e:
            end = True
            warning(f'Terminating player {engine.turn + 1}. (E: {e})')
            result = engine.terminatePlayer(engine.turn)
            break

        pr = re.findall('\s*\d+\s*', player_response)
        if len(pr) != 1:
            end = True
            warning(f'Terminating player {engine.turn + 1}. (E: Bad response ({str(pr)}).)')
            result = engine.terminatePlayer(engine.turn)
            break
        action_taken = int(pr[0].split()[0])
        if action_taken < 0 or action_taken > MAX_LEGAL_MOVE:
            action_taken = Action.no_action.value
        result = engine.step(Action(action_taken))

        if result != -1:
            # There is a winner
            break

    # TERMINATION
    for playerIdx in range(player_count):
        try:
            players[playerIdx].communicate(
                messageHandler.GetTerminationMessage(result, end))
        except Exception as e:
            pass
        finally:
            players[playerIdx].end_process()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='args')

    parser.add_argument('-p1', default='none', type=str,
                        help='first player path')
    parser.add_argument('-p2', default='none', type=str,
                        help='second player path')

    args = parser.parse_args()

    main(args)
