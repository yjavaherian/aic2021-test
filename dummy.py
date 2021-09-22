import random
import sys

class Controller:
    def __init__(self, pid: int) -> None:
        self.pid = pid
       
    def communicate(self, inp: str) -> str:
        if 'term' in inp :
                return "\n"

        if 'init' in inp:
            # do stuff ...
            return 'init confirm'
        else:
            # do stuff ...
            action = int(random.random() * 10)
            print(f"player#{self.pid} action: {action}", file=sys.stderr)
            return f'{action}'


if __name__ == "__main__":
    controller = Controller(-1)
    print(controller.communicate(input()), flush=True)

    while True:
        state_msg = input()
        if 'term' in state_msg:
            break
        print(controller.communicate(state_msg), flush=True)