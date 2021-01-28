"""
Sending Script
Client that sends STDIN, over a simulated faulty network connection.
"""

import argparse
import logging
import util.wire
import project

PARSER = argparse.ArgumentParser(description="Client script for sending data "
                                             "over a faulty network "
                                             "connection.")
PARSER.add_argument("-p", "--port", type=int, default=9999,
                    help="The port to connect to the simulated network over.")
PARSER.add_argument("-f", "--file", required=True,
                    help="The file to send over the simulated network.")
PARSER.add_argument('-v', '--verbose', action="store_true",
                    help="Enable extra verbose mode.")
ARGS = PARSER.parse_args()

if ARGS.verbose:
    logging.getLogger('project-sender').setLevel(logging.DEBUG)

DATA = open(ARGS.file, 'rb').read()
SOC = util.wire.bad_socket(ARGS.port)

project.send(SOC, DATA)

SOC.close()
