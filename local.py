import re
from Logic.Logger import *
from Logic.Engine import Engine, Action, MAX_LEGAL_MOVE
from ProcessManagement.MessageHandler import *
from dummy import *
import sys

player_count = 2
N = 5

def play_game(c1: Controller, c2:Controller):
    players = [c1, c2]

    end = False
    engine = Engine()
    messageHandler = MessageHandler(engine)

    # INITIATION
    for playerIdx in range(player_count):

        player_response = players[playerIdx].communicate(messageHandler.GetInitiationMessage(playerIdx))
        if "init confirm" not in player_response:
            warning(
                f'Player {playerIdx + 1} failed to correctly respond to initiation message. Penalising player {playerIdx + 1} and ending the game.')
            result = engine.terminatePlayer(playerIdx)
            end = True
            break

    # LOOP
    while not end:
        print(f"turn {engine.stepCount}", file=sys.stderr)
        player_response = players[engine.turn].communicate(messageHandler.GetLoopMessage())
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
        players[playerIdx].communicate(messageHandler.GetTerminationMessage(result, end))
    print(f"won by player {result}", file=sys.stderr)


if __name__ == "__main__":
    c1 = Controller(1)
    c2 = Controller(2)

    for i in range(N):
        print(f"============round {i+1}============", file=sys.stderr)
        play_game(c1,c2)
