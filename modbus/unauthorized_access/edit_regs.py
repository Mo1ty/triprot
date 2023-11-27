from pymodbus.framer import ModbusSocketFramer
import pymodbus.client as ModbusClient
from pymodbus.exceptions import ModbusException
import asyncio


class ClientArgs:
    def __init__(self, host="127.0.0.1"):
        self.baudrate = 9600
        self.comm = 'tcp'
        self.framer = ModbusSocketFramer
        self.host = host
        self.log = 'INFO'
        self.port = 5020
        self.timeout = 10


async def main():

    host = input("Type IP: ")

    args = ClientArgs(host)
    print("### Create client object")
    client = ModbusClient.AsyncModbusTcpClient(
        args.host,
        port=args.port,
        framer=args.framer,
        timeout=args.timeout,
        retries=3,
        reconnect_delay=1,
        reconnect_delay_max=10,
    )

    await client.connect()
    assert client.connected
    try:
        await client.write_registers(address=0x10, values=13 * [40])
        request = await client.read_input_registers(address=0x00, count=96)
        print(request.registers)

    except ModbusException as exc:
        print("### ERROR ###")
        print("### RECEIVING DEVICE INFORMATION FAILED! ###")
        print(exc.string)
    finally:
        client.close(reconnect=False)
        print("### End of Program")


if __name__ == "__main__":
    asyncio.run(main())