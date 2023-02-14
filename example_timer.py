"""
Where solution code to project should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import util
import util.logging
import threading


# Below is a program to show timer test alone through 'python3 project_timer.py'
# It is not needed for the project.
from threading import Timer
import time

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def dummyfn(msg="foo"):
    print(msg)

def main():
    timer = RepeatTimer(1, dummyfn)
    timer.start()
    time.sleep(5)
    timer.cancel()

if __name__ == '__main__':
    main()
