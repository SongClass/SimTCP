"""
Implementation of an async based lossy wire, that simulates network
conditions between two communicating sockets.
"""
import asyncio
import random
import socket
import binascii
import hashlib
import struct
import util.logging


def data_rep(data: bytes) -> str:
    """Returns a plesant to print depiction of the given bytes, to make
    the logs / debugging easier to understand.
    """
    if len(data) <= 4:
        try:
            return struct.unpack("i", data)[0]
        except:
            return binascii.hexlify(data)

    sha1er = hashlib.sha1()
    sha1er.update(data)
    return sha1er.hexdigest()


class CrummyWireProtocol(asyncio.DatagramProtocol):

    def __init__(self, loop, loss: float, delay: float, buffer_size: int):
        self._loop = loop
        self._loss = loss
        self._delay = delay
        self._buffer_size = buffer_size
        self._wirebuffer = []
        self._peer_addrs = set()
        self._transport = None
        self._logger = util.logging.get_logger("project-wire")

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data, addr):
        self._logger.info(" --> Received %d bytes from %s - %s", len(data),
                          addr, data_rep(data))

        self._peer_addrs.add(addr)
        if data == b'connect':
            return

        # First, see if the buffer is full.  If it is, then just drop
        # the packet and pretend nothing happened.
        # Song: changed the following line to enable correct buffer size overflows
        # if len(self._wirebuffer) >= self._buffer_size:
        if len(self._wirebuffer) >= self._buffer_size:
            self._logger.debug(" !!-> Dropping, buffer is full: len(wirebuffer): %d >= buff_size: %d", len(self._wirebuffer), self._buffer_size)
            # print("drop due to buffer overflow")

            return

        # Second, see if we should drop the packet.  If so, then we just
        # discard it as if nothing ever happened.
        rand = random.random()
        # print("loss random:", rand, " threshold:", self._loss)
        if self._loss > 0 and rand < self._loss:
            self._logger.debug(" !-> Dropping to simulate a lossy connection: rand: %f < loss %f", rand, self._loss)
            # print("drop due to loss")
            return

        self._logger.debug(" --> Added %d bytes to send in %f seconds",
                           len(data), self._delay)

        # And now, schedule the data to actually be sent in the future.
        self._wirebuffer.append(data)
        self._loop.call_later(self._delay, self.send_to_peer_addrs, (data, addr))

    def send_to_peer_addrs(self, package):
        data, sender_addr = package

        if data not in self._wirebuffer:
            self._logger.error(" !!! Was scheduled to send data that is not "
                               "in the write buffer")
            return

        for a_peer_addr in self._peer_addrs:
            if a_peer_addr == sender_addr:
                continue
            self._logger.debug(" <-- Sending %d bytes to %s - %s", len(data),
                               a_peer_addr, data_rep(data))
            self._transport.sendto(data, addr=a_peer_addr)

        self._wirebuffer.remove(data)


def bad_socket(port: int) -> socket.socket:
    """Establishes a connection to the server, that simulates a crummy
    network, on the given port.

    Args:
        port -- the port to listen to the service simulating a lossy network.

    Return:
        socket instance, connected and ready to communicate on.
    """
    lossy_socket = socket.socket(type=socket.SOCK_DGRAM)
    lossy_socket.connect(('127.0.0.1', port))
    lossy_socket.send(b'connect')
    return lossy_socket


def create_server(port: int, loss: float, delay: float, buff_size: int) -> tuple:

    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        lambda: CrummyWireProtocol(loop, loss, delay, buff_size),
        local_addr=('127.0.0.1', port))
    transport, _ = loop.run_until_complete(listen)
    return transport, loop
