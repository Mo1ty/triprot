import c104
import random
import time
import numpy

def main(host104, registers):
    # client, connection and station preparation
    client = c104.Client(tick_rate_ms=1000, command_timeout_ms=1000)
    connection = client.add_connection(ip=host104, port=2404, init=c104.Init.INTERROGATION)
    station = connection.add_station(common_address=47)

    # monitoring point preparation
    point = station.add_point(io_address=11, type=c104.Type.M_ME_NC_1)

    # start
    client.start()

    while not connection.is_connected:
        print("Waiting for connection to {0}:{1}".format(connection.ip, connection.port))
        time.sleep(1)

    for i in range(0, len(registers)):
        infopoint = station.add_point(io_address=i+32+1, type=c104.Type.C_SE_NB_1)
        infopoint.value = registers[i]
        if infopoint.transmit(cause=c104.Cot.ACTIVATION):
            print(f"Point {infopoint.io_address} -> SUCCESS")
        else:
            break

    #time.sleep(3)

    print("read")
    print("read")
    print("read")
    if point.read():
        print("-> SUCCESS")
    else:
        print("-> FAILURE")

    #time.sleep(3)

    print("transmit")
    print("transmit")
    print("transmit")


    time.sleep(3)

    print("exit")
    print("exit")
    print("exit")




def start_client(host104='127.0.0.1', registers=None):
    c104.set_debug_mode(c104.Debug.Client | c104.Debug.Connection)
    main(host104, registers)
    time.sleep(1)
