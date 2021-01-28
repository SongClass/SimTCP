"""
Python code that simulates network connections by sitting between two
socket connections.
"""
import sys
import argparse
import logging
import util.wire
import util.logging

# Grab the dockblock of the current module, to avoid redundantly describing
# what this program does.
DESC = sys.modules[globals()['__name__']].__doc__
PARSER = argparse.ArgumentParser(description=DESC)
PARSER.add_argument('-p', '--port', type=int, default=9999,
                    help="The port this program should listen on (defaults to "
                         "9999).")
PARSER.add_argument('-l', '--loss', type=float, default=0.0,
                    help="The percentage of packets to drop.")
PARSER.add_argument('-d', '--delay', type=float, default=0.0,
                    help="The number of seconds, as a float, to wait before "
                         "forwarding a packet on.")
PARSER.add_argument('-b', '--buffer', type=int, default=100000,
                    help="The size of the buffer to simulate.")
PARSER.add_argument('-v', '--verbose', action="store_true",
                    help="Enable extra verbose mode.")
ARGS = PARSER.parse_args()

if ARGS.verbose:
    logging.getLogger('project-wire').setLevel(logging.DEBUG)

TRANSPORT, LOOP = util.wire.create_server(ARGS.port, ARGS.loss,
                                               ARGS.delay, ARGS.buffer)

try:
    LOOP.run_forever()
except KeyboardInterrupt:
    pass

TRANSPORT.close()
LOOP.close()
