import c104
import random
import time


def on_step_command(point: c104.Point, previous_state: dict, message: c104.IncomingMessage) -> c104.ResponseState:
    """ handle incoming regulating step command
    """
    print(
        "{0} STEP COMMAND on IOA: {1}, new: {2}, prev: {3}, cot: {4}, quality: {5}".format(point.type, point.io_address,
                                                                                           point.value, previous_state,
                                                                                           message.cot, point.quality))

    if point.value == c104.Step.LOWER:
        # do something
        return c104.ResponseState.SUCCESS

    if point.value == c104.Step.HIGHER:
        # do something
        return c104.ResponseState.SUCCESS

    return c104.ResponseState.FAILURE


def before_transmit(point: c104.Point) -> None:
    """ update point value before transmission
    """
    point.value = random.random() * 100
    print("{0} BEFORE TRANSMIT on IOA: {1}".format(point.type, point.io_address))


def main():
    # server and station preparation
    server = c104.Server(ip="0.0.0.0", port=2404)
    station = server.add_station(common_address=47)

    # monitoring point preparation
    point = station.add_point(io_address=11, type=c104.Type.M_ME_NC_1, report_ms=15000)
    point.on_before_auto_transmit(callable=before_transmit)
    point.on_before_read(callable=before_transmit)

    # command point preparation
    command = station.add_point(io_address=12, type=c104.Type.C_RC_TA_1)

    # start
    server.start()

    while not server.has_active_connections:
        print("Waiting for connection")
        time.sleep(1)

    time.sleep(1)

    c = 0
    while server.has_open_connections and c < 30:
        c += 1
        print("Keep alive until disconnected")
        time.sleep(1)

    print(f"### POINT 12 VALUE IS: {command.value}")
    print("CONNECTION OVER!")
    print("CONNECTION OVER!")
    print("CONNECTION OVER!")


def start_server():
    c104.set_debug_mode(c104.Debug.Client | c104.Debug.Connection)
    print("### DEBUG MODE SET")
    main()
    time.sleep(1)
