from subprocess import Popen, PIPE, DEVNULL
from threading import Timer, Lock, Thread
import os
import errno
from queue import Queue, Empty
from datetime import datetime

from Logic.settings import AGENT_LOG_DESTINATION, AGENT_LOG, AGENT_LOG_TO_FILE
from Logic.Logger import *


class Process():
    def __init__(self, fileName: str, timeout: float, timeout_behaviour: str, agentLogFilename: str = None):
        self.fileName = fileName
        self.agentLogFilename = agentLogFilename
        self.toBeKilled = False
        self.lock = Lock()
        self.errors = ''
        try:
            command = fileName
            useShell = False
            if fileName.split('.')[-1] == 'py':
                command = f'"{PYTHON_EXECUTABLE}" ' + command
                useShell = True
            elif fileName.split('.')[-1] == 'jar':
                command = 'java -jar ' + command
                useShell = True

            if AGENT_LOG:
                if AGENT_LOG_TO_FILE:
                    stderrStream = PIPE
                else:
                    stderrStream = None
            else:
                stderrStream = DEVNULL

            self.process = Popen(command, stdin=PIPE, stderr=stderrStream,
                                 stdout=PIPE, text=True, bufsize=1, shell=useShell)

        except Exception:
            raise Exception(
                f"Process failed to start properly. Executable: {command}.\tTimeout: {timeout}.")
        self.timeout = timeout
        self.timeout_behaviour = timeout_behaviour

        self.q = Queue()
        self.t = Thread(target=self.enqueue_output, args=(self.process.stderr, self.q))
        self.t.daemon = True  # thread dies with the program
        self.t.start()

    def timeout_function(self):
        self.lock.acquire()
        if self.timeout_behaviour == "kill":
            self.end_process()
        self.lock.release()

    def communicate(self, input):
        if self.toBeKilled or self.process.poll() is not None:  # If not terminated poll() returns 'None'
            raise Exception("Process is going to be killed.")
        self.process.stdin.write(input + '\n')  # Possible race
        timeout_timer = Timer(
            self.timeout, self.timeout_function)
        output = None
        try:
            timeout_timer.start()
            # self.read_stderr()
            output = self.process.stdout.readline()
            timeout_timer.cancel()
            self.lock.acquire()
            if self.toBeKilled:
                raise Exception('timeout')
            self.lock.release()
            return output
        except:
            raise Exception('timeout')

    @staticmethod
    def enqueue_output(out, queue):
        if out is None:
            return
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def read_stderr(self):
        # Read line without blocking
        while True:
            try:
                line = self.q.get(timeout=.01)
                self.errors += line
                if not line:
                    break
            except Empty:
                break

    def end_process(self):
        self.toBeKilled = True
        if self.agentLogFilename:
            self.read_stderr()

            p = os.path.join(AGENT_LOG_DESTINATION,
                             self.agentLogFilename + '_' + str(datetime.now().microsecond) + '.txt')
            try:
                if not os.path.exists(os.path.dirname(p)):
                    try:
                        os.makedirs(os.path.dirname(p))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            # self.process.kill()
                            raise Exception("Process killed...")
                with open(p, 'w') as f:
                    f.write(self.errors)
                    info(f"Agent log saved in: {p}")
            except Exception as e:
                warning("There was a problem saving the game error:\n" + str(e))
                # self.process.kill()
                raise Exception("Process killed...")
        self.process.kill()
