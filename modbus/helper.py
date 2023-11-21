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


def get_commandline(host=None, server=False, description=None, extras=None, cmdline=None):
    """Read and validate command line arguments"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--comm",
        choices=["tcp", "udp", "serial", "tls"],
        help="set communication, default is tcp",
        dest="comm",
        default="tcp",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--framer",
        choices=["ascii", "binary", "rtu", "socket", "tls"],
        help="set framer, default depends on --comm",
        dest="framer",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--log",
        choices=["critical", "error", "warning", "info", "debug"],
        help="set log level, default is info",
        dest="log",
        default="info",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="set port",
        dest="port",
        type=str,
    )
    parser.add_argument(
        "--baudrate",
        help="set serial device baud rate",
        default=9600,
        type=int,
    )
    # parser.add_argument("--host", help="set host, default is 127.0.0.1", dest="host", default=host, type=str)
    parser = argparse.ArgumentParser(host=host)
    if server:
        parser.add_argument(
            "--store",
            choices=["sequential", "sparse", "factory", "none"],
            help="set type of datastore",
            default="sequential",
            type=str,
        )
        parser.add_argument(
            "--slaves",
            help="set number of slaves, default is 0 (any)",
            default=0,
            type=int,
            nargs="+",
        )
        parser.add_argument(
            "--context",
            help="ADVANCED USAGE: set datastore context object",
            default=None,
        )
    else:
        parser.add_argument(
            "--timeout",
            help="ADVANCED USAGE: set client timeout",
            default=10,
            type=float,
        )
    if extras:  # pragma no cover
        for extra in extras:
            parser.add_argument(extra[0], **extra[1])
    args = parser.parse_args(cmdline)

    # set defaults
    comm_defaults = {
        "tcp": ["socket", 5020],
        "udp": ["socket", 5020],
        "serial": ["rtu", "/dev/ptyp0"],
        "tls": ["tls", 5020],
    }
    pymodbus_apply_logging_config(args.log.upper())
    _logger.setLevel(args.log.upper())
    args.framer = get_framer(args.framer or comm_defaults[args.comm][0])
    args.port = args.port or comm_defaults[args.comm][1]
    if args.comm != "serial" and args.port:
        args.port = int(args.port)
    if not args.host:
        args.host = "" if server else "127.0.0.1"
    return args

