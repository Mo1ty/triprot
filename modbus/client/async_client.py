#!/usr/bin/env python3
"""Pymodbus asynchronous client example.

usage::

    client_async.py [-h] [-c {tcp,udp,serial,tls}]
                    [-f {ascii,binary,rtu,socket,tls}]
                    [-l {critical,error,warning,info,debug}] [-p PORT]
                    [--baudrate BAUDRATE] [--host HOST]

    -h, --help
        show this help message and exit
    -c, -comm {tcp,udp,serial,tls}
        set communication, default is tcp
    -f, --framer {ascii,binary,rtu,socket,tls}
        set framer, default depends on --comm
    -l, --log {critical,error,warning,info,debug}
        set log level, default is info
    -p, --port PORT
        set port
    --baudrate BAUDRATE
        set serial device baud rate
    --host HOST
        set host, default is 127.0.0.1

The corresponding server must be started before e.g. as:
    python3 server_sync.py
"""
import asyncio
import logging

import helper

import pymodbus.client as ModbusClient
from pymodbus.exceptions import ModbusException


_logger = logging.getLogger(__file__)
_logger.setLevel("DEBUG")


def setup_async_client(description=None, cmdline=None):
    """Run client setup."""
    args = helper.get_commandline(
        server=False, description=description, cmdline=cmdline
    )
    _logger.info("### Create client object")
    client = ModbusClient.AsyncModbusTcpClient(
        args.host,
        port=args.port,  # on which port
        # Common optional parameters:
        framer=args.framer,
        timeout=args.timeout,
        retries=3,
        reconnect_delay=1,
        reconnect_delay_max=10,
        #   retry_on_empty=False,
        #   TCP setup parameters
        #   source_address=("localhost", 0),
    )
    return client


async def run_async_client(client):
    """Run sync client."""
    _logger.info("### Client starting")
    await client.connect()
    assert client.connected
    device_info = None
    try:
        device_info = client.read_device_information()
    except ModbusException as exc:
        _logger.info("### ERROR ###")
        _logger.info("### RECEIVING DEVICE INFORMATION FAILED! ###")
        _logger.info(exc.string)
    finally:
        _logger.info("### End of Program")
        return device_info



async def run_a_few_calls(client):
    """Test connection works."""
    try:
        rr = await client.read_coils(32, 1, slave=1)
        assert len(rr.bits) == 8
        rr = await client.read_holding_registers(4, 2, slave=1)
        assert rr.registers[0] == 17
        assert rr.registers[1] == 17
    except ModbusException:
        pass


