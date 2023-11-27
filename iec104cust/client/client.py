import c104
import time


def main(host104, registers):
    # client, connection and station preparation
    client = c104.Client(tick_rate_ms=1000, command_timeout_ms=1000)
    connection = client.add_connection(ip=host104, port=2404, init=c104.Init.INTERROGATION)
    station = connection.add_station(common_address=47)
    # start
    client.start()

    while not connection.is_connected:
        print("Waiting for connection to {0}:{1}".format(connection.ip, connection.port))
        time.sleep(1)

    for i in range(0, len(registers)):
        # C_SE_NB_1 - Setpoint command, scaled value. This type allows to set value of IOA in RTU.
        # Point number = Modbus register index + 32 (position offset in point numeration) + 1 (position to index).
        # Control direction - Client transmits to server.
        infopoint = station.add_point(io_address=i+32+1, type=c104.Type.C_SE_NB_1)
        infopoint.value = registers[i]
        if infopoint.transmit(cause=c104.Cot.ACTIVATION):
            print(f"Point {infopoint.io_address} -> SUCCESS")
        else:
            break

    time.sleep(3)
    print("exit")
    print("exit")
    print("exit")


def start_client(host104='127.0.0.1', registers=None):
    c104.set_debug_mode(c104.Debug.Client | c104.Debug.Connection)
    main(host104, registers)
    time.sleep(1)
