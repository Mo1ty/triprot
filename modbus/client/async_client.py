#!/usr/bin/env python3
import time

import pymodbus.client as ModbusClient
from pymodbus.exceptions import ModbusException
from modbus.args.client_args import ClientArgs as Args

def setup_async_client(host=None):
    """Run client setup."""
    args = Args(host)
    print("### Create client object")
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
    print("### Client starting")
    await client.connect()
    assert client.connected
    try:
        request = await client.read_input_registers(address=0x00, count=96)
        while not request.registers:
            time.sleep(1)
        return request
    except ModbusException as exc:
        print("### ERROR ###")
        print("### RECEIVING DEVICE INFORMATION FAILED! ###")
        print(exc.string)
    finally:
        print("### End of Program")


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
