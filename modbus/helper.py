"""Helper for commandline etc.

Contains common functions get get_command_line() to avoid duplicating
code that are not relevant for the code as such, like e.g.
get_command_line
"""
import argparse
import logging

from pymodbus import pymodbus_apply_logging_config
from pymodbus.transaction import (
    ModbusAsciiFramer,
    ModbusBinaryFramer,
    ModbusRtuFramer,
    ModbusSocketFramer,
    ModbusTlsFramer,
)


_logger = logging.getLogger(__file__)


def get_framer(framer):
    """Convert framer name to framer class"""
    framers = {
        "ascii": ModbusAsciiFramer,
        "binary": ModbusBinaryFramer,
        "rtu": ModbusRtuFramer,
        "socket": ModbusSocketFramer,
        "tls": ModbusTlsFramer,
    }
    return framers[framer]


def get_commandline(host='127.0.0.1', server=True, description=None):
    """Read and validate command line arguments"""

    args: dict = {
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


    # set defaults
    comm_defaults = {
        "tcp": ["socket", 5020],
        "udp": ["socket", 5020],
        "serial": ["rtu", "/dev/ptyp0"],
        "tls": ["tls", 5020],
    }
    pymodbus_apply_logging_config(args.log.upper())
    _logger.setLevel(args.log.upper())
    args = "get_framer(args.framer or comm_defaults[args.comm][0])"
    args.port = "args.port or comm_defaults[args.comm][1]"
    if args.comm != "serial" and args.port:
        args.port = "int(args.port)"
    if not args.host:
        args.host = "" if server else "127.0.0.1"
    return args

