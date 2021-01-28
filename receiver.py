"""
Receiving Script
Client that receives data over a simulated slow socket, and writes the results
to STDOUT.
"""

import argparse
import sys
import logging
import project.wire
import YourFunction

PARSER = argparse.ArgumentParser(description="Client script for sending data "
                                             "over a faulty network "
                                             "connection.")
PARSER.add_argument("-p", "--port", type=int, default=9999,
                    help="The port to connect to the simulated network over.")
PARSER.add_argument("-f", "--file", type=str,
                    help="The path to write the data recorded over the buffer "
                         "to (default=STDOUT).")
PARSER.add_argument('-v', '--verbose', action="store_true",
                    help="Enable extra verbose mode.")
ARGS = PARSER.parse_args()

if ARGS.verbose:
    logging.getLogger('YourFunction-receiver').setLevel(logging.DEBUG)

OUTPUT = open(ARGS.file, 'wb') if ARGS.file else sys.stdout.buffer

SOC = project.wire.bad_socket(ARGS.port)

YourFunction.recv(SOC, OUTPUT)

SOC.close()
OUTPUT.close()
