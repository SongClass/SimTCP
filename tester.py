"""
Utility script for testing ptoject solutions under user set conditions.
"""
import time
import argparse
import subprocess
import hashlib
import pathlib
import sys
import os
import tempfile
import signal
import logging
import util.logging
import util.utils

DESC = sys.modules[globals()['__name__']].__doc__
PARSER = argparse.ArgumentParser(description=DESC)
PARSER.add_argument('-p', '--port', type=int, default=9999,
                    help="The port to simulate the lossy wire on (defaults to "
                         "9999).")
PARSER.add_argument('-l', '--loss', type=float, default=0.0,
                    help="The percentage of packets to drop.")
PARSER.add_argument('-d', '--delay', type=float, default=0.0,
                    help="The number of seconds, as a float, to wait before "
                         "forwarding a packet on.")
PARSER.add_argument('-b', '--buffer', type=int, default=2,
                    help="The size of the buffer to simulate (defaults to "
                         "2 packets).")
PARSER.add_argument('-f', '--file', required=True,
                    help="The file to send over the wire.")
PARSER.add_argument('-r', '--receive', default=None,
                    help="The path to write the received file to.  If not "
                         "provided, the results will be written to a temp "
                         "file.")
PARSER.add_argument('-s', '--summary', action="store_true",
                    help="Print a one line summary of whether the "
                         "transaction was successful, instead of a more "
                         "verbose description of the result.")
PARSER.add_argument('-v', '--verbose', action="store_true",
                    help="Enable extra verbose mode.")
ARGS = PARSER.parse_args()

LOGGER = util.logging.get_logger("project-tester")
if ARGS.verbose:
    LOGGER.setLevel(logging.DEBUG)

PYTHON_BINARY = sys.executable
SERVER_ARGS = [PYTHON_BINARY, "server.py"]

if ARGS.verbose:
    SERVER_ARGS.append("-v")

for AN_ARG in ("port", "loss", "delay", "buffer"):
    SERVER_ARGS.append("--" + AN_ARG)
    SERVER_ARGS.append(str(getattr(ARGS, AN_ARG)))

SERVER_PROCESS = None
RECEIVING_PROCESS = None

# Make sure we kill and cleanup the other processes if something goes wrong
# in the server, sender, or receiver.
def on_end(signal, frame):
    for a_process in (SERVER_PROCESS, RECEIVING_PROCESS):
        if a_process is None:
            continue
        try:
            a_process.kill()
        except:
            pass

for A_SIGNAL in (signal.SIGTERM, signal.SIGINT):
    signal.signal(A_SIGNAL, on_end)


SERVER_PROCESS = subprocess.Popen(SERVER_ARGS)
LOGGER.info("Starting wire process: {}".format(SERVER_PROCESS.pid))
time.sleep(1)

if ARGS.receive:
    DEST_FILE_PATH = ARGS.receive
else:
    TEMP_HANDLE, TEMP_FILE_NAME = tempfile.mkstemp()
    DEST_FILE_PATH = TEMP_FILE_NAME
    os.close(TEMP_HANDLE)

RECEIVING_ARGS = [PYTHON_BINARY, "receiver.py",
                  "--port", str(ARGS.port),
                  "--file", DEST_FILE_PATH]

if ARGS.verbose:
    RECEIVING_ARGS.append("-v")

RECEIVING_PROCESS = subprocess.Popen(RECEIVING_ARGS)
LOGGER.info("Starting receiving process: {}".format(RECEIVING_PROCESS.pid))
time.sleep(1)

SENDER_ARGS = [PYTHON_BINARY, "sender.py",
               "--port", str(ARGS.port),
               "--file", ARGS.file]

if ARGS.verbose:
    SENDER_ARGS.append("-v")

INPUT_PATH = pathlib.Path(ARGS.file)
INPUT_LEN, INPUT_HASH = util.utils.file_summary(INPUT_PATH)
START_TIME = time.time()

LOGGER.info("Starting sending process: {}".format(SERVER_PROCESS.pid))
SENDING_RESULT = subprocess.run(SENDER_ARGS)

END_TIME = time.time()

# Sleep the delay time, to allow the buffer to drain.
time.sleep(ARGS.delay)
RECEIVING_PROCESS.terminate()
RECEIVING_PROCESS = None
SERVER_PROCESS.terminate()
SERVER_PROCESS = None

RECV_PATH = pathlib.Path(DEST_FILE_PATH)
RECV_LEN, RECV_HASH = util.utils.file_summary(RECV_PATH)

IS_SUCCESS = RECV_HASH == INPUT_HASH
NUM_SECONDS = END_TIME - START_TIME
RATE = round(((RECV_LEN / NUM_SECONDS) / 1000), 2)
TEMPLATE = "[{}] latency={}ms, packet loss={}%, buffer={}, throughput={} Kb/s"
if ARGS.summary:
    SUMMARY = TEMPLATE.format(
        "SUCCESS" if IS_SUCCESS else "INCORRECT",
        round(ARGS.delay * 1000),
        round(ARGS.loss * 100, 2),
        ARGS.buffer,
        RATE
    )
    print(SUMMARY)
else:
    print("\n")
    print("Success" if IS_SUCCESS else "Incorrect")
    print("===\n")

    print("Input")
    print("---")
    print("File: {}\nLength: {}\nHash: {}".format(
        str(INPUT_PATH), INPUT_LEN, INPUT_HASH))

    print("\nReceived")
    print("---")
    print("File: {}\nLength: {}\nHash: {}".format(
        str(RECV_PATH), RECV_LEN, RECV_HASH))

    print("\nStats")
    print("---")
    print("Time: {} secs\nRate: {} kB/s".format(round(NUM_SECONDS, 2), RATE))
sys.exit(0 if IS_SUCCESS else 1)
