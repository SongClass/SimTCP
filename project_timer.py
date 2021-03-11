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

from threading import Timer

packet = []
sock_g = []

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def resend():
    # global sock_g
    sock_g.send(packet)
    print("$$$ resend:", packet)

def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)
    logger = util.logging.get_logger("project-sender")
    chunk_size = util.MAX_PACKET
    pause = .1
    offsets = range(0, len(data), util.MAX_PACKET)

    global packet
    global sock_g
    sock_g = sock

    timer = RepeatTimer(0.2, resend) # repeat every 200 ms
    for chunk in [data[i:i + chunk_size] for i in offsets]:
        packet = chunk
        sock.send(packet)

        logger.info("Pausing for %f seconds", round(pause, 2))
        time.sleep(pause)
        if not timer.is_alive():
            logger.info("start timer resending ...")
            timer.start()
        # time.sleep(5)
    
    if timer.is_alive():
        timer.cancel()



def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.
    """
    logger = util.logging.get_logger("project-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0
    while True:
        data = sock.recv(util.MAX_PACKET)
        if not data:
            break
        logger.info("Received %d bytes", len(data))
        dest.write(data)
        num_bytes += len(data)
        dest.flush()
    return num_bytes


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
