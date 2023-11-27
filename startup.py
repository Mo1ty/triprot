import modbus.client.async_client as async_client
import modbus.server.async_server as async_server
import asyncio
import time
import iec104cust.server.server as Server104
import iec104cust.client.client as Client104
import dnp3.client.dnp3_client as Dnp3Client
import dnp3.server.dnp3_server as Dnp3Outstation

async def initialize_application():

    print("What machine do you want to start?")
    result = input("Put your number (1 to 3) here: ")

    if result == "1":
        modbus_async_server = await async_server.async_helper()
    elif result == "2":
        host = input("Put your IP here: ")
        register_info: list = []
        modbus_async_client = async_client.setup_async_client(host)
        res = await async_client.run_async_client(modbus_async_client)
        if res is not None:
            print("### Information received successfully! ###")
            print(res.registers)
            register_info = res.registers

        modbus_async_client.close()
        print("### Modbus client closed. ###")
        print("### Sending application to sleep to establish next checkpoint! ###")
        time.sleep(2)

        print("Select your protocol:")
        print("1 - DNP3")
        print("2 - IEC104")
        result = input("Type here: ")
        if result == "1":
            dnp3_host = input("Put your dnp3 IP here: ")
            client = Dnp3Client.start_master(dnp3_host, register_info)
        elif result == "2":
            host104 = input("Put your c104 IP here: ")
            client = Client104.start_client(host104, register_info)
        else:
            print("No option with such value!")


    elif result == "3":
        print("Select your protocol:")
        print("1 - DNP3")
        print("2 - IEC104")
        result = input("Type here: ")
        if result == "1":
            server = Dnp3Outstation.start_outstation()
        elif result == "2":
            server = Server104.start_server()
        else:
            print("No option with such value!")

    else:
        print("No option with such value!")


async def startup_menu():
    print("Welcome to the TriProt application!")
    print("Choose one of possible options: ")
    for i in range(0, len(options)):
        print(f"{i+1}: {options[i]}")

    result = input("Put your number here: ")

    if result == "1":
        await initialize_application()
    elif result == "2":
        about()
    elif result == "3":
        return
    else:
        print("Error, no option with such value!")


options = ["Start app.", "How it works?", "Exit."]


def about():
    print("Welcome to the TriProt application!")
    print("After starting you app you have to choose, which VM you simulate:")
    print("- VM 1 simulates Modbus slave.")
    print("- VM 2 simulates Master gateway, connecting Modbus with dnp3/iec 104.")
    print("- VM 3 simulates dnp3/iec 104 client.")
    print("ATTENTION: You have to specify same protocol on VM 2 and VM 3 - they cannot autoconfigure protocol.")
    print("--------------------------------")
    print("VM 2 must be started after VM 1 and VM 3.")
    print("You will need to know VM 1 and VM 3 IP addresses to connect.")


if __name__ == "__main__":
    asyncio.run(startup_menu())
