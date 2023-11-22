#!/usr/bin/env python3

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer

from modbus.args.server_args import ServerArgs as Args


def setup_server(host=None, description=None):
    """Run server setup."""
    args = Args(host, description)

    print("### Create datastore")
    datablock = ModbusSequentialDataBlock(0x00, [17] * 100)
    context = ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock)

    print("# Build data storage")
    args.context = ModbusServerContext(slaves=context, single=True)

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
    print(txt)
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
    print("Starting...")
    run_args = setup_server(description="Run asynchronous server on machine 1.")
    await run_async_server(run_args)
