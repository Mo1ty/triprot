#!/usr/bin/env python3
"""Pymodbus asynchronous Server Example.

An example of a multi threaded asynchronous server.

usage::

    server_async.py [-h] [--comm {tcp,udp,serial,tls}]
                    [--framer {ascii,binary,rtu,socket,tls}]
                    [--log {critical,error,warning,info,debug}]
                    [--port PORT] [--store {sequential,sparse,factory,none}]
                    [--slaves SLAVES]

    -h, --help
        show this help message and exit
    -c, --comm {tcp,udp,serial,tls}
        set communication, default is tcp
    -f, --framer {ascii,binary,rtu,socket,tls}
        set framer, default depends on --comm
    -l, --log {critical,error,warning,info,debug}
        set log level, default is info
    -p, --port PORT
        set port
        set serial device baud rate
    --store {sequential,sparse,factory,none}
        set datastore type
    --slaves SLAVES
        set number of slaves to respond to

The corresponding client can be started as:

    python3 client_sync.py

"""
import logging

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer

from modbus.args.server_args import ServerArgs as Args

_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)


def setup_server(host=None, description=None):
    """Run server setup."""
    args = Args(host, description)
    print("### Create datastore")
    datablock = ModbusSequentialDataBlock(0x00, [17] * 100)
    context = ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock)
    single = True

    print("# Build data storage")
    args.context = ModbusServerContext(slaves=context, single=single)

    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server made for purposes of ICT2 test!",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    return args


def setup_server_args(host='127.0.0.1', description=''):
    server_args = {
        "comm": 'tcp',
        "framer": {
            "method": 'socket',
            "name": ''
        },
        "log": 'INFO',
        "port": 5020,
        "baudrate": 9600,
        "host": host,
        "store": 'sequential',
        "slaves": 0,
        "context": None,
        "description": description
    }
    return server_args


async def run_async_server(args):
    """Run server."""
    txt = f"### start ASYNC server, listening on {args.port} - {args.comm}"
    _logger.info(txt)
    address = (args.host if args.host else "", args.port if args.port else None)
    server = await StartAsyncTcpServer(
        context=args.context,  # Data storage
        identity=args.identity,  # server identify
        # TBD host=
        # TBD port=
        address=address,  # listen address
        # custom_functions=[],  # allow custom handling
        framer=args.framer,  # The framer strategy to use
        # ignore_missing_slaves=True,  # ignore request to a missing slave
        # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
        # timeout=1,  # waiting time for request to complete
        # TBD strict=True,  # use strict timing, t1.5 for Modbus RTU
    )

    return server


async def async_helper():
    """Combine setup and run."""
    _logger.info("Starting...")
    run_args = setup_server(description="Run asynchronous server on machine 1.")
    await run_async_server(run_args)
